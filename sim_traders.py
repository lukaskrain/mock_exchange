#####################################################################
#
# File simulates random trades to simulate a complete market with 
# numerous participants
#
#####################################################################



import numpy as np
import pandas as pd
import random




class Random_Traders:
    
    def __init__(self, n=25, p_market=0.2, p_limit=0.7, delete_factor=3, avg_ask_q=75, avg_bid_q=75):
        self.n = n
        self.p_market = p_market
        self.p_limit = p_limit
        self.del_factor = delete_factor#for poisson distribution for deleted orders
        self.avg_ask_q = avg_ask_q
        self.avg_bid_q = avg_bid_q
        self.asset_num = 0
        self.trade_prob = None
        self.momentum = None
    
    def connect_interface(self, interface):
        try:
            self.interface = interface
            self.asset_num = len(interface.book.stock_list)
            self.momentum = [0 for s in interface.book.stock_list]
            print("Connection to trader-exchange interface successful.")
        except:
            print("Could not connect to trader-exchange interface. Please try again.")
        return None
    
    def market_orders(self, vola_q=10, direction=None, dynamic=False):
        trade_checks = np.random.uniform(size=self.n)
        for i in range(self.n):
            if trade_checks[i] <= self.p_market:
                stock = random.choice(self.interface.book.stock_list)
                if not direction:
                    direction = random.choice(["bid", "ask"])
                if direction == "bid":
                    if dynamic:
                        calc_q = self.dynamic_q(stock)
                    else:
                        calc_q = 1
                    q = max(int(np.random.normal(self.avg_bid_q/calc_q, vola_q)), 0)
                    self.interface.market_bid(stock, q, -1)
                elif direction == "ask":
                    if dynamic:
                        calc_q = self.dynamic_q(stock)
                    else:
                        calc_q = 1
                    q = max(int(np.random.normal(self.avg_ask_q*calc_q, vola_q)), 0)
                    self.interface.market_ask(stock, q, -1)
        return None
    
    def limit_orders(self, stock=None, avg_price=None, vola=2.5, dist="normal", direction=None):
        trade_checks = np.random.uniform(size=self.n)
        for i in range(self.n):
            if trade_checks[i] <= self.p_limit:
                quantity = random.randint(10, 1000)
                if not stock:
                    stock = random.choice(self.interface.book.stock_list)
                if not avg_price:
                    avg_price = self.interface.trade_reporter.prices[stock][0]
                if not direction:
                    direction = random.choice(["bid", "ask"])
                if dist == "normal":
                    if direction == "bid":
                        price = np.random.normal(avg_price-vola/2, vola)
                    else:
                        price = np.random.normal(avg_price+vola/2, vola)
                elif dist == "uniform":
                    price = avg_price+(random.random()-0.5)*vola + vola/2
                elif dist == "t":
                    price = np.random.standard_t(1)+avg_price+vola/2
                if price <= 0:
                    continue
                if direction == "ask":
                    self.interface.limit_ask(stock, price, quantity, -1)
                if direction == "bid":
                    self.interface.limit_bid(stock, price, quantity, -1)
    
    def dynamic_q(self, stock):
        prices = self.interface.trade_reporter.p_t[stock].tail().values
        return prices[-1]/prices[0]
    
    def delete_order(self):
        stocks = self.interface.book.stock_list
        for stock in stocks:
            n0 = len(self.interface.book.book[stock]["bid"])
            n1 = len(self.interface.book.book[stock]["ask"])
            delete_num = np.random.poisson(self.del_factor, size=2)
            if n0 >= delete_num[0]:
                all_orders = self.interface.book.book[stock]["bid"].index[self.interface.book.book[stock]["bid"].index != -1]
                if len(all_orders) > 0:
                    delete_orders = np.random.choice(all_orders, delete_num[0])
                    self.interface.book.book[stock]["bid"].drop(delete_orders, inplace=True)
            if n1 >= delete_num[1]:
                all_orders = self.interface.book.book[stock]["ask"].index[self.interface.book.book[stock]["ask"].index != -1]
                if len(all_orders) > 0:
                    delete_orders = np.random.choice(all_orders, delete_num[1])
                    self.interface.book.book[stock]["ask"].drop(delete_orders, inplace=True)