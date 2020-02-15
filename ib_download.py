"""
https://interactivebrokers.github.io/tws-api/historical_bars.html#hd_request
"""
import ib_core
import time,sys
from tps import ohlc_file, common, config

"""
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('-d', '--feeder', type=str, default='', help="feeder name")
args = parser.parse_args()
"""

from pathlib import Path

class IbDownload(object):
    def __init__(self, symbol_df, typ='IB1D'):

        Path("./cache").mkdir(parents=True, exist_ok=True)
        self.app = ib_core.IBApp("127.0.0.1", 7496, 101)
        self.symbol_df = symbol_df
        #self.app.set_callback(self.cb_histdata,self.cb_end)
        self.app.set_cbdct(
            {
                'hist_data': self.cb_histdata,
                'end': self.cb_end,
                'next_valid_id': self.cb_run,
                'error': self.cb_error
             }
        )
        self.ohf_dct = {}
        #self.ohlc_file = ohlc_file.OhlcFile()
        #self.symdct = {}
        self.done_set = set()
        self.typ = typ

        '''
        while (not self.app.ready):
            time.sleep(1)
            print('waiting for app ready')
        '''
        pass

    def cb_run(self):
        for index, row in self.symbol_df.iterrows():
            symdct = common.symbol_row2dct(row)
            self.get_hist(symdct)
        #exit?
        #self.app.disconnect()
        pass

    def run(self):
        self.app.start_run()

    #def shutdown(self):
    #    self.app.shutdown()

    '''
    def wait(self):
        while not self.done:
            print("waiting...")
            time.sleep(2)
    '''

    def cb_histdata(self, symdct, d, open, high, low, close, vol):
        ohf = self.ohf_dct[id(symdct)]
        ohf.add_ohlc(d, open, high, low, close, vol)
        # print(" Date:", d, "Open:", open, "High:", high, "Low:", low, "Close:", close, "Volume:", vol)
        pass

    def cb_end(self, symdct):
        ohf = self.ohf_dct[id(symdct)]
        ohf.save_ohlc(symdct, self.typ)
        self.done_set.add(id(symdct))
        if len(self.done_set) == len(self.symbol_df):
            print('%s download is done' % self.typ)
            print("=========================================")
            #self.app.reset()
            #sys.exit(0)
            #os._exit(0)
            self.app.disconnect()
            pass

        '''
        symbol = self.symdct['symbol'] if 'symbol' in self.symdct else '###'
        if result:
            self.ohlc_file.save_ohlc(self.symdct, self.typ)
        else:
            print("***___***___ignore___***___***", symbol)
        self.done = True
        '''
        pass

    def cb_error(self, symbol):
        print("***___***___error___***___***", symbol)
        pass

    def get_hist(self, symdct):
        self.done = False
        self.ohf_dct[id(symdct)] = ohlc_file.OhlcFile()
        print('requesting %s' % symdct['symbol'])
        self.app.get_his(symdct, self.typ)


def download(fdrname='IB1D', fn='./symbol_ib.txt'):
    #fdrname = args.feeder.upper()
    symbol_df = common.load_symbol_csv(fn)
    fdr_list = fdrname.split(',')
    """
    if fdrname:
        fdr_list = ["IB1D"]
    else:
        fdr_list = ["IB1D","IB1H","IB1D5Y"]
    """
    for fdr in fdr_list:
        obj = IbDownload(symbol_df, fdr)
        obj.run()

    '''
    try:
        
        symbol_df = common.load_symbol_csv('./symbol_ib.txt')
        for index, row in symbol_df.iterrows():
            symdct = common.symbol_row2dct(row)
            obj.get_hist(symdct)       
        
        # for symbol in symbol_list:
        #     print('retrieving %s' % symbol)
        #     obj.get_hist(symbol)
        #     #time.sleep(2)
        #     #obj.wait()
        sys.exit(0)
    except Exception as e:
        print("some error",str(e))
    pass
    '''



#if __name__ == '__main__':
#    download()

'''
BX,PRU,GS,COF,NYSE:BAC:BAC,CG,WFC,MS,AIG,JPM,TRV,BLK,AXP,V,MA,C,SQ,STI,BMO,UBS,DB,RBS,
NFLX,AAPL,AMZN,GOOGL,FB,TWTR,ADBE,TSLA,MSFT,EXPE,PCLN,EBAY,SNAP,
GRMN,AABA,FEYE,P,ATVI,WDAY,DATA,
GSK,PFE,AZN,JNJ,ABBV,UNH,NVS,BMY,SNY,ABT,LLY,MRK,
ILMN,CVS,HUM,ZTS,HCA,CI,ESRX,
GILD,BIIB,CELG,KITE,ALXN,REGN,BMRN,VRX,VRTX,BLUE,AMGN,IBB,AGN,JAZZ,ISRG,JUNO,RARE,MYL,EXEL,INCY,BIVV,
NTES,JD,YY,BABA,BIDU,VIPS,SOHU,WB,CYOU,CTRP,ASHR,MOMO,EDU,SINA,
IBM,ACN,SAP,ORCL,CSCO,ERIC,NOK,VIAV,RHT,VMW,A,MSI,CRM,HPE,
TXN,INTC,BBRY,QCOM,AMD,GPRO,AVGO,MU,NVDA,MRVL,SWKS,
SPY,QQQ,XLP,XBI,XLU,XLE,TLT,XLF,
NOC,BA,RTN,NYSE:LMT:LMT,GD,
PG,GIS,KMB,PM,HD,CL,CLX,
CMG,MCD,PEP,KHC,KO,YUM,SBUX,MDLZ,
MMM,CAT,UTX,GE,MON,HON,ARNC,MOS,DE,X,NUE,
COST,NKE,KR,WMT,COH,UAA,TIF,TGT,KSS,M,FL,JWN,
XOM,CVX,COP,FSLR,JNUG,NUGT,BP,PSX,SLB,VALE,
VZ,T,VIAB,TMUS,
MAR,
FOXA,DIS,
F,GM,TM,
WYNN,MLCO,
LUV,UAL,DAL'''