from pickle import TRUE
from urllib.request import BaseHandler
import ccxt
import pandas as pd
import pandas_ta as ta
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
import math
import vectorbt as vbt
import numpy as np

exchange = ccxt.binance()

hold = 30
limit = 1000

def download(symbol, from_timestamp, end_timestamp, timeframe):
    tf_multi = exchange.parse_timeframe(timeframe) * 1000
    
    data = []
    candle_no = (int(end_timestamp) - int(from_timestamp)) / tf_multi + 1
    
    while from_timestamp < end_timestamp and (int(time.time()*1000)) > from_timestamp:
        try:
            ohlcvs = exchange.fetch_ohlcv(symbol, timeframe, from_timestamp, limit)
            
            # if (ohlcvs[0][0] > end_timestamp) or (ohlcvs[-1][0] > end_timestamp):
            if (ohlcvs[0][0] > end_timestamp) :
                break
            
            from_timestamp += len(ohlcvs) * tf_multi
            data += ohlcvs
            # print(str(len(data)) + ' of ' + str(int(candle_no)) + ' candle loaded... ')
            
        except(ccxt.ExchangeError, ccxt.AuthenticationError, ccxt.ExchangeNotAvailable, ccxt.RequestTimeout):
            time.sleep(hold)
        
    return data
    
def find_range(data,term,price_now):
    maxi = 0
    mini = 1000000
    price = []
    result = []
    quant = (10 ** (int(math.log10(price_now))-1))*2
    pos = 0
    for i in range(len(data)):
        for j in range(4):
            p = (int)(data[i][j+1]/quant)*quant
            maxi = max(maxi,p)
            mini = min(mini,p)
            price.append(p)
    for i in range(5):
        result.append(pd.value_counts(price).index[i])
    result.append(mini)
    result.append(maxi)
    result.append(mini + round((maxi-mini)*0.618/quant)*quant)
    result.append(mini + round((maxi-mini)*0.5/quant)*quant)
    result.append(mini + round((maxi-mini)*0.382/quant)*quant)
    result.sort()
    for i in range(len(result)):
        if(price_now<result[i]): 
            pos = i
            break
    if(term == "long"):
        return [result[max(0,pos-3)],result[min(pos+2,len(result)-1)]]
    if(term == "mid"):
        return [result[max(0,pos-2)],result[min(pos+1,len(result)-1)]]
    if(term == "short"):
        return [result[max(0,pos-1)],result[min(pos,len(result)-1)]]
    if(term == "skyground"):
        return [result[0],result[len(result)-1]]

def strategy(scale,term,first_price):
    block_num = 150
    if(term == "long"):
        block_num = 100
    if(term == "mid"):
        block_num = 80
    if(term == "short"):
        block_num = 40
    if(term == "skyground"):
        block_num = 150
        
    block_size = (scale[1] - scale[0])/block_num
    pos = (int)((first_price-scale[0])/block_size)
    #price now is between scale[0]+pos*block_size  and  scale[0]+(pos+1)*block_size
    percentage = (block_num - pos)/block_num
    
    return [
        block_num,
        block_size,
        scale[0]+pos*block_size,
        percentage,
    ]

def backtrade(data,scale,strategy,init_cash):
    cash = init_cash
    curr = 0
    df = pd.DataFrame(data)
    header = ['t','o','h','l','c','v']
    df = pd.DataFrame(data, columns = header)
    df.ta.core = 4
    
    buy = strategy[2] - strategy[1]
    sell = strategy[2] + strategy[1]
    
    behavior = []
    # entry = []
    # exit = []
    # size = []
    for i in range(len(data)):
        if(i == 0):
            print(init_cash,strategy[2],data[i][4],strategy[3],buy,sell)
            behavior.append(["buy",init_cash*strategy[3]/data[i][4],data[i][4]])
            cash = cash - init_cash*strategy[3]
            curr = curr + init_cash*strategy[3]/data[i][4]
            # entry.append(True)
            # exit.append(False)
            # size.append(init_cash*strategy[3]/data[i][4])
            
        else:
            # if(data[i][4] < scale[0] or data[i][4] > scale[1]):
            #     break
            # if(data[i][4] < buy):
            #     entry.append(True)
            #     exit.append(False)
            #     size.append(init_cash/strategy[0]/data[i][4])
            #     buy = buy - strategy[1]
            #     sell = sell - strategy[1]
            # elif(data[i][4] > sell):
            #     entry.append(False)
            #     exit.append(True)
            #     size.append(init_cash/strategy[0]/data[i][4])
            #     buy = buy + strategy[1]
            #     sell = sell + strategy[1]
            # else:
            #     entry.append(False)
            #     exit.append(False)
            #     size.append(0)
            
            if(data[i][4] < scale[0] or data[i][4] > scale[1]):
                break
            if(data[i][4] < buy):
                behavior.append(["buy",init_cash/strategy[0]/buy,buy])
                cash = cash - init_cash/strategy[0]
                curr = curr + init_cash/strategy[0]/buy
                buy = buy - strategy[1]
                sell = sell - strategy[1]
            elif(data[i][4] > sell):
                behavior.append(["sell",init_cash/strategy[0]/buy,sell])
                cash = cash + init_cash/strategy[0]/buy*sell
                curr = curr - init_cash/strategy[0]/buy
                buy = buy + strategy[1]
                sell = sell + strategy[1]
            # else:
            #     entry.append(False)
            #     exit.append(False)
            #     size.append(0)
    end_value = cash + curr*data[len(data)-1][4] 
    return [end_value,behavior]     
    
    # en = pd.DataFrame(entry)
    # ex = pd.DataFrame(exit)
    # si = pd.DataFrame(size)


    # pf = vbt.Portfolio.from_signals(df['c'],entries=en,exits=ex,init_cash=init_cash, fees=0.001, size=si)
    # print(pf.stats())
    # print(pf.orders.records_readable)

def rsi(data,init_cash):
    df = pd.DataFrame(data)
    header = ['t','o','h','l','c','v']
    df = pd.DataFrame(data, columns = header)
    df.ta.core = 4
    # rsi test
    rsi = ta.rsi(df['c'], length = 14)
    df['rsi'] = rsi

    entry = df.apply(lambda x: (x['rsi']<30),axis=1)
    # print(entry.value_counts())
    exit = df.apply(lambda x: (x['rsi']>70),axis=1)
    # print(exit.value_counts())

    pf = vbt.Portfolio.from_signals(df['c'],entries=entry,exits=exit,init_cash=init_cash, fees=0.001, size=0.0001)
    end_value = pf.total_profit() + init_cash
    return end_value
  
# if __name__ == '__main__':
def trade(term, symbol, init_cash = 10000):
    # user define inputs
    # term = "short" #input1
    # symbol = 'BTC/USDT' #input2
    # init_cash = 10000 #input3

    # history data
    start_date = "2020-01-01"
    end_date = str(datetime.now())[:19]
    # timeframe can be [5m,15m,30m,2h,4h,1d]
    timeframe = '1d' 

    from_timestamp = exchange.parse8601(f'{start_date} 00:00:00')
    end_timestamp = exchange.parse8601(f'{end_date} 00:00:00')
    data = download(symbol, from_timestamp, end_timestamp, timeframe)

    # test data
    # start_date = (datetime.now() - relativedelta(days=1)).strftime("%Y-%m-%d")
    start_date = "2022-04-12" 
    end_date = "2022-05-04"
    timeframe = '5m'

    from_timestamp = exchange.parse8601(f'{start_date} 00:00:00')
    end_timestamp = exchange.parse8601(f'{end_date} 00:00:00')
    test = download(symbol, from_timestamp, end_timestamp, timeframe)

    first_price = test[0][4]
    scale = find_range(data,term,first_price)
    strate = strategy(scale,term,first_price)
    
    # output,[最後有多少錢,交易過程]
    [end_value,behavior] = backtrade(test,scale,strate,init_cash)
    # print(behavior)
    # print(end_value)
    # rsi(data,init_cash)
    return [end_value, behavior]
