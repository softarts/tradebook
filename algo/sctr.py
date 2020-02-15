"""
https://stockcharts.com/articles/canada/2013/11/sctr-scanning-for-strong-stocks-on-an-sctr-pull-back-chapter-9.html
https://stockcharts.com/articles/scanning/2011/12/scanning-scooters.html?st=sctr
"""
from . import tps_ind, common
from collections import OrderedDict
import pandas
import numpy as np


def calcChg(netchg, totchg):
    if totchg != 0:
        chgRatio = (netchg / totchg)
    else:
        chgRatio = 0
    return chgRatio


def calc_ppo(ohlc):
    # ema12 = pandas.ewma(ohlc['Close'], span=12)
    # ema26 = pandas.ewma(ohlc['Close'], span=26)

    ema12 = ohlc['Close'].ewm(adjust=True, min_periods=0, ignore_na=False, span=12).mean()
    ema26 = ohlc['Close'].ewm(adjust=True, min_periods=0, ignore_na=False, span=26).mean()

    # macd = ema12 - ema26
    ppo = (ema12 - ema26) / ema26 * 100;
    '''
    print "1 ==================="
    print ema12
    print "2 ==================="
    print ema26
    print "3 ==================="
    print ppo
    return 1.2

    # p2 = pandas.Series(pandas.rolling_mean(ppo,3).tolist())
    # p2 = pandas.rolling_mean(ppo,3).reset_index(0).drop('index',axis=1)
    '''
    p1 = tps_ind.WEIGHT_MOV_AVG(ppo, 3)
    # p2 = pandas.rolling_mean(ppo, 3)
    p2 = ppo.rolling(center=False, window=3).mean()
    ppolinear = 6 * (p1 - p2) / (3 - 1)
    ppodiff = ppolinear - ppolinear.shift(1)
    # netChgAvg = pandas.rolling_mean(ppodiff, 3)
    netChgAvg = ppodiff.rolling(center=False, window=3).mean()
    # totChgAvg = pandas.rolling_mean(abs(ppodiff), 3)
    totChgAvg = abs(ppodiff).rolling(center=False, window=3).mean()
    chgratio = pandas.Series(map(calcChg, netChgAvg, totChgAvg), index=ppo.index)
    shppo = 50 * (chgratio + 1) / 100
    return shppo



class AlgoSctr(common.AlgoBase):
    def __init__(self, param=None):
        self.param = param
        pass

    # main entry
    def run_algo(self, ohlc):
        ind_dct = OrderedDict()
        ohlc = tps_ind.RSI(ohlc, 14)
        ohlc = tps_ind.MA(ohlc, [50, 200])

        ma200 = ohlc['ma200']
        ma50 = ohlc['ma50']
        rsi = ohlc['rsi']

        lti200 = (ohlc['Close'] / ma200 - 1) * 100 * 0.3
        lti125 = (ohlc['Close'] / ohlc['Close'].shift(125) - 1) * 100 * 0.3
        # lt = lti200+lti125

        mti50 = (ohlc['Close'] / ma50 - 1) * 100 * 0.15
        mti20 = (ohlc['Close'] / ohlc['Close'].shift(20) - 1) * 100 * 0.15

        stirsi = rsi * 0.05
        stippo = calc_ppo(ohlc) * 0.05

        score = lti200 + lti125 + mti50 + mti20 + stirsi + stippo

        ohlc['sctr'] = score
        ohlc.fillna(0, inplace=True)
        # print(id(ohlc))
        # print 'sctr', symbol, score
        # print "\t",lti200,lti125,mti50,mti20,stirsi,stippo
        # self.ind['sctr'] = self.score[-1]

        '''
        hv = np.array(ohlc['High'])
        lv = np.array(ohlc['Low'])
        cv = np.array(ohlc['Close'])
        '''
        # kdj
        full_k, full_d = tps_ind.STOCHASTIC(ohlc, kperiod=5, dperiod=1, smoothing=3)
        #print(full_k)
        ind_dct['stok'] = round(full_k.iloc[-1], 3)
        ind_dct['sctr'] = round(ohlc['sctr'].iloc[-1], 3)   ## score[-1]
        #ind_dct['px'] = ohlc['Close'].iloc[-1]

        '''
        # calculate performance
        bars_list = [5, 10, 20, 50, 200]
        perf_list = tps_ind.CALC_PERF(ohlc, bars_list)

        for idx, p in enumerate(perf_list):
            ind_dct['perf' + str(bars_list[idx])] = p
        '''
        return ind_dct

    def post_algo(self, df, ohlc_dct):
        # need 1,2,3,4,5,6,7
        past_sctr_bars = [3, 5, 10, 15, 20, 25, 30]
        num_symbol = len(ohlc_dct)

        dfsctr = df.sort_values(by='sctr', ascending=False)
        rank = [round(100 - i*100/num_symbol, 2) for i in range(0, num_symbol)]
        dfsctr['sctr_rank'] = rank

        for sb in past_sctr_bars:
            col_past_rank = 'sctr_r%d' % sb
            dfsctr[col_past_rank] = 0
            dct = {}
            for symbol, ohlc in ohlc_dct.items():
                try:
                    dct[symbol] = round(ohlc['sctr'].iloc[-sb], 2)
                except Exception as e:
                    dct[symbol] = 0
                    print(symbol, "no enough sctr data")
                    #print(e)

            # sort dct
            count = 0
            dct_rank = {}
            # tp = sorted(dct.items(),key=itemgetter(1), reverse=True)
            # if value has 'nan' can't sort
            for key, value in sorted(dct.items(), key=lambda x: x[1], reverse=True):
                rank = 100 - round(count*100/num_symbol,2)
                dct_rank[key] = rank
                # print("%s: %s: %f" % (key, value, rank))
                count += 1
            # print("==================================")

            for index, row in dfsctr.iterrows():
                symbol = row['symbol']
                dfsctr.loc[index, col_past_rank] = dct_rank[symbol]

        #print(dfsctr)
        dfsctr.index = range(len(dfsctr.index))
        return dfsctr

def algo_init(param=None):
    return AlgoSctr(param)
