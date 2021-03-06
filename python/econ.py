import pandas as pd
import numpy as np
import argparse
import datetime

from binance.spot import Spot
import btalib

def klines(symbol, interval, num = 1000):
    assert 0 < num and num <= 1000
    client = Spot()
    return client.klines(symbol, interval, limit=num)

## [TODO]: Economic Indicator Here ~
def indicator(symbol, interval, num = 1000):
    # bar is a list type object
    # pd.options.display.float_format = '{:, .4f}'.format
    bars = klines(symbol, interval, num)

    # delete unwanted data - just keep date, open, high, low, close
    for line in bars:
        del line[5:]
    
    btc_df = pd.DataFrame(bars, columns=['date', 'open', 'high', 'low', 'close'])
    btc_df[['date', 'open', 'high', 'low', 'close']] = btc_df[['date', 'open', 'high', 'low', 'close']].apply(pd.to_numeric)
    
    btc_df['date'] = pd.to_datetime(btc_df['date'], unit='ms')
    btc_df['date'] = btc_df['date'].astype(str)
    btc_df.set_index('date', inplace=True)

    # optional
    # calculate 20 moving average using Pandas
    # btc_df['20sma'] = btc_df.close.rolling(20).mean()
    
    # create sma and attach as column to original df
    btc_df['sma'] = btalib.sma(btc_df, period=20).df
    
    rsi = btalib.rsi(btc_df.close, period=14)
    macd = btalib.macd(btc_df.close, pfast=12, pslow=26, psignal=9)
    # print(macd.df)

    # join the rsi and macd calculations as columns in original df
    btc_df = btc_df.join([rsi.df, macd.df])
    
    btc_df = btc_df.fillna(0)
    btc_df = btc_df.round(decimals=8)
    btc_df = btc_df.reset_index()
    print(btc_df.dtypes)
    btc_dict = btc_df.to_dict()
    
    return btc_dict

if __name__ == "__main__":
    # Test Section
    # print( klines("ETHUSDT", '1m', 100) )
    # print( indicator('ETHUSDT', '1d', 100) )
    indicator('ETHUSDT', '1d', 100)
