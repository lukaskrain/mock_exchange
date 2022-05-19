#####################################################################
#
# Orderbook class keeps all valid orders including information such
# as order ID, price, quantities, fees
#
#####################################################################

import numpy as np
import pandas as pd
import csv
import math
import string
import random



class Orderbook:
    
    def __init__(self, stocks, decimals=4):
        """
        orderbook class with all needed information
        orderbook has three entries per order per stock:
        list fo ask orders, list of bid orders, 8 digit unique order ID
        @param stocks: array-like: list of stock names traded in the index
        """
        self.stock_list = stocks
        self.decimals = decimals
        self.book = {s: {"bid": pd.DataFrame([[-math.inf, 0, -1]],
                                             columns = ["Price",
                                                        "Quantity",
                                                        "Order_ID"]).set_index("Order_ID"),
                         "ask": pd.DataFrame([[math.inf, 0, -1]],
                                             columns = ["Price",
                                                        "Quantity",
                                                        "Order_ID"]).set_index("Order_ID")}
                     for s in stocks}
        self.order_trader = pd.DataFrame([], columns = ["order_id", "trader_id"]).set_index("order_id")
    
    def connect_trade_reporter(self, trade_reporter):
        try:
            self.TR = trade_reporter
            print("Connection to trade reporter successful.")
        except:
            print("Could not connect to trade reporter. Please try again.")
        return None
    
    def connect_matching_engine(self, matching_engine):
        try:
            self.matching_engine = matching_engine
            print("Connection to matching engine successful. Matching algorithm is %s"%matching_engine.algo)
        except:
            print("Could not connect to matching engine. Please try again.")
        return None
    
    def generate_order_id(self, length=8):
        """
        generates 12-digit order id to identfy trades
        """
        new_order_id = ''.join(random.choice(string.digits) for _ in range(length))
        if not new_order_id in self.order_trader.index:
            return new_order_id
        else:
            return self.generate_order_id()
    
    def add_bid(self, stock, price, quantity, trader_id):
        """
        adds order to the bid side of the orderbook and calls matching engine
        @param price: float: price of order
        @param quantity: int: number of shares to trade
        @param order_id: int: unique identifier of order
        """
        new_order_id = self.generate_order_id()
        new_order = pd.DataFrame([[price, quantity, new_order_id]],
                                 columns = ["Price", "Quantity", "Order_ID"]).set_index("Order_ID")
        self.book[stock]["bid"] = pd.concat([self.book[stock]["bid"], new_order])
        self.order_trader = pd.concat([self.order_trader,
                                       pd.DataFrame([[new_order_id, trader_id]],
                                                    columns = ["order_id", "trader_id"]).set_index("order_id")])
        self.matching_engine.check_trades()
        return None
    
    def add_ask(self, stock, price, quantity, trader_id):
        """
        adds order to the ask side of the orderbook and calls matching engine
        @param price: float: price of order
        @param quantity: int: number of shares to trade
        @param order_id: int: unique identifier of order
        """
        new_order_id = self.generate_order_id()
        new_order = pd.DataFrame([[price, quantity, new_order_id]],
                                 columns = ["Price", "Quantity", "Order_ID"]).set_index("Order_ID")
        self.book[stock]["ask"] = pd.concat([self.book[stock]["ask"], new_order])
        self.order_trader = pd.concat([self.order_trader,
                                       pd.DataFrame([[new_order_id, trader_id]],
                                                    columns = ["order_id", "trader_id"]).set_index("order_id")])
        self.matching_engine.check_trades()
        return None
    
    def alter_bid(self, stock, order_id, new_q=None, new_p=None):
        """
        changes the price and the quantity of a given order_id
        """
        if not new_p:
            self.book[stock]["bid"].loc[order_id, "Price"] = new_p
        if not new_q:
            self.book[stock]["bid"].loc[order_id, "Quantity"] = new_q
        self.matching_engine.check_trades()
        return None
    
    def alter_ask(self, stock, order_id, new_q=None, new_p=None):
        """
        changes the price and the quantity of a given order_id
        """
        if not new_p:
            self.book[stock]["ask"].loc[order_id, "Price"] = new_p
        if not new_q:
            self.book[stock]["ask"].loc[order_id, "Quantity"] = new_q
        self.matching_engine.check_trades()
        return None
    
    def best_bid(self, stock):
        """
        returns complete orderbook entry of best bid order
        """
        return self.book[stock]["bid"].loc[self.book[stock]["bid"].Price.idxmax()]
    
    def best_ask(self, stock):
        """
        returns complete orderbook entry of best ask order
        """
        return self.book[stock]["ask"].loc[self.book[stock]["ask"].Price.idxmin()]
        

