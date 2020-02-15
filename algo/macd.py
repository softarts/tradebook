"""

"""
from collections import OrderedDict
from . import tps_ind, common, tps_pattern
import numpy as np
import math
#from scipy import stats

class AlgoMacd(common.AlgoBase):
    def __init__(self, param=None):
        pass

    def run_algo(self, ohlc):
        diff = tps_ind.MACD(ohlc)
        ind_dct = OrderedDict()
        ind_dct['macd'] = round(diff[-1],3)

        ma_lst = [10, 20, 50, 200]
        #ohlc = tps_ind.MA(ohlc, ma_lst)
        tps_ind.MA(ohlc, ma_lst)

        px = ohlc['Close'].iloc[-1]

        # MA
        for l in ma_lst:
            col_ma = 'ma%d' % l
            siglst = tps_pattern.cross_point(ohlc['Close'], ohlc[col_ma], buy_nbar=1)
            ohlc[col_ma + '_sig'] = siglst
            ind_dct[col_ma+'%'] = round(px / ohlc[col_ma].iloc[-1] - 1, 3)*100
            ind_dct[col_ma] = round(ohlc[col_ma].iloc[-1], 4)

        # volume
        #ohlc = tps_ind.VOLMA(ohlc, 20)
        tps_ind.VOLMA(ohlc, 20)
        ohlc['vol20_sig'] = ohlc.apply(lambda row: 1 if row['volra20']>=1.1 else 0, axis=1)
        ind_dct['volra20'] = round(ohlc['volra20'].iloc[-1], 4)
        tps_pattern.calc_sig_distance(ohlc, ind_dct, ['ma10_sig', 'ma20_sig', 'ma50_sig', 'vol20_sig'])

        #slope
        SLOPE_LEN = 5

        """
        使用pct不太合理，涨幅收敛这个太激进 
        """
        for l in ma_lst:
            col_ma = 'ma%d' % l
            #y = ohlc[col_ma].pct_change().iloc[-SLOPE_LEN:]
            y = ohlc[col_ma].iloc[-SLOPE_LEN:]
            x = range(0,SLOPE_LEN)
            slopes = np.polyfit(x,y,1)
            #h = math.atan(slopes[0])
            #a = math.degrees(h)
            ind_dct['slo%d' % l] = round(slopes[0]*100/ind_dct[col_ma],3)
            #print(slopes,x,y)


        '''
        for l in ma_lst:
            col_ma = 'ma%d' % l
            slope, intercept, r_value, p_value, std_err = stats.linregress(ohlc.index[-SLOPE_LEN:],ohlc[col_ma][-SLOPE_LEN:])
            ind_dct[col_ma+'_slo'] = slope
        '''

        #print('exit macd=',id(ohlc))
        #print(ohlc)
        return ind_dct


def algo_init(param=None):
    return AlgoMacd(param)

