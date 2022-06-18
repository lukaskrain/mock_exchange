#####################################################################
#
# Test file creates simulated trades and connects with the
# exchange-trader interface
#
#####################################################################

import numpy as np
import pandas as pd
import csv
import random
import matplotlib.pyplot as plt
plt.style.use('ggplot')
from tqdm import tqdm

import matching_engine
import orderbook
import sim_traders
import sim_traders
import TE_interface
import trade_reporter
import trader

stock_list = list(csv.reader(open("stock_list.txt", "r")))[0]
starting_prices = list(csv.reader(open("stock_list.txt", "r")))[1]

############################# initialize and set up all connections #############################
me = matching_engine.Matching_Engine()
ob = orderbook.Orderbook(stock_list)
trade_rep = trade_reporter.TradeReporter(stock_list, starting_prices)
interface = TE_interface.Interface()
trade_sim = sim_traders.Random_Traders(p_market = 0.05, p_limit = 0.08)
t1 = trader.Trader()
t2 = trader.Trader()
t3 = trader.Trader()

interface.connect_orderbook(ob)
interface.connect_trade_reporter(trade_rep)

t1.connect_interface(interface)
t2.connect_interface(interface)
t3.connect_interface(interface)

interface.connect_trader([t1, t2, t3])

ob.connect_matching_engine(me)
ob.connect_trade_reporter(trade_rep)

me.connect_orderbook(ob)
me.connect_interface(interface)
me.connect_trade_reporter(trade_rep)

trade_rep.connect_interface(interface)
trade_sim.connect_interface(interface)




############################# simulate time periods with random supply and demand #############################
time_intervals = 500
for _ in tqdm(range(time_intervals), position=0, leave=True):
    trade_sim.limit_orders(vola=5)
    # rarely switch to t distributed limit orders
    #if np.random.randint(100) > 96:
    #    trade_sim.limit_orders(dist = "t", df = 5)
    # rarely switch to t distributed limit orders
    #if np.random.randint(100) > 90:
    #    trade_sim.limit_orders(dist = "uniform")
    trade_sim.market_orders(dynamic=False)
    trade_sim.delete_order()
    
    
    ###### end of period ######
    trade_rep.end_period()


trade_rep.show_asset_prices()
avg_ret_A = trade_rep.p_t["A"].pct_change().mean()*100
print("Average return of stock A is: " + str(avg_ret_A))
