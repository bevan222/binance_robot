from http import client
import os
import time
from binance.client import Client
from datetime import datetime
from dotenv import load_dotenv
import csv
from binance.futures import Futures
from flask import jsonify 


load_dotenv()

class volume_robot:

    #初始化
    def __init__(self,ticker,api_key,api_secret,leverage):
        self.volume_list = []
        self.ticker = ticker
        self.side = 0
        self.client = Client(api_key, api_secret)
        self.client_future = Futures(key=api_key, secret=api_secret)
        self.leverage = leverage

        klines_20min_ago = self.client.get_historical_klines(ticker, Client.KLINE_INTERVAL_1MINUTE,'21 minutes ago UTC')
        for data in klines_20min_ago:
            self.volume_list.append(float(data[5]))
    
    #顯示交易量列表
    def show_volume_list(self):
        for data in self.volume_list:
            print(data)

    #該分鐘價格變化量（％）
    def minute_price_change_rate(self):
        price_now = float(self.client.get_symbol_ticker(symbol=self.ticker)['price'])
        price_open = float(self.client.get_historical_klines(self.ticker, Client.KLINE_INTERVAL_1MINUTE,'1 minutes ago UTC')[0][1])
        return (price_now - price_open)*100 / price_open
        
    #抓取倉位大小
    def position_amount(self):
        position = self.client_future.get_position_risk(symbol=self.ticker)[0]
        return float(position['positionAmt'])

    #更新交易量列表
    def update_volume(self,vol):
        print("pop out volume:" + str(self.volume_list.pop(0)))
        print("append volume:" + str(vol))
        self.volume_list.append(float(vol))
    
    #抓取該分鐘交易量
    def get_this_min_volume(self):
        fetch_time = datetime.now()  # using the local timezone
        fetch_second = int(fetch_time.strftime("%S"))
        print(fetch_second)
        if(fetch_second != 0):
            return float(self.client.get_historical_klines(self.ticker, Client.KLINE_INTERVAL_1MINUTE,'1 minutes ago UTC')[0][5])

    #獲取過去20分交易量平均
    def get_20min_volume_average(self):
        volume_sum = sum(self.volume_list)
        return volume_sum//len(self.volume_list)

    #檢測該分鐘交易量是否超過過去20分平均
    def voulume_break(self):
        fetch_time = datetime.now()  # using the local timezone
        fetch_second = int(fetch_time.strftime("%S"))
        if fetch_second != 0:
            if(self.get_this_min_volume() > self.get_20min_volume_average()*2):
                return True
            else: 
                return False
        return False

    #更改合約倍數
    def change_leverage(self,leverage):
        self.client_future.change_leverage(symbol=self.ticker, leverage=leverage)

    #獲取該幣種歷史交易收入
    def get_income_sum(self):
        total_income = 0 
        for income_history in robot.client_future.get_income_history():
            if(income_history['symbol'] == robot.ticker):
                total_income += float(income_history['income'])
        return total_income
    
    def change_levearge(self,leverage):
        self.client.futures_change_leverage(symbol=self.ticker, leverage=leverage) 


    def create_order(self):
        #trade = self.client.futures_account_trades()[-1] #it fetch details of latest trade
        self.client.futures_change_leverage(symbol=self.ticker, leverage=self.leverage)
        if(self.minute_price_change_rate()>0):
            position_side = 'BUY'
            close_side = 'SELL'
        elif(self.minute_price_change_rate()<0):
            position_side = 'SELL'
            close_side = 'BUY'
        elif(self.minute_price_change_rate()==0):
            position_side = 'BUY'
            close_side = 'SELL'

        if(float(self.position_amount() ==0)):
            #該機器人合約幣種現在無倉位
            print("no position")
        elif(float(self.position_amount() <0)):
            #該機器人合約幣種現在有多頭倉位，所以有往上賣單往下賣單
            print("position buy")
            self.client_future.cancel_open_orders(symbol=self.ticker)#有新買點更新止盈止損

            
        elif(float(self.position_amount() >0)):
            #該機器人合約幣種現在現在有空頭倉位，所以有往下買單往上買單
            print("position sell")
            self.client_future.cancel_open_orders(symbol=self.ticker)#有新賣點更新止盈止損
        
        self.client.futures_create_order(
            symbol=self.ticker,
            type='MARKET',
            side='BUY',  # Direction ('BUY' / 'SELL'), string
            quantity=0.003  # Number of coins you wish to buy / sell, float
        )
        time.sleep(3)
        open_price = float(self.client.futures_account_trades()[-1]['price'])#it fetch details of latest trade
        print(open_price)
        self.client.futures_create_order(
            symbol=self.ticker,
            type='TAKE_PROFIT_MARKET',
            side='SELL',
            stopPrice=round(open_price*1.01,2),
            closePosition=True,
        )


        self.client.futures_create_order(
            symbol=self.ticker,
            type='STOP_MARKET',
            side='SELL',
            stopPrice=round(open_price*0.99,2),
            closePosition=True,
        )



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
leverage = os.getenv("LEVERAGE")


#get trade volume last 20 minutes
robot  = volume_robot(os.getenv("TICKER"),api_key,api_secret,leverage)
print(robot.leverage)
#robot.create_order()
print(robot.client.futures_position_information(symbol=robot.ticker))
print(robot.client_future.api_trading_status())


robot.client.futures_create_order(
    symbol=robot.ticker,
    type='MARKET',
    side='BUY',  # Direction ('BUY' / 'SELL'), string
    quantity=0.003  # Number of coins you wish to buy / sell, float
)

robot.client.futures_create_order(
    symbol=robot.ticker,
    type='MARKET',
    side='SELL',  # Direction ('BUY' / 'SELL'), string
    quantity=0.006  # Number of coins you wish to buy / sell, float
)


while True:
    fetch_time = datetime.now()  # using the local timezone
    fetch_second = int(fetch_time.strftime("%S"))
    robot.change_leverage(20)
    this_min_vol = robot.get_this_min_volume()
    if fetch_second % 4 == 3:
        print(fetch_time.strftime("volume minute : "+"%Y-%m-%d %H:%M:%S"))  # 2018-04-07 20:48:08, YMMV
        print("volume this min : " + str(robot.get_this_min_volume()))
        print("volume average last 20 min: " + str(robot.get_20min_volume_average()))
        print("volume change rate 1 min: " + str(robot.minute_price_change_rate()))
    
        if(robot.voulume_break()):
            if(robot.minute_price_change_rate()> 0):
                #判斷該分鐘為漲
                print()
            elif(robot.minute_price_change_rate()< 0):
                #判斷該分鐘為跌
                print()
                
                
        print()

        if fetch_second == 59:
            robot.update_volume(this_min_vol)
        time.sleep(1)
        
        


#get future account's balance



# Get account information
#client_future.change_position_mode(dualSidePosition=True)
#client_future.get_position_risk(symbol=os.getenv("TICKER")) #get symbol's position
#client_future.get_orders(symbol=os.getenv("TICKER"))#get symbol's ordering
