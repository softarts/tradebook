import ib_core
import time,sys
from tps import common


class IbQuote(object):
    def __init__(self):
        self.app = ib_core.IBApp("127.0.0.1", 7496, 101)
        #self.app.set_callback(self.cb_quote, self.cb_end)
        self.app.set_cbdct({'tick_price':self.cb_quote,'tick_size':self.cb_size,'end':self.cb_end})
        self.total_quote = 0
        self.symset = set()
        self.ohlc_dct = {}


    def update_ohlc(self, symbol, px, size):
        if symbol not in self.ohlc_dct:
            self.ohlc_dct[symbol] = {'High':0,'Low':0,'Close':0,'Adj Close':0,'Open':0}

        ohlc = self.ohlc_dct[symbol]

        if px>0:
            ohlc['High'] = max(ohlc['High'], px)
            if ohlc['Low'] == 0:
                ohlc['Low'] = px
                ohlc['Open'] = px
            else:
                ohlc['Low'] = min(ohlc['Low'], px)
            ohlc['Adj Close'] = ohlc['Close'] = px

        if size>0:
            ohlc['Volume'] = size

    def cb_quote(self, symdct, px):
        symbol = symdct['symbol']
        self.update_ohlc(symbol, px, 0)
        self.symset.add(id(symdct))

    def cb_size(self, symdct, volume):
        symbol = symdct['symbol']
        self.update_ohlc(symbol, 0, volume)

    def cb_end(self, result):
        print("***___***___ignore___***___***", result)
        pass

    def ready(self):
        if len(self.symset) == self.total_quote:
            self.symset.clear()
            print("received all quote ------>")
            print(self.ohlc_dct)
            # TODO merge？
            return True
        return False
        pass

    #def cb_end(self, result=True):
    #    pass

    def get_quote(self, symdct):
        print('requesting %s' % symdct['symbol'])
        self.app.get_quote(symdct)
        pass

    def get_quote_batch(self, symbol_df):
        self.symset.clear()
        self.total_quote = len(symbol_df)
        for index, row in symbol_df.iterrows():
            symdct = common.symbol_row2dct(row)
            self.get_quote(symdct)
        pass

def quote():
    try:
        obj = IbQuote()
        symbol_df = common.load_symbol_csv('./symbol_ib.txt')
        obj.get_quote_batch(symbol_df)
        while True:
            print('sleeping 10 seconds')
            time.sleep(10)
        sys.exit(0)
    except Exception as e:
        print("some error", str(e))
    pass

if __name__ == '__main__':
    quote()