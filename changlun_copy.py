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
    def __init__(self,ticker,api_key,api_secret,leverage,quantity):
        self.ticker = ticker
        self.client = Client(api_key, api_secret)
        self.client_future = Futures(key=api_key, secret=api_secret)
        self.leverage = leverage
        self.quantity = quantity
        self.price_up = 0 
        self.price_down = 0

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

    def create_order(self):
        if self.position_amount() == 0:
            price_now = float(self.client.get_symbol_ticker(symbol=self.ticker)['price'])
            self.price_up = price_now * 1.028
            self.price_down = price_now * 0.972
            self.client.futures_create_order(
                symbol=self.ticker,
                type='LIMIT',
                side='BUY',  # Direction ('BUY' / 'SELL'), string
                quantity=self.quantity,  # Number of coins you wish to buy / sell, float
                timeInForce = 'GTC',
                price = self.price_down
            )

            self.client.futures_create_order(
                symbol=self.ticker,
                type='LIMIT',
                side='SELL',  # Direction ('BUY' / 'SELL'), string
                quantity=self.quantity,  # Number of coins you wish to buy / sell, float
                timeInForce = 'GTC',
                price = self.price_up
            )



api_key = os.getenv("API_KEY")
api_secret = os.getenv("PRIVATE_KEY")
leverage = os.getenv("LEVERAGE")
quantity = float(os.getenv("QUANTITY"))
ticker = os.getenv("TICKER")


robot  = volume_robot(ticker,api_key,api_secret,leverage,quantity)
print(robot.leverage)
print(robot.client.futures_position_information(symbol=robot.ticker))
print(robot.position_amount())

robot.create_order()