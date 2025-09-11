from pybit.unified_trading import HTTP
from pprint import pprint
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta
import pandas as pd
from time import sleep
import time


script_dir = Path(__file__).parent

session = HTTP(
    testnet=False,
    # api_key="DYagNLt8eh6FKFCsbn",
    # api_secret="bVvLdk08q84VdpO5s6oDoHD4diPeUHv9la9z",
)

def timestamp_to_date(timestamp_ms):
    # candle_date=datetime.fromtimestamp(timestamp_ms)
    dt_obj = datetime.fromtimestamp(int(timestamp_ms) / 1000)
    dt_str = dt_obj.strftime("%Y-%m-%d %H:%M:%S")
    return dt_str

def save_json(data,file_name):
    script_dir = Path(__file__).parent
    with open(f'{script_dir}/{file_name}.json', 'w', encoding='utf8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

session = HTTP(testnet=False)

def get_live_candles(coin_name,duration,interval,days_ago=0):
    todays_timestamp= int(datetime.timestamp(datetime.now()-timedelta(days_ago))*1000)+6000*15
    # specific_date = datetime(2020, 2, 13)
    # earliest data I could get today 8/9/2025 is from 2020,2,13 (1581552000000) for 60m interval 
    # earliest data I could get today 8/9/2025 is from 2020,3,25 (1585094400000) for 1m interval
    # & C:/Users/kinga/AppData/Local/Programs/Python/Python311/python.exe f:/Files/LinuxProgrammingFiles/tests/Bybit_Notion/bybit/get_candle_data/get_candle_data_v2.py

    # hour = 
    day= 8
    month= 9
    year= 2024

    specific_timestamp = int(datetime.timestamp(datetime(year, month, day))*1000)

    time_diff = (datetime.fromtimestamp(todays_timestamp/1000) - datetime.fromtimestamp(specific_timestamp/1000)).days

    print(time_diff)

    start_timestamp = 1753632000000

    category="linear"

    coin = coin_name

    duration = duration * 1
    live_timestamp = todays_timestamp - (6000 * 10 * 1440 * duration)
    start_timestamp = live_timestamp

    interval = interval
    other = interval
    interval = 1440 if other == "D" else 10080 if other == "W" else interval
    # duration = duration if time_diff >= duration else time_diff


    all_candles = []
    total_candles = int(duration * 1 * 24 * (60/interval))
    candle_num = 0

    add_timestamp = interval * 60000 * 1000
    end_timestamp = start_timestamp + add_timestamp

    while candle_num < total_candles:
        raw_candles_data = session.get_kline(
            category=category,
            symbol=coin,
            interval=interval,
            limit=total_candles if total_candles < 1000 else 1000,
            start=start_timestamp,
            # end=end_timestamp,
        )['result']['list']
        raw_candles_data = list(reversed(raw_candles_data))
        # save_json(raw_candles_data,"temp_list")
        start_timestamp += add_timestamp 
        if len(raw_candles_data) == 0 or len(raw_candles_data) == 7:
            print("there is no more data")
            break
        for candle in raw_candles_data:
            candle_num+=1
            all_candles.append(candle)
            if candle_num >= total_candles+1:
                # print("rumber reached")
                break
        # sleep(5)
        print(f"{coin} {interval} m {duration} d ")
        print(f"{candle_num} /{total_candles} {100*candle_num/total_candles:.2f}%")
        print(datetime.fromtimestamp(start_timestamp/1000).strftime('%Y-%m-%d (%H:%M)'))
        end_timestamp += add_timestamp
    # save_json(all_candles,"raw_data")


    candles_data = {}
    open_prices = []
    high_prices = []
    low_prices = []
    close_prices = []
    date=[]

    for candle in all_candles:
        candle_timestamp= candle[0]
        open = candle[1]
        high = candle[2]
        low = candle[3]
        close = candle[4]
        volume= candle[5]
        turnover = candle[6]
        
        open_prices.append(open)
        high_prices.append(high)
        low_prices.append(low)
        close_prices.append(close)
        date.append(timestamp_to_date(candle_timestamp))
    candles_data = {
        "date" : date,
        "close" : close_prices,
        "open" : open_prices,
        "high" : high_prices,
        "low" : low_prices,
    }

    candles_dataframe = pd.DataFrame(candles_data)

    num_days = int(candle_num * interval /1440)

    candles_dataframe.to_csv(f'{script_dir}/{coin}_{interval}m_Live.csv', index=False)
    print(f"data saved to {coin}_{interval}m_{duration}d_{num_days}D.csv")

# get_live_candles("BTCUSDT",.25,1)

# while True:
#     get_live_candles("MOODENGUSDT",5.25,1)
#     sleep(1)
