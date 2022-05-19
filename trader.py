#####################################################################
#
# Trader class that communicates with the exchange interface and
# stores all information for the trader
#
# TODO1 are trader_ids unique
# TODO2 delete limit order
#
#####################################################################

import pandas as pd
import numpy as np


class Trader:
    
    def __init__(self, start_capital=1000000):
        self.start_capital = start_capital
        self.capital = pd.DataFrame([[start_capital, 0, start_capital]],
                                    columns = ["Cash", "Stocks", "Total Assets"])
        self.waiting_orders = pd.DataFrame([], columns = ["Stock", "Direction", "Entry Price", "Quantity"])
        self.filled_orders = pd.DataFrame([], columns = ["Stock", "Direction", "Price", "Quantity"])
        self.shares_owned = None
    
    def connect_interface(self, interface):
        try:
            self.interface = interface
            try:
                self.shares_owned = pd.DataFrame({s: [0] for s in interface.book.stock_list})
            except:
                print("Interface did not connect to an orderbook yet. Trader reporter cannot be linked.")
                return None
            print("Connection to trader-exchange interface successful.")
        except:
            print("Could not connect to trader-exchange interface. Please try again.")
        return None
    
    def get_trader_id(self, trader_id):
        self.trader_id = trader_id
        return None
    
    def orderbook(self, stock, side=2):
        """
        display the orderbook of a stock of interest
        @param side: int: 0 shows bid side, 1 shows ask side and 2 shows both sides of the orderbook
        """
        if side not in [0, 1, 2]:
            print("Invalid side of the order book.")
            return None
        sides = ["Bid", "Ask"]
        if side == 2:
            print("Orderbook of stock "+stock+" for both sides. Bid and ask.")
            return self.interface.show_orderbook(stock)
        else:
            print("%s side of the orderbook of stock "%sides[side]+stock)
            return self.interface.show_orderbook(stock)[side]
    
    def limit(self, stock, p, q, direction, verbose=0):
        """
        sends limit order to exchange, where entry is checked and sent to orderbook is proper.
        """
        if verbose not in [0,1]:
            print("Got unexpected value for verbose. No order has been sent to the exchange.")
            return None
        if direction == "ask":
            if self.interface.limit_ask(stock, p, q, self.trader_id):
                # TODO1
                if verbose:
                    print("Sell limit order successfully sent.")
                return None
        elif direction == "bid":
            if self.interface.limit_bid(stock, p, q, self.trader_id):
                # TODO1
                if verbose:
                    print("Buy limit order successfully sent.")
                return None
    
    def market(self, stock, q, direction, verbose=0):
        """
        sends market order to exchange interface
        """
        if verbose not in [0,1]:
            print("Got unexpected value for verbose. No order has been sent to the exchange.")
            return None
        if direction == "ask":
            if self.interface.market_ask(stock, q, self.trader_id):
                # TODO1
                if verbose:
                    print("Sell market order successfully sent.")
                return None
        elif direction == "bid":
            if self.interface.market_bid(stock, q, self.trader_id):
                # TODO1
                if verbose:
                    print("Buy market order successfully sent.")
                return None
    
    def filled_order_info(self, stock, p, q, direction):
        self.filled_orders = pd.concat([self.filled_orders,
                                        pd.DataFrame([[stock, direction, p, q]],
                                                     columns = ["Stock", "Direction", "Price", "Quantity"])])
        self.alter_capital_allocation(stock, p, q, direction)
        return None
    
    def alter_capital_allocation(self, stock, p, q, direction):
        if direction == "buy":
            self.capital.Cash -= p*q
            self.shares_owned.loc[0, stock] += q
        elif direction == "sell":
            self.capital.Cash += p*q
            self.shares_owned.loc[0, stock] -= q
        else:
            print("Invalid direction. Capital was not altered.")
            return None
        current_prices = self.get_prices().loc[0]
        self.capital.Stocks = np.dot(np.array(current_prices, dtype=float), self.shares_owned.loc[0])
        self.capital.loc[0, "Total Assets"] = (self.capital.Cash + self.capital.Stocks).values[0]
        return None
    
    def get_prices(self):
        return self.interface.trade_reporter.prices
    
    def get_capital(self):
        current_prices = self.get_prices().loc[0]
        self.capital.Stocks = np.dot(np.array(current_prices, dtype=float), self.shares_owned.loc[0])
        self.capital.loc[0, "Total Assets"] = (self.capital.Cash + self.capital.Stocks).values[0]
        return self.capital