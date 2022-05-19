#####################################################################
#
# Interface between investor and exchange
#
# TODO1: check if trader ids are unique
# TODO2: implement maker taker fee
# TODO3: option to restrict short selling
#
#####################################################################

import numpy as np
import pandas as pd
import random
import string
import math


class Interface:
    
    def __init__(self):
        self.book = None
        self.trader_ids = pd.DataFrame([], columns = ["trader", "trader_id"]).set_index("trader_id")
        self.taker_fee = 0.0008
        self.maker_fee = 0.0005
        self.retail_limit_fee = 3
        self.retail_market_fee = 2
        self.retail_cancel_limit_fee = 0
    
    def connect_trader(self, traders):
        for trader in traders:
            new_ID = self.generate_trader_ID()
            trader.get_trader_id(new_ID)
            self.trader_ids = pd.concat([self.trader_ids,
                                             pd.DataFrame([[trader, new_ID]],
                                                          columns = ["trader", "trader_id"]).set_index("trader_id")])
        print("Successfully connected %i traders to the exchange"%len(traders))
        return None
    
    def generate_trader_ID(self, id_length=8):
        all_char = string.ascii_uppercase + string.ascii_lowercase + string.digits
        # TODO1 check if trader_ID is doubled
        trader_ID = ''.join(random.choice(all_char) for _ in range(id_length))
        return trader_ID
    
    def connect_orderbook(self, orderbook):
        try:
            self.book = orderbook
            print("Connection to orderbook successful. There are %i stocks in the orderbook."%len(orderbook.book))
        except:
            print("Could not connect to orderbook. Please try again.")
        return None
    
    def connect_trade_reporter(self, trade_reporter):
        try:
            self.trade_reporter = trade_reporter
            print("Connection to trade reporter successful.")
        except:
            print("Could not connect to trade reporter. Please try again.")
        return None
    
    def show_orderbook(self, stock):
        """
        shows the prices and quantities of the orderbook for a given stock
        @param exchange: Orderbook object: orderbook from which the bid/ask prices should be shown
        @param stock: string: name of the stock of interest
        @param direction: string or None: only show bid or ask section of orderbook. Shows both if None
        """
        if stock in self.book.stock_list:
            self.book.book[stock]["bid"].sort_values(["Price", "Quantity"],
                                                     inplace = True,
                                                     ascending = [False, False])
            self.book.book[stock]["ask"].sort_values(["Price", "Quantity"],
                                                     inplace = True,
                                                     ascending = [True, False])
            bid = self.book.book[stock]["bid"]
            ask = self.book.book[stock]["ask"]
            return bid, ask
        
    def get_spread(self, stock):
        """
        get the bid/ask spread of a certain stock
        @param stock: string: name of the stock of interest
        """
        ask = self.book.book[stock]["ask"].Price.min()
        bid = self.book.book[stock]["bid"].Price.max()
        spread = ask-bid
        if abs(spread) < math.inf:
            return spread
        else:
            print("No available spread. At least one side of the orderbood is empty.")
            return None
    
    def limit_bid(self, stock, p, q, trader_id):
        """
        checks validity of order and sends it to orderbook
        @param stock: string: name of stock to be bought
        @param p: float: price at which order should be filled
        @param q: int: number of shares to be traded
        @param trader_id: string: id of trader who sent the order
        """
        if q == 0:
            return None
        if not stock in self.book.stock_list:
            print("Invalid stock name. No order has been placed.")
            return None
        best_ask = self.book.best_ask(stock)
        if best_ask.Price <= p:
            self.market_bid(stock, min(q, best_ask.Quantity), trader_id)
            self.limit_bid(stock, p, q-min(q, best_ask.Quantity), trader_id)
        else:
            self.book.add_bid(stock, p, q, trader_id)
        return True
        
    def limit_ask(self, stock, p, q, trader_id):
        """
        checks validity of order and sends it to orderbook
        @param stock: string: name of stock to be sold
        @param p: float: price at which order should be filled
        @param q: int: number of shares to be traded
        @param trader_id: string: id of trader who sent the order
        """
        if q == 0:
            return None
        if not stock in self.book.stock_list:
            print("Invalid stock name. No order has been placed.")
            return None
        best_bid = self.book.best_bid(stock)
        if best_bid.Price >= p:
            self.market_ask(stock, min(q, best_bid.Quantity), trader_id)
            self.limit_ask(stock, p, q-min(q, best_bid.Quantity), trader_id)
        else:
            self.book.add_ask(stock, p, q, trader_id)
        return True
    
    def market_bid(self, stock, q, trader_id):
        """
        checks validity of market bid order and places the order if valid
        """
        if not stock in self.book.stock_list:
            print("Invalid stock name. No order has been placed.")
            return None
        q = min(q, self.book.book[stock]["ask"].Quantity.sum())
        if q <= 0:
            return None
        best_ask_index = self.book.book[stock]["ask"].Price.idxmin()
        new_q = q - min(q, self.book.book[stock]["ask"].Quantity.loc[best_ask_index])
        self.book.add_bid(stock,
                          self.book.book[stock]["ask"].Price.loc[best_ask_index],
                          min(q, self.book.book[stock]["ask"].Quantity.loc[best_ask_index]),
                          trader_id)
        self.market_bid(stock, new_q, trader_id)
        return True
    
    def market_ask(self, stock, q, trader_id):
        """
        checks validity of market ask order and places the order if valid
        """
        if not stock in self.book.stock_list:
            print("Invalid stock name. No order has been placed.")
            return None
        q = min(q, self.book.book[stock]["bid"].Quantity.sum())
        if q <= 0:
            return None
        best_bid_index = self.book.book[stock]["bid"].Price.idxmax()
        new_q = q - min(q, self.book.book[stock]["bid"].Quantity.loc[best_bid_index])
        self.book.add_ask(stock,
                          self.book.book[stock]["bid"].Price.loc[best_bid_index],
                          min(q, self.book.book[stock]["bid"].Quantity.loc[best_bid_index]),
                          trader_id)
        self.market_ask(stock, new_q, trader_id)
        return True
    
    def communicate_filled_order(self, order_id, stock, p, q, direction):
        trader = self.book.order_trader.loc[order_id].trader_id
        if trader == -1:
            return None
        trader = self.trader_ids.loc[trader].trader
        trader.filled_order_info(stock, p, q, direction)
        return None