import pandas as pd
import json
"""
symbol file 
"""
def load_symbol_file(fn):
    with open(fn, 'r') as f:
        txt = f.read()
        symbol_lst = txt.replace("\n", "").split(',')
        print(symbol_lst)
        return list(dict.fromkeys(symbol_lst))


def load_symbol_csv(fn):
    df = pd.read_csv(fn)
    df.fillna('', inplace=True)
    return df


def symbol_row2dct(row):
    dct = {
        'symbol': row['symbol'],
        'sectype': row['sectype'],
        'exchange': row['exchange'],
        'currency': row['currency'],
        'priexg': row['priexg']
    }
    return dct

"""
config/json
"""
def load_rule_file(fn):
    with open(fn, encoding='utf-8') as data_file:
        data = json.load(data_file)
        print('json config',data)
        return data
    return {}
