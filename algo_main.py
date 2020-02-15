from tps import common, ohlc_file
import os, sys, re, time
import pandas
import datetime
#from collections import OrderedDict
from ib_quote import IbQuote
from tabulate import tabulate
import matplotlib.pyplot as plt


algo_inx_dct = {}
g_ohlc_dct = {}
g_rule={}
g_symbol_df=pandas.DataFrame()
g_algo_list=[]
g_fdr_name = ''
class AlgoInfo:
    def __init__(self, filename, param, _feeder):
        self.name = filename
        self.param = param
        self.file = filename
        self.fdr = FeederInfo(_feeder)
        pass


class FeederInfo:
    def __init__(self, name):
        self.name = name
        self.start_time = None
        self.end_time = None
        pass


def __get_algo_instance(algo_info):
    algo_file = algo_info.file
    algo_param = algo_info.param
    if algo_file not in algo_inx_dct:
        mod = __import__('algo.'+algo_file, globals(), locals(), [algo_file])
        if hasattr(mod, 'algo_init'):
            algo_inx = mod.algo_init(algo_param)
            algo_inx_dct[algo_file] = algo_inx
            return algo_inx
    return algo_inx_dct[algo_file]


def __init_algo_inx(algo_list):
    """
    init each algo module once
    """
    for agIn in algo_list:
        agIn.inx = __get_algo_instance(agIn)


def __print_df(df):
    print(tabulate(df, tablefmt="pipe", headers="keys",showindex=False))
    print('========================================================')
    print('= total', len(df), 'selected')
    print('========================================================')
    print(df)




# ========================================================
def __strategy_init_ohlc():
    __init_algo_inx(g_algo_list)
    df = g_symbol_df

    # use the first algo's feeder
    #fdr = g_algo_list[0].fdr

    #fdrname = get_feeder_name()

    for index, row in df.iterrows():
        symbol = row['symbol']
        if symbol not in g_ohlc_dct:
            ohlc = ohlc_file.OhlcFile.get_ohlc(row, g_fdr_name)
            g_ohlc_dct[symbol] = ohlc
            if ohlc.empty:
                print(symbol, "ohlc is empty")
                continue
            #print(ohlc)

    #print(g_ohlc_dct)
    pass



def __strategy_run_algo(df):
    last_date = ''
    for algo_info in g_algo_list:
        fdr = algo_info.fdr
        algo_name = algo_info.name
        algo_file = algo_info.file
        algo_inx = algo_info.inx
        algo_param = algo_info.param
        #ohlc_dct = algo_info.ohlc_dct
        print("run algo:", algo_name, ",feeder:", fdr.name, ",param:", algo_param)
        for index, row in df.iterrows():
            symbol = row['symbol']
            ohlc = g_ohlc_dct[symbol]
            if ohlc.empty:
                print(symbol, "ohlc is empty")
                continue
            print("processing", symbol)

            #print(ohlc)
            #ind_dct = algo_inx.run_algo(g_ohlc_dct[symbol])
            ind_dct = algo_inx.run_algo(ohlc)
            # add px
            ind_dct['px'] = ohlc['Close'].iloc[-1]
            if ind_dct:
                for cn in ind_dct:
                    df.loc[index, cn] = ind_dct[cn]
            #print(ohlc)
            if not last_date:
                last_date = ohlc['Date'].iloc[-1]
    df = __strategy_post_algo(df)
    """
    select columns
    """
    #print(g_rule)
    if 'columns' in g_rule:
        output_cols = g_rule['columns']
        if not output_cols:
            output_cols.extend(df.columns.values)
        df = df[output_cols]
    else:
        output_cols = df.columns.values
        df = df[output_cols]
    
    ret = {}
    ret['raw'] = df
    #__print_df(df)

    print("======= SCAN ===================================")
    df = __strategy_scan(df)
    __print_df(df)
    ret['scan']=df
    #print(ohlc)
    # TODO ohlc.to_csv(r'ohlc.csv')
    print("last date is", last_date)
    run_model(df)
    return ret


'''
from matplotlib import style
def plot_ohlc(ohlc):
    ax = plt.gca()
    ohlc.plot(ax=ax, kind='line')
    plt.show()
'''
# deep learning, TODO
def run_model(df_algo):
    if 'model' in g_rule:
        models = g_rule['model']
    else:
        return

    print("======= RUNNING MODEL===================================")
    this_model = models[0]
    model_file = this_model["name"]
    mod = __import__('model.'+model_file, globals(), locals(), [model_file])
    model_entry = mod.model


    df_model = g_symbol_df.copy()[["symbol"]]
    if 'ohlc_output' in this_model:
        symbol_set = set(models[0]['ohlc_output'])

    for index, row in df_model.iterrows():
        symbol = row['symbol']
        ohlc = g_ohlc_dct[symbol]
        #print('model=',id(ohlc))
        # Drop missing value
        #ohlc.fillna(value=-99999, inplace=True)
        #ohlc.is_copy = None
        df1 = ohlc[['Date']+models[0]["input_cols"]].copy()
        df1.dropna(inplace=True)
        #print('==---------*****************^%%%%%%%%%%%%%++++++++++++++++')
        ind_dct,dfpred = model_entry(symbol,df1,this_model)
        #print(ohlc[-100:])
        g_ohlc_dct[symbol] = ohlc
        ind_dct['px'] = ohlc['Close'].iloc[-1]
        if ind_dct:
            for cn in ind_dct:
                df_model.loc[index, cn] = ind_dct[cn]
        if dfpred is not None and symbol in symbol_set:
            print('========================= PREDICTION =========================================')
            print(dfpred)
            ax = plt.gca()
            dfpred.plot(ax=ax, kind='line')
            #plot_ohlc(dfpred)
            #thread1 = threading.Thread(target = plot_ohlc, args = (dfpred,))
            #thread1.start()

    if hasattr(mod, 'model_post'):
        mod.model_post(df_algo)


    # sort
    if 'sort' in models[0]:
        sort_list = models[0]['sort']
        if sort_list:
            sort_cols=[]
            asc_list=[]
            for dct in sort_list:
                for key,value in dct.items():
                    sort_cols.append(key)
                    asc_list.append(False if value=="False" else True)
            df_model.sort_values(by=sort_cols, inplace=True, ascending=asc_list)
            pass
    print(tabulate(df_model, tablefmt="pipe", headers="keys",showindex=False))
    print(df_model.describe())
    plt.show()
    #print(df)




def __strategy_post_algo(df):
    for algo_info in g_algo_list:
        fdr = algo_info.fdr
        algo_name = algo_info.name
        algo_file = algo_info.file
        algo_inx = algo_info.inx
        algo_param = algo_info.param
        #ohlc_dct = algo_info.ohlc_dct
        print("run post algo:", algo_name, ",feeder:", fdr.name, ",param:", algo_param)
        df = algo_inx.post_algo(df, g_ohlc_dct)
    return df

# scan and pick columns
def __strategy_scan(df):
    if 'criteria' in g_rule:
        criteria = g_rule['criteria']
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
    if 'columns' in g_rule:
        output_cols = g_rule['columns']
        if not output_cols:
            output_cols.extend(df.columns.values)

        #print('===========================================',output_set)
        for col in collst:
            if col not in output_cols:  # keep origin order
                output_cols.append(col)
        df = df[output_cols]
    if 'sort' in g_rule:
        sort_list = g_rule['sort']
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



def __merge_rt(ohlc_today):
    for symbol, ohlc in ohlc_dct:
        ts = ohlc.index[-1].to_datetime()
        newt = ts + datetime.timedelta(days=1)  # get today timestamp
        ohlc.loc[newt] = {
            'Open': ohlc_today['Open'],
            'Close': ohlc_today['Close'],
            'High': ohlc_today['High'],
            'Low': ohlc_today['Low'],
            'Volume': ohlc_today['Volume'],
            'Adj Close': ohlc_today['Close']
        }



"""
scan routine, strategy is algo_list which is consist of many algo,
this function will run each algo then merge their result into one table.
"""
def run_strategy():
    df = g_symbol_df.copy()
    print('run_strategy',df)
    __strategy_init_ohlc()

    # parse feeder -----------------------------
    fdrcfg = {'type':'normal'}
    #print(g_rule)
    if 'feeder' in g_rule:
        fdrcfg = g_rule['feeder']

    if fdrcfg['type']=='realtime':
        ibquote = IbQuote()
        ibquote.get_quote_batch(g_symbol_df)
        while True:
            if not ibquote.ready():
                time.sleep(5)
                continue
            else:  #merge hist and live data
                __merge_rt(ibquote.ohlc_dct)
            __strategy_run_algo(df)
            pass
    else: #not realtime
        return __strategy_run_algo(df)
    pass

"""
import argparse
# help flag provides flag help
# store_true actions stores argument as True
parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file', type=str, default='./config/trend.json', help="config file")
args = parser.parse_args()
"""

def get_feeder_name():
    if 'feeder' in g_rule and 'name' in g_rule['feeder']:
        fdrname = g_rule['feeder']['name'].upper()
    else:
        fdrname = 'IB1D'
    if fdrname in ['IB1D','IB1H','IB1D5Y']:
        return fdrname
    else:
        return 'IB1D'

def main(rule,symbolfn='./symbol_ib.txt'):
    global g_symbol_df,g_rule,g_fdr_name
    g_rule = rule
    g_symbol_df = common.load_symbol_csv(symbolfn)
    #feeder = 'IB1D'
    g_fdr_name = get_feeder_name()

    for algo_dct in g_rule['algo']:
        #param is dict
        #algo_param = dict.fromkeys(dct['param'], 1)
        g_algo_list.append(AlgoInfo(algo_dct['name'],algo_dct['param'],g_fdr_name))

    if not g_symbol_df.empty:
        return run_strategy()        
    else:
        print("usage: prog  -f symbol_file -s symbol_lst -a algo -p algo_param -d feeder")
        return {}
    pass



#main(None)
