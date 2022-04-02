from decimal import Decimal
import os
import time
import math
from tkinter import BOTH
from binance.client import Client
from datetime import datetime
from dotenv import load_dotenv
from binance.futures import Futures

load_dotenv()

class volume_robot:
    def __init__(self,ticker,api_key,api_secret,leverage,quantity,risk_time,add_percentage):
        self.ticker = ticker
        self.client = Client(api_key, api_secret)
        self.client_future = Futures(key=api_key, secret=api_secret)
        self.leverage = leverage
        self.quantity = quantity
        self.risk_time = int(risk_time)
        self.precision = len(str(Decimal(self.client.get_symbol_ticker(symbol=self.ticker)['price']).normalize()).split('.')[1])
        self.up_order = {}
        self.down_order = {}
        self.first_open_quantity = round((float(self.quantity) / float(self.client.get_symbol_ticker(symbol=self.ticker)['price'])))
        self.add_percentage = add_percentage
    def position_amount(self):
        position = self.client_future.get_position_risk(symbol=self.ticker)[0]
        return float(position['positionAmt'])
    
    def change_leverage(self,leverage):
        self.client_future.change_leverage(symbol=self.ticker, leverage=leverage)

    def get_income_sum(self):
        total_income = 0 
        for income_history in self.client_future.get_income_history():
            if(income_history['symbol'] == self.ticker):
                total_income += float(income_history['income'])
        return total_income

    def check_order_deal(self):
        if self.client.futures_get_order(symbol=self.ticker,orderId=self.up_order)['status'] == 'FILLED' or self.client.futures_get_order(symbol=self.ticker,orderId=self.down_order)['status'] == 'FILLED':
            return True
        return False

    def create_order(self):
        #print(self.risk_time)
        #print(self.quantity * math.pow(2,self.risk_time)-self.quantity*1)
        #print("max : " + str(self.first_open_quantity * math.pow(2,self.risk_time)-self.first_open_quantity*1))
        if abs(self.position_amount()) < self.first_open_quantity * math.pow(2,self.risk_time)-self.first_open_quantity*1:
            if self.position_amount() == 0:
                self.change_leverage(10)
                price = float(self.client.get_symbol_ticker(symbol=self.ticker)['price'])
                price_up = round(price * (1+float(self.add_percentage)),self.precision)
                price_down = round(price * (1-float(self.add_percentage)),self.precision)
                print("price up:" + str(price_up))
                print("price down:" + str(price_down))
                self.down_order = self.client.futures_create_order(
                    symbol=self.ticker,
                    type='LIMIT',
                    side='BUY',  # Direction ('BUY' / 'SELL'), string
                    quantity= round((float(self.quantity) / float(self.client.get_symbol_ticker(symbol=self.ticker)['price']))),  # Number of coins you wish to buy / sell, float
                    timeInForce = 'GTC',
                    price = price_down
                )['orderId']

                self.up_order = self.client.futures_create_order(
                    symbol=self.ticker,
                    type='LIMIT',
                    side='SELL',  # Direction ('BUY' / 'SELL'), string
                    quantity= round((float(self.quantity) / float(self.client.get_symbol_ticker(symbol=self.ticker)['price']))),  # Number of coins you wish to buy / sell, float
                    timeInForce = 'GTC',
                    price = price_up
                )['orderId']
            elif self.position_amount() > 0:
                print(self.position_amount())
                price = float(self.client.futures_account_trades()[-1]['price'])
                price_up = round(price * (1+float(self.add_percentage)),self.precision)
                price_down = round(price * (1-float(self.add_percentage)),self.precision)
                print("price up:" + str(price_up))
                print("price down:" + str(price_down))
                pos_amount = abs(self.position_amount())
                self.client_future.cancel_open_orders(symbol=self.ticker)

                self.down_order = self.client.futures_create_order(
                    symbol=self.ticker,
                    type='LIMIT',
                    side='BUY',  # Direction ('BUY' / 'SELL'), string
                    quantity=pos_amount*2,  # Number of coins you wish to buy / sell, float
                    timeInForce = 'GTC',
                    price = price_down
                )['orderId']

                self.up_order = self.client.futures_create_order(
                    symbol=self.ticker,
                    type='LIMIT',
                    side='SELL',  # Direction ('BUY' / 'SELL'), string
                    quantity=pos_amount*2,  # Number of coins you wish to buy / sell, float
                    timeInForce = 'GTC',
                    price = price_up
                )['orderId']
            elif self.position_amount() < 0:
                print(self.position_amount())
                price = float(self.client.futures_account_trades()[-1]['price'])
                price_up = round(price * (1+float(self.add_percentage)),self.precision)
                price_down = round(price * (1-float(self.add_percentage)),self.precision)
                print("price up:" + str(price_up))
                print("price down:" + str(price_down))
                pos_amount = abs(float(robot.client.futures_account_trades(symbol=robot.ticker)[-1]['qty']))
                self.client_future.cancel_open_orders(symbol=self.ticker)

                self.up_order = self.client.futures_create_order(
                    symbol=self.ticker,
                    type='LIMIT',
                    side='SELL',  # Direction ('BUY' / 'SELL'), string
                    quantity=pos_amount*2,  # Number of coins you wish to buy / sell, float
                    timeInForce = 'GTC',
                    price = price_up
                )['orderId']

                self.down_order = self.client.futures_create_order(
                    symbol=self.ticker,
                    type='LIMIT',
                    side='BUY',  # Direction ('BUY' / 'SELL'), string
                    quantity=pos_amount*2,  # Number of coins you wish to buy / sell, float
                    timeInForce = 'GTC',
                    price = price_down
                )['orderId']



api_key = os.getenv("API_KEY")
api_secret = os.getenv("PRIVATE_KEY")
leverage = os.getenv("LEVERAGE")
quantity = float(os.getenv("USDTQUANTITY"))
ticker = os.getenv("TICKER")
risk_time = os.getenv("RISK_TIME")
add_percentage = os.getenv("ADD_PERCENTAGE")


robot  = volume_robot(ticker,api_key,api_secret,leverage,quantity,risk_time,add_percentage)
print("leverage: " + str(robot.leverage))
print(robot.client.futures_position_information(symbol=robot.ticker))
print("position: " + str(robot.position_amount()))
robot.create_order()



while True:
    fetch_time = datetime.now()
    print(fetch_time.strftime("volume minute : "+"%Y-%m-%d %H:%M:%S"))
    print("open position: " + str(robot.position_amount()))
    print("recent open price: " + robot.client.futures_account_trades(symbol=robot.ticker)[-1]['price'])
    print("mark price: " + robot.client.futures_mark_price(symbol=robot.ticker)['markPrice'])
    up = robot.client.futures_get_order(symbol=robot.ticker,orderId=robot.up_order)
    down =robot.client.futures_get_order(symbol=robot.ticker,orderId=robot.down_order)
    print("up_order inform: " +up['status'] +" "+ up['side'] + " " + up['price'])
    print("down_order inform: " +down['status']+" "+ down['side'] + " " + down['price'])
    if robot.check_order_deal():
        time.sleep(5)
        robot.create_order()
        time.sleep(3)
    print()
    #print(robot.client.futures_account_trades(symbol=robot.ticker)[-1])
    #print(robot.client.futures_get_order(symbol=robot.ticker,orderId=robot.client.futures_account_trades(symbol=robot.ticker)[-1]['orderId']))
    time.sleep(5)