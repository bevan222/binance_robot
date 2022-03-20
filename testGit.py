import os
import time
from binance.client import Client
from datetime import datetime
from dotenv import load_dotenv
import csv
import ccxt
from pprint import pprint


load_dotenv()

class volume_robot:
    def __init__(self,ticker):
        self.volume_list = []
        self.ticker = ticker
        self.side = 0
        klines_20min_ago = client.get_historical_klines(ticker, Client.KLINE_INTERVAL_1MINUTE,'21 minutes ago UTC')
        for data in klines_20min_ago:
            self.volume_list.append(data[5])
    
    def show_data(self):
        for data in self.volume_list:
            print(data)

    def show_current_order(self):
        current_order = client.futures_get_open_orders(symbol=self.ticker)
        for data in current_order:
            print(data)



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

def program_initailize():
    #get trade volume last 20 minutes
    robot  = volume_robot(os.getenv("TICKER"))
    #get future account's balance
    current_order = client.futures_get_open_orders(symbol=os.getenv("TICKER"))
    
    #get future account's 

program_initailize()

exchange = ccxt.binance({
    'enableRateLimit': True,  # required by the Manual https://github.com/ccxt/ccxt/wiki/Manual#rate-limit
    'apiKey': api_key,
    'secret': api_secret,
    'options': {  # exchange-specific options
        'defaultType': 'future',  # switch to a futures API/account
    },
})
pprint(exchange.fetchBalance())
ccxt.binancecoinm ().fetchPositions ()