from pickle import TRUE
from unittest import result
from urllib.request import BaseHandler
import ccxt
from matplotlib.pyplot import contour
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

def download(symbol, start_date, end_date, timeframe):
    tf_multi = exchange.parse_timeframe(timeframe) * 1000
    from_timestamp = exchange.parse8601(f'{start_date} 00:00:00')
    end_timestamp = exchange.parse8601(f'{end_date} 00:00:00')
    
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
    control = 1 if (price_now >= result[5] and price_now <= result[9]) else 0
    for i in range(len(result)):
        if(price_now<result[i]): 
            pos = i
            break
    if(term == "long"):
        return [result[max(0,pos-3-control)],result[min(pos+2+control,len(result)-1)]]
    if(term == "mid"):
        return [result[max(0,pos-2-control)],result[min(pos+1+control,len(result)-1)]]
    if(term == "short"):
        return [result[max(0,pos-1-control)],result[min(pos+control,len(result)-1)]]
    if(term == "skyground"):
        return [result[0],result[len(result)-1]]

def strategy(data,term,first_price):
    scale = find_range(data,term,first_price)
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
        scale
    ]

def backtrade(data,strategy,init_cash):
    scale = strategy[4]
    cash = init_cash
    curr = 0
    value_now = init_cash
    
    buy = strategy[2] - strategy[1]
    sell = strategy[2] + strategy[1]
    
    behavior = []
    for i in range(len(data)):
        if(i == 0):
            cash = cash - init_cash*strategy[3]*1.001
            curr = curr + init_cash*strategy[3]/data[i][4]
            value_now = cash + curr*data[i][4]
            behavior.append(["buy",init_cash*strategy[3]/data[i][4],data[i][4],value_now])
            
        else:
            
            if(data[i][4] < scale[0] or data[i][4] > scale[1]):
                continue
            elif(data[i][4] < buy):
                cash = cash - init_cash/strategy[0]*1.001
                curr = curr + init_cash/strategy[0]/buy
                buy = buy - strategy[1]
                sell = sell - strategy[1]
                value_now = cash + curr*data[i][4]
                behavior.append(["buy",init_cash/strategy[0]/buy,buy,value_now])
            elif(data[i][4] > sell):
                cash = cash + init_cash/strategy[0]/buy*sell*0.999
                curr = curr - init_cash/strategy[0]/buy
                buy = buy + strategy[1]
                sell = sell + strategy[1]
                value_now = cash + curr*data[i][4]
                behavior.append(["sell",init_cash/strategy[0]/buy,sell,value_now])
    return behavior

def rsi(data,init_cash):
    df = pd.DataFrame(data)
    header = ['t','o','h','l','c','v']
    df = pd.DataFrame(data, columns = header)
    df.ta.core = 4
    # rsi test
    rsi = ta.rsi(df['c'], length = 14)
    df['rsi'] = rsi

    entry = df.apply(lambda x: (x['rsi']<30),axis=1)
    exit = df.apply(lambda x: (x['rsi']>70),axis=1)

    pf = vbt.Portfolio.from_signals(df['c'],entries=entry,exits=exit,init_cash=init_cash, fees=0.001)
    end_value = pf.total_profit() + init_cash
    return end_value
  
# if __name__ == '__main__':
def trade(term, symbol, init_cash = 10000):
    # user define inputs
    # term = "long" #input1
    # symbol = 'BTC/USDT' #input2
    # init_cash = 10000 #input3
    
    # history data
    start_date = "2020-01-01"
    end_date = str(datetime.now())[:19]
    # timeframe can be [5m,15m,30m,2h,4h,1d]
    timeframe = '1d'
    
    data = download(symbol, start_date, end_date, timeframe)

    # test data
    # 現在交易的整個list,["buy/sell",amount,price,cash_now]
    start_date = (datetime.now() - relativedelta(days=14)).strftime("%Y-%m-%d")
    end_date = str(datetime.now())
    timeframe = '1m'
    test = download(symbol, start_date, end_date, timeframe)
    strate = strategy(data,term,test[0][4])
    # output1
    test_result = backtrade(test,strate,init_cash)

    # best data
    # 最佳交易的整個 list, ["buy/sell", amount,price, cash_now],
    # 取 best_result[len(best_result)-1][3] 為最後結算的錢
    start_best = "2022-03-14"
    end_best = "2022-03-28"
    best = download(symbol, start_best, end_best, timeframe)
    best_strate = strategy(data,term,best[0][4])
    # output2
    best_result = backtrade(best,best_strate,init_cash) 
    
    # worst data
    # 最差交易的整個 list, ["buy/sell", amount, price,cash_now],
    # 取 worst_result[len(worst_result)-1][3] 為最後結算的錢
    start_worst = "2022-04-29"
    end_worst = "2022-05-13"
    worst = download(symbol, start_worst, end_worst, timeframe)
    worst_strate = strategy(data,term,worst[0][4])
    # output3
    worst_result = backtrade(worst,worst_strate,init_cash) 

    # print(term, symbol), 所 print 即所要
    # print("now:", test_result[len(test_result)-1][3],"rsi:",rsi(test,init_cash))
    # print("best:", best_result[len(best_result)-1][3],"rsi:",rsi(best,init_cash))
    # print("worst:", worst_result[len(worst_result)-1][3],"rsi:",rsi(worst,init_cash))

    # order: (now, best, worst)
    ret_data = {
        'end_value': [test_result[len(test_result)-1][3], best_result[len(best_result)-1][3], worst_result[len(worst_result)-1][3]], 
        'rsi': [rsi(test,init_cash), rsi(best,init_cash), rsi(worst,init_cash)]
        }
    ret_df = pd.DataFrame(ret_data)
    ret_df = ret_df.round(decimals=8)
    ret_dict = ret_df.to_dict()
    print(ret_dict)

    return [ret_dict, test_result]
