import os
from . import config
import pandas
from datetime import datetime

class OhlcFile(object):
    def __init__(self):
        self.reset()
        pass

    def reset(self):
        self.date_lst = []
        self.open_lst = []
        self.high_lst = []
        self.low_lst = []
        self.close_lst = []
        self.volume_lst = []

    def add_ohlc(self, d, open, high, low, close, vol):
        #20180627 -> 2018-06-27
        #d1 = datetime.strptime(d,"%Y%m%d")
        #self.date_lst.append(d1.strftime("%Y-%m-%d"))
        try:
            self.date_lst.append(d)
        except:
            self.date_lst.append(self.date_lst[-1])

        try:
            self.open_lst.append(open)
        except:
            self.open_lst.append(self.open_lst[-1])
        try:
            self.high_lst.append(high)
        except:
            self.high_lst.append(self.high_lst[-1])
        try:
            self.low_lst.append(low)
        except:
            self.low_lst.append(self.low_lst[-1])
        try:
            self.close_lst.append(close)
        except:
            self.close_lst.append(self.close_lst[-1])

        self.volume_lst.append(vol)
        #print(" Date:", d, "Open:", open, "High:", high, "Low:", low, "Close:", close, "Volume:", vol)
        pass

    def to_dataframe(self):
        date_lst = self.date_lst
        open_lst = self.open_lst
        high_lst = self.high_lst
        low_lst = self.low_lst
        close_lst = self.close_lst
        volume_lst = self.volume_lst

        '''date_lst.reverse()
        open_lst.reverse()
        high_lst.reverse()
        low_lst.reverse()
        close_lst.reverse()
        volume_lst.reverse()
        '''
        ohlc = pandas.DataFrame({'Date':date_lst,'Open': open_lst, 'High': high_lst, 'Low': low_lst,
                                 'Close': close_lst, 'Volume': volume_lst, 'Adj Close': close_lst},
                                columns=['Date','Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close'])
        #,index=date_lst
        #ohlc.index.name = 'Date'
        return ohlc
    
    def save_ohlc(self, symdct, feeder_name):
        symbol = "%s_%s" %(symdct['symbol'],symdct['sectype'])

        ohlc = self.to_dataframe()
        cache_path = config.CACHE_PATH
        # print cache_path
        filename = cache_path + symbol + "_ohlc_" + feeder_name + ".csv"
        try:
            os.remove(filename)  # delete file firstly
        except:
            print("unable to delete file %s",filename)
            pass
        ohlc.to_csv(filename, sep=',', index=False)
        print("save to", filename)

    @staticmethod
    def get_ohlc(symdct, feeder_name='IB1D', delta=0):
        symbol_fn = "%s_%s" %(symdct['symbol'], symdct['sectype'])
        filename = config.CACHE_PATH + symbol_fn + "_ohlc_" + feeder_name + ".csv"
        print("*** load ohlc from %s ***" % filename)
        try:
            #ohlc = pandas.read_csv(filename, index_col=['Date'])
            ohlc = pandas.read_csv(filename)
        except Exception as e:
            ohlc = pandas.DataFrame()
            print("error in reading %s,err=%s" % (filename,e))  # logging
        #ohlc.index = pandas.to_datetime(ohlc.index)
        if config.OHLC_SLICE!=0:
            ohlc=ohlc[:config.OHLC_SLICE]
        return ohlc
