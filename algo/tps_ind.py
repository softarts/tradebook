import numpy as np
import pandas as pd
import talib
#generate temporary list
def WEIGHT_MOV_AVG(lst, period):
    data = []
    for index in range(0,len(lst)):
        if index < (period-1):
            #print index,"add nan"
            data.append(float('nan'))
        else:
            d = np.average(lst[index+1-period:index+1], weights=range(period,0,-1))
            data.append(d)
            #print index,"add",d
    return pd.Series(data, index=lst.index)


'''
def MA(ohlc, len_lst):
    for l in len_lst:
        col = "ma%d" % l
        ohlc[col] = ohlc['Close'].rolling(center=False, window=l).mean()
    return ohlc
'''
def MA(ohlc, len_lst):
    for window in len_lst:
        col = "ma%d" % window
        ohlc[col] = talib.EMA(ohlc['Close'].values, timeperiod = window)
    return ohlc

def RSI(ohlc, RSI_LEN):
    prices = ohlc['Close']
    deltas = np.diff(prices)
    seed = deltas[:RSI_LEN + 1]
    up = seed[seed >= 0].sum() / RSI_LEN
    down = -seed[seed < 0].sum() / RSI_LEN
    rs = up / down

    rsi = np.zeros_like(prices)
    rsi[:RSI_LEN] = 100. - 100. / (1. + rs)

    for i in range(RSI_LEN, len(prices)):
        delta = deltas[i - 1]  # cause the diff is 1 shorter

        if delta > 0:
            up_val = delta
            down_val = 0.
        else:
            up_val = 0.
            down_val = -delta

        up = (up * (RSI_LEN - 1) + up_val) / RSI_LEN
        down = (down * (RSI_LEN - 1) + down_val) / RSI_LEN

        rs = up / down
        rsi[i] = 100. - 100. / (1. + rs)
    return rsi
    #ohlc['rsi'] = rsi
    #return ohlc

def STOCHASTIC(ohlc, kperiod=5, dperiod=1, smoothing=3):
    # low_min = pd.rolling_min(lowp, kperiod)
    # high_max = pd.rolling_max(highp, kperiod)
    low_min = ohlc['Low'].rolling(min_periods=1, window=kperiod, center=False).min()
    high_max = ohlc['High'].rolling(min_periods=1, window=kperiod, center=False).max()

    fast_k = 100 * (ohlc['Close'] - low_min) / (high_max - low_min)

    # full_k = pd.stats.moments.rolling_mean(fast_k, smoothing)
    # full_d = pd.stats.moments.rolling_mean(full_k, dperiod)

    full_k = fast_k.rolling(center=False, window=smoothing).mean()
    full_d = full_k.rolling(center=False, window=dperiod).mean()
    return full_k, full_d

"""
计算周期回报
"""
def CALC_PERF(ohlc, bars_lst):

    px = ohlc['Close']
    result = []
    ohlc_len = len(px)
    for bar_num in bars_lst:
        if ohlc_len > bar_num:
            result.append(round((px.iloc[-1] / px.iloc[-1 - bar_num] - 1) * 100, 2))
        else:
            result.append(round((px.iloc[-1] / px.iloc[0] - 1) * 100, 2))
    return result


def MACD(ohlc):
    value, avg, diff = talib.MACD(ohlc['Close'].values, fastperiod=12, slowperiod=26, signalperiod=9)
    #print(macd,signal,diff)  #hist
    return diff


# new high and new low
def NHNL(ohlc, **kwargs):
    SHORTTERN_WINDOW = 20
    MIDTERM_WINDOW = 100
    LONGTERM_WINDOW = 200
    OFF_SNH_PCT = 1.0

    if 'stw' in kwargs:
        SHORTTERN_WINDOW = kwargs['stw']

    if 'mtw' in kwargs:
        MIDTERM_WINDOW = kwargs['mtw']

    if 'ltw' in kwargs:
        LONGTERM_WINDOW = kwargs['ltw']

    if 'pct' in kwargs:
        OFF_SNH_PCT = float(kwargs['pct'])

    #print('using NHNL_OFF_PCT=',OFF_SNH_PCT)

    sthigh = ohlc['High'].rolling(min_periods=1, window=SHORTTERN_WINDOW, center=False).max()
    #mthigh = ohlc['High'].rolling(min_periods=1, window=MIDTERM_WINDOW, center=False).max()
    lthigh = ohlc['High'].rolling(min_periods=1, window=LONGTERM_WINDOW, center=False).max()

    ohlc['sth'] = round(sthigh.shift(1),2)
    #ohlc['mth'] = round(mthigh.shift(1),2)
    ohlc['lth'] = round(lthigh.shift(1),2)

    stlow = ohlc['Low'].rolling(min_periods=1, window=SHORTTERN_WINDOW, center=False).min()
    #mtlow = ohlc['Low'].rolling(min_periods=1, window=MIDTERM_WINDOW, center=False).min()
    ltlow = ohlc['Low'].rolling(min_periods=1, window=LONGTERM_WINDOW, center=False).min()

    ohlc['stl'] = round(stlow, 2)
    #ohlc['mtl'] = round(mtlow, 2)
    ohlc['ltl'] = round(ltlow.shift(1), 2)

    ohlc['sth_sig'] = ohlc.apply(lambda row: 1 if row['Close'] >= row['sth']*OFF_SNH_PCT else 0, axis=1)
    ohlc['stl_sig'] = ohlc.apply(lambda row: 1 if row['Close'] <= row['stl']*OFF_SNH_PCT else 0, axis=1)
    ohlc['lth_sig'] = ohlc.apply(lambda row: 1 if row['Close'] >= row['lth']*OFF_SNH_PCT else 0, axis=1)
    ohlc['ltl_sig'] = ohlc.apply(lambda row: 1 if row['Close'] <= row['ltl']*OFF_SNH_PCT else 0, axis=1)

    #ohlc['offsnh'] = ohlc.apply(
    #    lambda row: 1 if row['snh'] == 1 and row['Close'] < row['High'] * OFF_SNH_PCT else 0, axis=1)

    return ohlc

# TODO check the accuracy
def DMI2(df, **kwargs):
    n = 14
    n_ADX = 14
    i = 0
    UpI = [float('nan')]
    DoI = [float('nan')]

    dfsize = len(df.index)
    #while i + 1 <= df.index[-1]:
    while i + 1 < dfsize:
        next_high = df['High'].iloc[i+1]
        this_high = df['High'].iloc[i]
        next_low = df['Low'].iloc[i + 1]
        this_low = df['Low'].iloc[i]
        UpMove = next_high - this_high
        DoMove = this_low - next_low

        if UpMove > DoMove and UpMove > 0:
            UpD = UpMove
        else:
            UpD = 0
        UpI.append(UpD)
        if DoMove > UpMove and DoMove > 0:
            DoD = DoMove
        else:
            DoD = 0
        DoI.append(DoD)
        i += 1
    i = 0
    TR_l = [0]
    #while i < df.index[-1]:
    while i < dfsize-1:
        TR = max(df['High'].iloc[i+1], df['Close'].iloc[i]) - min(df['Low'].iloc[i+1], df['Close'].iloc[i])
        # TR = max(df.get_value(i + 1, 'High'), df.get_value(i, 'Close')) - min(df.get_value(i + 1, 'Low'), df.get_value(i, 'Close'))
        TR_l.append(TR)
        i = i + 1
    TR_s = pd.Series(TR_l).shift(1)
    # ATR = pd.Series(pd.ewma(TR_s, span=n, min_periods=n))
    ATR = TR_s.ewm(span=n, ignore_na=False, min_periods=n, adjust=True).mean()


    #print(ATR)

    UpI = pd.Series(UpI)
    DoI = pd.Series(DoI)

    #PosDI = pd.Series(pd.ewma(UpI, span=n, min_periods=n - 1) / ATR)
    #NegDI = pd.Series(pd.ewma(DoI, span=n, min_periods=n - 1) / ATR)
    PosDI = UpI.ewm(span=n, ignore_na=False, min_periods=n - 1, adjust=True).mean() / ATR
    NegDI = DoI.ewm(span=n, ignore_na=False, min_periods=n - 1, adjust=True).mean() / ATR

    #ADX = pd.Series(pd.ewma(100* abs(PosDI - NegDI) / (PosDI + NegDI), span=n_ADX, min_periods=n_ADX - 1), name='ADX_' + str(n) + '_' + str(n_ADX))

    ADX = (100 * abs(PosDI - NegDI) / (PosDI + NegDI)) \
        .ewm(span=n_ADX, ignore_na=False, min_periods=n_ADX - 1, adjust=True).mean()

    df['adx'] = ADX.tolist()
    df['di+'] = PosDI.tolist()
    df['di-'] = NegDI.tolist()
    '''
    buysg, sellsg = pattern.cross(df['di+'], df['di-'], **kwargs)
    df['dmibuy'] = buysg
    df['dmisell'] = sellsg
    '''
    return df

def VOLMA(ohlc, length):
    col_vr = 'volra%d' % length
    smooth = 3
    volmara = ohlc['Volume'] / ohlc['Volume'].rolling(center=False, window=length).mean()
    volmaramean = volmara.rolling(center=False, window=smooth).mean()
    ohlc[col_vr] = volmaramean.round(4)
    return ohlc