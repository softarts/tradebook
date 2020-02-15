"""
fasr cross slow, and keep nbar
"""
def cross_point(fast, slow, **kwargs):
    buy_nbar = 1
    sell_nbar = 1
    offset = 0
    signal_point = 1
    signal_empty = 0
    if 'buy_nbar' in kwargs:
        buy_nbar = kwargs['buy_nbar']
    if 'sell_nbar' in kwargs:
        sell_nbar = kwargs['sell_nbar']
    if 'offset' in kwargs:
        offset = kwargs['offset']
    if 'point' in kwargs:
        signal_point = kwargs['point']

    prev_fast = fast[0]
    prev_slow = slow[0]
    signal_lst = []
    buy_flag = False
    buy_count = 1
    sell_flag = False
    sell_count = 1

    for idx, curSlow in enumerate(slow):
        signal = signal_empty
        current_fast = fast[idx]
        if idx >= offset:
            if buy_flag:
                # second round check
                if current_fast > curSlow:
                    buy_count += 1
                    if buy_count == buy_nbar:
                        #buy_signal = signal_point
                        signal = signal_point

                        buy_flag = False
                        buy_count = 1
                else:
                    buy_flag = False
                    buy_count = 1
                pass
            else:
                if (prev_fast < prev_slow) and (current_fast > curSlow):
                    if buy_count == buy_nbar:
                        signal = signal_point
                        buy_flag = False
                        buy_count = 1
                    else:
                        buy_flag = True

            if sell_flag:
                if current_fast < curSlow:
                    sell_count += 1
                    if sell_count == sell_nbar:
                        signal = -signal_point
                        sell_count = 1
                        sell_flag = False
                else:
                    sell_count = 1
                    sell_flag = False
            else:
                if (prev_fast > prev_slow) and (current_fast < curSlow):
                    if sell_count == sell_nbar:
                        signal = -signal_point
                        sell_count = 1
                        sell_flag = False
                    else:
                        sell_flag = True

        prev_fast = current_fast
        prev_slow = curSlow
        signal_lst.append(signal)
    return signal_lst


#1 ,1 ,1 ,[1] ,0 ,0, 0  -> 4
def calc_sig_distance(ohlc, ind_dct, sig_list):
    for sig in sig_list:
        ind_dct[sig] = 0
        idx = len(ohlc) - 1
        while idx >= 0:
            if ind_dct[sig]==0:
                if ohlc[sig].iloc[idx] != 0:
                    ind_dct[sig] = int(ohlc[sig].iloc[idx] * (len(ohlc)-idx))
                    break
                pass
            else:
                break
            idx -=1
    return ind_dct

"""
0,0,0,1,1,1,0,0 -> count = 3 in the past 20 bars 
"""
def calc_sig_count(ohlc, ind_dct, sig_list, nbar=20):
    for sig in sig_list:
        ind_dct[sig] = ohlc[sig].iloc[-nbar:].sum()
    return ind_dct