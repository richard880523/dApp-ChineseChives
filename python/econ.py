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
    # bar is a list type objectc
    bars = klines(symbol, interval, num)

    # delete unwanted data - just keep date, open, high, low, close
    for line in bars:
        del line[5:]

    btc_df = pd.DataFrame(bars, columns=['date', 'open', 'high', 'low', 'close'])
    btc_df['date'] = pd.to_datetime(btc_df['date'], unit='ms')
    btc_df.set_index('date', inplace=True)

    # optional
    # calculate 20 moving average using Pandas
    # btc_df['20sma'] = btc_df.close.rolling(20).mean()
    
    # create sma and attach as column to original df
    btc_df['sma'] = btalib.sma(btc_df, period=20).df
    btc_df.close = pd.to_numeric(btc_df.close, errors='coerce')
    
    rsi = btalib.rsi(btc_df.close, period=14)
    # print(rsi.df.rsi[-1])
    
    macd = btalib.macd(btc_df.close, pfast=20, pslow=50, psignal=13)
    # print(macd.df)

    # join the rsi and macd calculations as columns in original df
    btc_df = btc_df.join([rsi.df, macd.df])
    
    btc_df = btc_df.fillna('null')
    # print(btc_df.tail())
    # print(btc_df.size)
    # return btc_df.to_json()
    btc_list = btc_df.values.tolist()
    # print(btc_list[0])
    return btc_list

if __name__ == "__main__":
    # Test Section
    # print( klines("ETHUSDT", '1m', 100) )
    print( indicator('ETHUSDT', '1d', 100) )
