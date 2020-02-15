"""
DMI & RSI
"""
from collections import OrderedDict
from . import tps_ind, common, tps_pattern
#import numpy as np



class AlgoDmiRsi(common.AlgoBase):
    def __init__(self, param=None):
        pass

    def run_algo(self, ohlc):
        # DMI and buy, sell signal
        ind_dct = OrderedDict()
        ohlc = tps_ind.DMI2(ohlc)
        ohlc['rsi'] = tps_ind.RSI(ohlc, 14)
        #print(ohlc)

        sig_lst = tps_pattern.cross_point(ohlc['di+'], ohlc['di-'])
        ohlc['dmi_sig'] = sig_lst
        #ohlc = tps_ind.RSI(ohlc, 14)
        ind_dct['rsi'] = round(ohlc['rsi'].iloc[-1], 4)
        tps_pattern.calc_sig_distance(ohlc, ind_dct, ['dmi_sig'])
        return ind_dct


def algo_init(param=None):
    return AlgoDmiRsi(param)

