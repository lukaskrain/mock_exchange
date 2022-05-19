# Simulated Financial Exchange

This project simulates a limit orderbook with matching engine in order to simulate price changes for made up financial assets. It currently supports limit and market orders and the matching engine uses the pro rata method. 

## What it does and what it does not do
This is a research oriented project for orderbook simulations. It represents a research framework for backtesting trading strategies that need a limit orderbook. The project supports random agents and non-random agents. So you can change the behavior of the supply and demand side for limit and market orders for each asset due to random agents, correlate these orders etc. You can also implement non-random limit and market orders and thus implement LOB-based trading strategies due to manually added strategies for non-random agents, e.g. market makers. 

Since the main purpose of this project is research and not real-life deployment, performance/speed is certainly the main issue (it is written in python and not C++). Also there are currently no available APIs to connect different agents in one project. 

## Components
The components that make up this project are
1. Orderbook
2. Matching Engine
3. Trader-Exchange interface
4. Radom trader order generator
5. Trade reporter
6. Manual traders

where the orderbook simply holds all limit orders for each asset. The matching engine matches tradable bid and ask orders. The interface is the connection between the traders (simulated or manual) and the orderbook. The traders are not supposed to have access via commands directly to the orderbook. The trade reporter keeps all information of completed trades and makes those information available to market participants. 

## Process
First, all components need to be propberly connected.

Then, for every simulated time interval, the random and non-random agents submit their orders to the trader-exchange interface. The interface makes some validity checks and if successful, sends the order to the orderbook. Whenever the orderbook adds or deletes at least one order, the matching engine checks if there are tradable orders and executes them. The trade information of a completed trade are sent to the trade reporter. If one of the trading parties was a non-random agent, the trade information are sent to that agent too and its equity is adjusted accordingly.

You can see a simulated process in the 'trading_sim_tests.py' script.

## Reasoning
When we simulate price/return data of financial assets, we usually simulate some sort of (Geometric) Brownian Motion or GANs. However, the 'price' of a financial asset is the price of the most recent trade, i.e. the current price is not necessarily a good estimator for the next trade is the orderbook is very dry. Therefore, simulating prices based on orderbooks might be an interesting approach.

Further, academic research is uncertain, which distribution of asset return data is most appropriate. However, we could make a case that we can estimate the distribution of supply and demand behavior must better than return data directly.

## Disclaimer
Note that this project is made for research and informational purposes only. Do not take this for any type of financial, legal, tax or trading advice. Use this simulation at your own risk. 


## Next steps
Within the next commits, I will add 
1. maker-taker fees for more realistic market making research
2. more order types
3. more matching algorithms (FIFO)

