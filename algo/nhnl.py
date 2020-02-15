from collections import OrderedDict
from . import tps_ind,common,tps_pattern

class AlgoNhNl(common.AlgoBase):
    def __init__(self, param=None):
        self.param = param
       # print("algo param is ",self.param)
        pass

    # main entry
    def run_algo(self,ohlc):
        #ohlc = tps_ind.NHNL(ohlc, **self.param)
        tps_ind.NHNL(ohlc, **self.param)
        ind_dct = OrderedDict([
            ('sth', ohlc['sth'].iloc[-1]),
            #('mth', ohlc['mth'].iloc[-1]),
            ('lth', ohlc['lth'].iloc[-1]),
            ('stl', ohlc['stl'].iloc[-1]),
            #('mtl', ohlc['mtl'].iloc[-1]),
            ('ltl', ohlc['ltl'].iloc[-1])
        ])

        tps_pattern.calc_sig_count(ohlc, ind_dct, ['lth_sig'], 20)
        tps_pattern.calc_sig_count(ohlc, ind_dct, ['sth_sig'], 20)
        tps_pattern.calc_sig_count(ohlc, ind_dct, ['stl_sig'], 20)
        tps_pattern.calc_sig_count(ohlc, ind_dct, ['ltl_sig'], 20)
        # def __calc_row(row):
        #     print(row['Close'],type(row),row.index)
        #     return 5
        #
        # ohlc_nhnl['pt'] = ohlc.apply(
        #     lambda row: __calc_row(row), axis=1
        # )

        # nhnl signal
        # nhnl signal
        #ohlc['nhl_sig'] = 0  # no signal

        #ohlc.loc[(ohlc['sth_sig'] == 1), 'nhl_sig'] = 1  # signal point
        #ohlc.loc[(ohlc['stl_sig'] == 1), 'nhl_sig'] = -1  # signal point
        #ohlc['nhlvol_sig'] = 0
        #ohlc.loc[(ohlc['snh'] == 1) & (ohlc['volra20'] >= 1.0), 'nhlvol_sig'] = 1
        #ohlc.loc[(ohlc['snl'] == 1) & (ohlc['volra20'] >= 1.0), 'nhlvol_sig'] = -1
        #ind_dct['stl'] = ohlc['stl'].iloc[-1]
        #ind_dct['sth'] = ohlc['sth'].iloc[-1]

        return ind_dct


def algo_init(param=None):
    return AlgoNhNl(param)
