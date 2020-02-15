from . import tps_ind,common
from collections import OrderedDict

"""
columns:
perf1,2,3,...10,20,50,200]
"""

class AlgoPerf(common.AlgoBase):
    def __init__(self, param=None):
        self.param = param
        pass

    # main entry
    def run_algo(self,ohlc):
        #ohlc = ohlc_dct[symbol]
        ind_dct = OrderedDict()
        # calculate performance
        bars_list = [1, 2, 3, 4, 5, 7, 10, 15, 20, 30, 50, 100, 200]
        perf_list = tps_ind.CALC_PERF(ohlc, bars_list)

        for idx, p in enumerate(perf_list):
            ind_dct['perf' + str(bars_list[idx])] = p
        return ind_dct


def algo_init(param=None):
    return AlgoPerf(param)