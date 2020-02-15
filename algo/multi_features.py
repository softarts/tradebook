"""

"""
from collections import OrderedDict
from . import tps_ind, common, tps_pattern
import numpy as np


class MultiFeature(common.AlgoBase):
    def __init__(self, param=None):
        pass

    def run_algo(self, ohlc):
        ind_dct = OrderedDict()
        ohlc['hlpct'] = (ohlc['High'] - ohlc['Low']) / ohlc['Close'] * 100.0
        ohlc['ocpct'] = (ohlc['Close'] - ohlc['Open']) / ohlc['Open'] * 100.0
        ohlc['pct'] = (ohlc['Close'] / ohlc['Close'].shift() - 1) * 100.0
        ohlc['rsi'] = tps_ind.RSI(ohlc, 14)

        #ohlc['Close'].shift(-30)
        # ohlc['mlp30'] = round(ohlc['Close'].shift(-30) / ohlc['Close'] *100-100, 2)
        # ohlc['Close30'] = ohlc['Close'].shift(-30)
        #ohlc['mlp30'] = ohlc.apply(lambda row: 1 if (row['Close30'] / row['Close'] *100 > 100) else 0, axis=1)
        return ind_dct


def algo_init(param=None):
    return MultiFeature(param)

