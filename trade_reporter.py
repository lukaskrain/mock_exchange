#####################################################################
#
# Trade Reporter keeps track of all completed activities in the 
# exchange and makes the information available to the traders
#
# TODO 1 create price ts
#
#####################################################################

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class TradeReporter:
    
    def __init__(self, stocks, starting_prices):
        self.completed_trades = pd.DataFrame(columns = ["Stock", "Price", "Quantity"])
        self.stocks = stocks
        self.prices = pd.DataFrame([[float(p) for p in starting_prices]], columns = stocks)
        self.p_t = pd.DataFrame([[float(p) for p in starting_prices]], columns = stocks)
        
    def connect_interface(self, interface):
        try:
            self.interface = interface
            print("Connection to trader-exchange interface successful.")
        except:
            print("Could not connect to trader-exchange interface. Please try again.")
        return None
    
    def get_spread(self, stock):
        """
        get the bid/ask spread of a certain stock from the orderbook
        @param stock: string: name of the stock of interest
        """
        ask = self.interface.book.book[stock]["ask"].Price.min()
        bid = self.interface.book.book[stock]["bid"].Price.max()
        spread = ask - bid
        if abs(spread) == math.inf:
            return None
        else:
            return spread
        
    def end_period(self):
        self.p_t = pd.concat([self.p_t, self.prices], ignore_index=True)
        
    def new_filled_order(self, stock, price, quantity):
        self.prices.loc[0, stock] = price
        self.completed_trades = pd.concat([self.completed_trades,
                                           pd.DataFrame([[stock, price, quantity]],
                                                        columns = ["Stock", "Price", "Quantity"])])
        return None
    
    def show_asset_prices(self, hight=15, width=None):
        n = len(self.stocks)
        height = 15
        if n%3 == 0:
            rows = n//3
        else:
            rows = n//3 + 1
        if n >= 3:
            columns = 3
            if not width:
                width = 7
        elif n == 2:
            columns = n
            if not width:
                width = 10
        else:
            columns = n
            if not width:
                width = 14
        plt.figure(figsize=(hight, width))
        for i in range(n):
            plt.subplot(rows, columns, i+1)
            plt.plot(self.p_t[self.stocks[i]].values)
            plt.title("Price of asset %s"%self.stocks[i])
        plt.show()
