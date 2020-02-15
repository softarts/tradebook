from ibapi.wrapper import EWrapper
from ibapi.client import EClient
from ibapi.ticktype import *
from ibapi.common import *
from ibapi.contract import Contract

from threading import Thread

import datetime

class IBApp(EWrapper, EClient):
    def __init__(self, ipaddress="127.0.0.1", portid=7496, clientid=1):
        EWrapper.__init__(self)
        EClient.__init__(self, wrapper=self)
        self.connect(ipaddress, portid, clientid)
        print("serverVersion:%s connectionTime:%s" % (self.serverVersion(),self.twsConnectionTime()))
        '''
        self.thread = Thread(target=self.run)
        self.thread.start()
        setattr(self, "_thread", self.thread)
        '''

        self.reqid = 1000
        self.reqid2symbol = {}
        self.sym2reqid = {}
        self.ready = False
        self.cbdct={}

    def set_cbdct(self, dct):
        self.cbdct = dct
        pass

    def start_run(self):
        print("client run()")
        try:
            self.run()
        except:
            raise
        #finally:
        #    self.dumpTestCoverageSituation()
        #    self.dumpReqAnsErrSituation()
        pass

    def nextValidId(self, orderId: int):
        super().nextValidId(orderId)
        print("setting nextValidOrderId: %d" % orderId)
        #self.nextValidOrderId = orderId
        self.ready = True
        self.cbdct['next_valid_id']()

    def get_contract(self, symdct):
        ibcontract = Contract()
        ibcontract.symbol = symdct['symbol'].upper()
        ibcontract.secType = symdct['sectype'].upper()
        ibcontract.exchange = symdct['exchange'].upper()
        ibcontract.currency = symdct['currency'].upper()
        ibcontract.primaryExchange = symdct['priexg'].upper()
        return ibcontract
    """
    market data
    """
    def tickPrice(self, reqId: TickerId, tickType: TickType, price: float, attrib: TickAttrib):
        #print("Tick Price. Ticker Id:", reqId, "tickType:", tickType, "Price:", price, "CanAutoExecute:", attrib.canAutoExecute, "PastLimit", attrib.pastLimit)
        super().tickPrice(reqId, tickType, price, attrib)
        if tickType == TickTypeEnum.LAST:
            symdct = self.reqid2symbol[reqId]
            self.cbdct['tick_price'](symdct, price)
        '''
        if tickType == 4:   #last
            if reqId in self._symbol_reqid_dct:
                symbol = self._symbol_reqid_dct[reqId]
                if not self.tick_cb:
                    self.tick_cb(symbol, price)
        '''
    def tickSize(self, reqId: TickerId, tickType: TickType, size: int):
        super().tickSize(reqId, tickType, size)
        #print("TickSize. TickerId:", reqId, "TickType:", tickType, "Size:", size)
        if tickType == TickTypeEnum.LAST:
            symdct = self.reqid2symbol[reqId]
            self.cbdct['tick_size'](symdct,size)


    def get_quote(self, symdct):
        contract = self.get_contract(symdct)
        self.reqid2symbol[self.reqid] = symdct
        self.reqMktData(self.reqid , contract, "", False, False, []) #
        self.reqid += 1

        # self._symbol_reqid_dct[self._reqid] = symbol
        # self._symbol_reqid_dct[symbol] = self._reqid
        #print('sending request')

    """
    realtime bar, no resp data when there is no trade?
    """
    # def realtimeBar(self, reqId: TickerId, time:int, open_: float, high: float, low: float, close: float,
    #                 volume: int, wap: float, count: int):
    #     super().realtimeBar(reqId, time, open_, high, low, close, volume, wap, count)
    #     print("RealTimeBar. TickerId:", reqId, RealTimeBar(time, -1, open_, high, low, close, volume, wap, count))
    #
    # def get_realtime(self,symdct):
    #     contract = self.get_contract(symdct)
    #     self.reqRealTimeBars(self._reqid, contract, 5, "MIDPOINT", True, [])
    #     self._reqid += 1

    """
    hisdata
    """
    def historicalData(self, reqId:int, bar:BarData):
        '''
        print("HistoricalData. ", reqId, " Date:", bar.date, "Open:", bar.open,
              "High:", bar.high, "Low:", bar.low, "Close:", bar.close, "Volume:", bar.volume,
              "Count:", bar.barCount, "WAP:", bar.average)
        '''
        symdct = self.reqid2symbol[reqId]
        self.cbdct['hist_data'](symdct, bar.date, bar.open, bar.high, bar.low, bar.close, bar.volume)

    def historicalDataEnd(self, reqId: int, start: str, end: str):
        super().historicalDataEnd(reqId, start, end)
        print("HistoricalDataEnd. ReqId:", reqId, "from", start, "to", end)
        symdct = self.reqid2symbol[reqId]
        self.cbdct['end'](symdct)
        #self.done = True


    def get_his(self, symdct, typ='IB1D'):
        contract = self.get_contract(symdct)
        #queryTime = (datetime.datetime.today() - datetime.timedelta(days=delta)).strftime("%Y%m%d %H:%M:%S")
        queryTime = datetime.datetime.today().strftime("%Y%m%d %H:%M:%S")
        # TODO move to common?
        if typ == 'IB1D':
            DURATION = "1 Y"
            BAR_SIZE = "1 day"
        elif typ == 'IB1D5Y':
            DURATION = "5 Y"
            BAR_SIZE = "1 day"
        elif typ == 'IB1H':
            DURATION = "3 M"
            BAR_SIZE = "1 hour"
        else:
            return False
        self.reqid2symbol[self.reqid] = symdct
        self.reqHistoricalData(self.reqid, contract, queryTime, DURATION, BAR_SIZE, "TRADES", 1, 1, False, [])
        self.reqid += 1
        return True

    def error(self, reqId:TickerId, errorCode:int, errorString:str):
        """This event is called when there is an error with the
        communication or when TWS wants to send a message to the client."""
        print("ERROR %s %s %s" %(reqId, errorCode, errorString))
        #self.cbdct['end'](False)
        if reqId in self.reqid2symbol:
            symdct = self.reqid2symbol[reqId]
            symbol = symdct['symbol']
        else:
            symbol='SYSTEM'
        self.cbdct['error'](symbol)

        #self.logAnswer(current_fn_name(), vars())
        #logger.error("ERROR %s %s %s", reqId, errorCode, errorString)

    #def shutdown(self):
    #    pass
        #self.done = True
        #self.thread.join()
        #super(IBApp, self).disconnect()
        # try:
        #     #self.disconnect()
        #     self.done=True
        # except:
        #     print('some error')

# def INIT_IB():
#     try:
#         app = FeederApp("127.0.0.1", 4001, 10)
#         # app.connect("127.0.0.1", 4001, 10)
#         print("serverVersion:%s connectionTime:%s" % (app.serverVersion(),
#                                                       app.twsConnectionTime()))
#         return app
#
#     except:
#         raise
#
#
#     pass

'''
def tickcb(symbol, px):
    print("%s:%f",symbol, px)

if __name__ == '__main__':
    app = IBApp("127.0.0.1", 7496, 10)
    app.set_tick_cb(tickcb)
    app.get_quote('AAPL')

    app.wait()
    print('exit....')
    pass
    symbol,sectype,exchange
ES,CONTFUT,GLOBEX
'''

