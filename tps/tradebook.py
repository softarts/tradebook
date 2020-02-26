from tps import common, ohlc_file
import pandas as pd
import re

def get_symbol_ohlc(symbol_df,fdrname='IB1D'):
    ohlc_dct = {}
    for index, row in symbol_df.iterrows():
        symbol = row['symbol']
        ohlc = ohlc_file.OhlcFile.get_ohlc(row,fdrname)
        if ohlc.empty:
            print(symbol, "ohlc is empty")
            continue
        ohlc_dct[symbol] = ohlc
    return ohlc_dct


"""
[{'name': 'macd', 'param': {}}, {'name': 'nhnl', 'param': {'pct': '0.99'}}]   
"""
def load_algo_pipeline(jscfg):
    algo_inx_dct = {}
    for element in jscfg['algo']:
        algo_file = element['name']
        algo_param = element['param']
        if algo_file not in algo_inx_dct:
            mod = __import__('algo.'+algo_file, globals(), locals(), [algo_file])
            if hasattr(mod, 'algo_init'):
                algo_inx = mod.algo_init(algo_param)
                algo_inx_dct[algo_file] = algo_inx

    return algo_inx_dct


def run_algo(ohlc_dct,algo_dct):
    df_raw = {'symbol':[],'px':[]}

    for symbol,ohlc in ohlc_dct.items():
        print("processing",symbol)
        if ohlc.empty:
            print(symbol, "ohlc is empty")
            continue

        for an,algo_inx in algo_dct.items():
            ind_dct = algo_inx.run_algo(ohlc)            
            if ind_dct:
                for cn in ind_dct:
                    if cn not in df_raw:
                        df_raw[cn]=[]
                    lst = df_raw[cn]
                    lst.append(ind_dct[cn])
        
        df_raw['symbol'].append(symbol)
        df_raw['px'].append(ohlc['Close'].iloc[-1])
    df = pd.DataFrame.from_dict(df_raw, orient='columns', dtype=None)
    
    # post algo
    for an,algo_inx in algo_dct.items():
        df = algo_inx.post_algo(df, ohlc_dct)
    return df


# scan and pick columns
def run_scan(df,rule):
    if 'criteria' in rule:
        criteria = rule['criteria']
    else:
        criteria = []

    collst = []
    if not criteria:
        print("criteria is empty,...take the original table")
    else:
        # filter by dynamic criteria string
        crstr = ""
        pattern1 = "([a-zA-Z][A-Za-z0-9-_]*)"
        pattern2 = "[></]"

        for cr in criteria:
            print("processing cr", cr)
            if cr[0] == '@':  # TODO handle parameter
                continue
            collst = re.findall(pattern1, cr) # find all related columns
            ration = re.findall(pattern2, cr)
            if len(ration) != 0:
                cr0 = re.sub(pattern1, r"df['\1']", cr)  # put df[] surround pattern / substitute
                if crstr == "":  # first criteria
                    crstr = crstr + "(" + cr0 + ") "
                else:
                    crstr = crstr + "& (" + cr0 + ") "
        print("\tto evaluate criteria(logical) = %s" % crstr)
        if crstr != "":
            df = df[eval(crstr)]
        # ===========================================================
    #print(g_rule)
    if 'columns' in rule:
        output_cols = rule['columns']
        if not output_cols:
            output_cols.extend(df.columns.values)

        #print('===========================================',output_set)
        for col in collst:
            if col not in output_cols:  # keep origin order
                output_cols.append(col)
        df = df[output_cols]
    if 'sort' in rule:
        sort_list = rule['sort']
        if sort_list:
            sort_cols=[]
            asc_list=[]
            for dct in sort_list:
                for key,value in dct.items():
                    sort_cols.append(key)
                    asc_list.append(False if value=="False" else True)
            df.sort_values(by=sort_cols, inplace=True, ascending=asc_list)
            pass
    return df

import plotly.graph_objects as go
import pandas as pd

def plot(ohlc):
    fig = go.Figure(data=go.Ohlc(x=ohlc['Date'],
                    open=ohlc['Open'],
                    high=ohlc['High'],
                    low=ohlc['Low'],
                    close=ohlc['Close']))
    fig.show()