import os
import time
from binance.client import Client
from datetime import datetime
from dotenv import load_dotenv
import csv

load_dotenv()

def date_to_string(date_to_convert):
    date_str = ""
    date_str += date_to_convert.strftime("%Y-")
    date_str += date_to_convert.strftime("%m-")
    date_str += date_to_convert.strftime("%d ")
    date_str += date_to_convert.strftime("%H:")
    date_str += date_to_convert.strftime("%M:")
    date_str += date_to_convert.strftime("%S")

    print(date_str)
    return(date_str)


api_key = os.getenv("API_KEY")
api_secret = os.getenv("PRIVATE_KEY")
client = Client(api_key, api_secret)

#open time
#open
#high
#low
#close
#volume
#close time
#quote asset volume
#number of trade
#taker buy base asset volume
#taker buy quote asset volume
#ignore
trading_volume_list = []
buy_time = []
data_to_csv = []
trade_list = []
csv_num = 0

#print(client.futures_account_balance())


klines_20min_ago = client.get_historical_klines("ETHUSDT", Client.KLINE_INTERVAL_1MINUTE,'21 minutes ago UTC')
for data in klines_20min_ago:
    if len(trading_volume_list) < 21: 
        trading_volume_list.append(float(data[5]))


while True:
    fetch_time = datetime.now()  # using the local timezone
    fetch_second = int(fetch_time.strftime("%S"))
    if fetch_second % 4 == 3:
        print(fetch_time.strftime("volume minute : "+"%Y-%m-%d %H:%M:%S"))  # 2018-04-07 20:48:08, YMMV
        klines = client.get_historical_klines("ETHUSDT", Client.KLINE_INTERVAL_1MINUTE,'1 minutes ago UTC')
        #print(klines)
        volume_sum = sum(trading_volume_list)
        print("Last 20 minutes volume sum : " + str(volume_sum))
        print("Last 20 minutes volume average : " + str(volume_sum/len(trading_volume_list)))
        print("This minutes volume : " + str(klines[0][5]))
        eth_price = client.get_symbol_ticker(symbol="ETHUSDT")
        print("open: " + klines[0][1])
        print("now: " + eth_price['price'])
        price_change_rate_1minute = (float(eth_price['price'])-float(klines[0][1]))*100/float(klines[0][1])
        print(price_change_rate_1minute)
        print("")
        if float(klines[0][5]) > volume_sum*2/len(trading_volume_list):
            data_to_csv.append(date_to_string(datetime.now()))
            data_to_csv.append(klines[0][5])
            trade_list.append(data_to_csv)
            
            
            client.futures_change_leverage(symbol='ETHUSDT', leverage=10)
            if price_change_rate_1minute > 0:
                print("Long")
                with open('long_buy'+str(csv_num) +'.csv', 'w', encoding='UTF8', newline='') as f:
                    writer = csv.writer(f)
                    # write multiple rows
                    writer.writerow(data_to_csv)
                    csv_num += 1
                data_to_csv.clear()
                
                client.futures_create_order(
                    symbol='ETHUSDT',
                    type='MARKET',
                    side='BUY',  # Direction ('BUY' / 'SELL'), string
                    quantity=0.04  # Number of coins you wish to buy / sell, float
                )
                
                
            elif price_change_rate_1minute < 0:
                print("Short")
                with open('short_buy'+str(csv_num) +'.csv', 'w', encoding='UTF8', newline='') as f:
                    writer = csv.writer(f)
                    # write multiple rows
                    writer.writerow(data_to_csv)
                    csv_num += 1
                data_to_csv.clear()
                
                client.futures_create_order(
                    symbol='ETHUSDT',
                    type='MARKET',
                    side='SELL',  # Direction ('BUY' / 'SELL'), string
                    quantity=0.04  # Number of coins you wish to buy / sell, float
                )
                
            
            while(fetch_second % 60 != 3):
                fetch_time = datetime.now()  # using the local timezone
                fetch_second = int(fetch_time.strftime("%S"))
                time.sleep(1)
        else:
            time.sleep(0.1)
    if int(datetime.now().strftime("%S")) %60 == 59:
        trading_volume_list.pop(0)
        trading_volume_list.append(float(klines[0][5]))
        time.sleep(1)
    

