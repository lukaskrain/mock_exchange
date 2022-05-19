#####################################################################
#
# Matching engine class checks bid ask matches and orders call back
# to exchange-trader interface
#
#
#####################################################################

import numpy as np
import pandas as pd
import math



class Matching_Engine:
    
    def __init__(self, algo="pro rata"):
        self.algo = algo
        
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
    
    def connect_interface(self, interface):
        try:
            self.interface = interface
            print("Connection to trader-exchange interface successful.")
        except:
            print("Could not connect to trader-exchange interface. Please try again.")
        return None
    
    def check_trades(self, stock=None):
        """
        checks if orders can be matched and calls order execution
        """
        if stock:
            if self.book.book[stock]["bid"].Price.max() >= self.book.book[stock]["ask"].Price.min():
                self.execute_trade(stock)
        else:
            for stock in self.book.stock_list:
                if self.book.book[stock]["bid"].Price.max() >= self.book.book[stock]["ask"].Price.min():
                    self.execute_trade(stock)
        return None
    
    def communicate_filled_order(self, order_id, stock, price, quantity, direction):
        """
        sends order information of filled order to interface and trade reporter
        """
        self.trade_reporter.new_filled_order(stock, price, quantity)
        self.interface.communicate_filled_order(order_id, stock, price, quantity, direction)
        return None
    
    def update_orderbook(self, stock, q, ask_ID, bid_ID):
        """
        reduces quantity of bid and ask side for a given stock by the traded amount of units
        """
        self.book.book[stock]["ask"].loc[ask_ID, "Quantity"] -= q
        self.book.book[stock]["bid"].loc[bid_ID, "Quantity"] -= q
        if self.book.book[stock]["ask"].loc[ask_ID, "Quantity"] == 0:
            if self.book.book[stock]["ask"].loc[ask_ID, "Price"] < math.inf:
                self.book.book[stock]["ask"].drop(ask_ID, inplace = True)
        if self.book.book[stock]["bid"].loc[bid_ID, "Quantity"] == 0:
            if self.book.book[stock]["bid"].loc[bid_ID, "Price"] > -math.inf:
                self.book.book[stock]["bid"].drop(bid_ID, inplace = True)
        return None
        
    def execute_trade(self, stock):
        """
        matches tradable orders, reduces quantities and send info to interface and trade reporter
        """
        while self.book.book[stock]["bid"].Price.max() >= self.book.book[stock]["ask"].Price.min():
            # get filled trade info
            ask_orderID = self.book.book[stock]["ask"].Price.idxmin()
            bid_orderID = self.book.book[stock]["bid"].Price.idxmax()
            q = min(self.book.book[stock]["ask"].loc[ask_orderID, "Quantity"],
                    self.book.book[stock]["bid"].loc[bid_orderID, "Quantity"])
            p = self.book.book[stock]["ask"].loc[ask_orderID, "Price"]
            # send trade info to interface
            self.communicate_filled_order(ask_orderID, stock, p, q, "sell")
            self.communicate_filled_order(bid_orderID, stock, p, q, "buy")
            # update orderbook
            self.update_orderbook(stock, q, ask_orderID, bid_orderID)
        return None
            



    
    