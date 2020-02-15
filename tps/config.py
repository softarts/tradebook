import os
import pandas
pandas.set_option('display.max_colwidth', 100)
pandas.set_option('display.max_columns', 50)
pandas.set_option('display.precision', 3)
pandas.set_option('display.expand_frame_repr', False)  # expand wide dataframe
pandas.set_option('display.max_rows', 10500)


dirname, filename = os.path.split(os.path.abspath(__file__))
#CACHE_PATH = dirname.replace("\\","/") + "/../cache/"
CACHE_PATH = "./cache/"
OHLC_SLICE = 0
#print(CACHE_PATH)