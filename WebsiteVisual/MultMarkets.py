"""
This is the layer above multiple stocks. It will run the same visual for MultStocks, and get that total equity curve line,
however, it will do it for each strategy, it is just a matter of coding that (look at back test funcitons). This will plot
Each strategies total equity curve, and then the total equity curve of each of those lines.

Should be very similar to the MultStocks.py
"""

"""
Can take a lot of code from Mult Stocks, might be a good idea to generalize mult stocks a little more first.

The concept would be it takes multiple stocks and run it through the strategy: the strategy should be the only thing 
that changes. The logic of the simulation stays the same regarding multiple stocks. 

Also, instead of plotting all the stocks, we only need the total equity curve line for each strategy.
"""

"""
Imports:
"""
import sys
import pandas as pd
import math
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import MultStrategies
from MultStocks import simulate
import WebDisplay
sys.path.append('../CustomStrategies/')
import Bollinger_Simulation
import LongTermSetup
import LongStrategy

sys.path.append('../DBMaintenance/')
import accessDB

"""
All the similar funcitons as multi stocks that simulate will refrence: Buy(), Sell(), FormatData(), equityCurve()
"""
def formatStockDataFrames(Stock_data):
    Stock_data = pd.DataFrame(Stock_data)
    Stock_data['datetime'] = pd.to_datetime(Stock_data['datetime'], unit='ms')
    Stock_data['datetime'] = Stock_data['datetime'].dt.date
    

    Stock_data = pd.DataFrame.drop(Stock_data, labels='_id', axis=1)

    Stock_data.index = Stock_data['datetime']

    Stock_data = pd.DataFrame.drop(Stock_data, labels='datetime', axis=1)


    Stock_data['SMA(9)'] = Stock_data.iloc[:,1].rolling(window=9).mean()
    Stock_data['SMA(27)'] = Stock_data.iloc[:,1].rolling(window=27).mean()

    return Stock_data

def formatCryptoDataFrames(Stock_data):

    Stock_data = pd.DataFrame(Stock_data)
    

    
    Stock_data['datetime'] = pd.to_datetime(Stock_data['datetime'], unit='s')
    Stock_data['datetime'] = Stock_data['datetime'].dt.date
    

    Stock_data = pd.DataFrame.drop(Stock_data, labels='_id', axis=1)

    Stock_data.index = Stock_data['datetime']

    Stock_data = pd.DataFrame.drop(Stock_data, labels='datetime', axis=1)


    Stock_data['SMA(9)'] = Stock_data.iloc[:,1].rolling(window=9).mean()
    Stock_data['SMA(27)'] = Stock_data.iloc[:,1].rolling(window=27).mean()

    return Stock_data

def buy(symbol, positions, capital, available, row):
    num_shares = math.floor(capital/row['close'])
    positions[symbol] = num_shares
    available = capital - (num_shares * row['close'])

    return positions, available

def sell(symbol, positions, available, row):
    available += row['close'] * positions[symbol]
    positions[symbol] = 0

    return positions, available

"""
The equity curve is the increase/decrease (%) from your initial investment, so it would be current value/initial value
current value = (positions * row[close]) + available cash
initial value = initial capital
available_cash = CAPITAL - (positions * row[close])
"""
def updateEquityCurve(equity_curve, symbol, positions, row, capital, available, initial_value):    
    available_cash = available
    CAPITAL = (positions[symbol] * row['close']) + available_cash
    equity_curve.append(((CAPITAL/initial_value) * 100) - 100)
    
    return equity_curve, CAPITAL, available_cash


def resetPositions(positions):
    for i in positions:
        positions[i] = 0

    return positions

def getCryptoIndex():

    BTC_data = accessDB.getCryptoHistory('BTC-USD', '1D')
    BTC_data = formatCryptoDataFrames(BTC_data)
    index = BTC_data.index
    #print(index)

    return index
"""
Simulate SmaCross(), can call the MultiStocks() simulate, (it uses the SmaCross strategy). So call call that method and just pull the data for the total
equity curve.
"""
def simulate_Sma_Crypto(Capital, positions):
    BTC_equity_curve = []
    ETH_equity_curve = []
    for symbol in positions:
        Crypto_data = accessDB.getCryptoHistory(symbol, '1D')
        Crypto_data = formatCryptoDataFrames(Crypto_data)
        if symbol == 'BTC-USD': BTC_equity_curve = simulate(Capital, symbol, Crypto_data, positions)
        #elif symbol == 'ETH-BTC': ETH_equity_curve = simulate(Capital, symbol, Crypto_data, positions)

    Total_equity_curve = []
    for i in range(len(BTC_equity_curve)):
        Total_equity_curve.append(BTC_equity_curve[i])
    return Total_equity_curve

"""
Simualte the BollingerBands with multiple stocks, very similar code as the Multistocks, just different buy/sell signals and technical analysis.
"""
def simulate_Bollinger_Crypto(Capital, positions):
    BTC_equity_curve = []
    ETH_equity_curve = []

    for symbol in positions:
        Stock_data = accessDB.getCryptoHistory(symbol, '1D')
        Stock_data = Bollinger_Simulation.formatDataFrames(Stock_data)
        Stock_data = LongTermSetup.long(Stock_data)
        if symbol == 'BTC-USD': 
            BTC_equity_curve = Bollinger_Simulation.Bollinger(Capital, symbol, Stock_data, positions)
        #elif symbol == 'ETH-BTC': 
            #ETH_equity_curve = Bollinger_Simulation.Bollinger(Capital, symbol, Stock_data, positions)
    Total_equity_curve = []
    for i in range(len(BTC_equity_curve)):
        Total_equity_curve.append(BTC_equity_curve[i])
    return Total_equity_curve

"""
Simulate the LongTerm strategy total equity curve. The strategy is in the custom strategies folder. Should run it on a givin dataframe, might need to edit it
a bit so it returns the correct things. Need to run the strategy on multiple stocks, and then calculate the total equity curve.
"""
def simulate_LongTerm_Crypto(Capital, positions):
    BTC_equity_curve = []
    ETH_equity_curve = []
    
    for symbol in positions:
        #print(symbol)
        Stock_data = accessDB.getCryptoHistory(symbol, '1D')
        Stock_data = formatCryptoDataFrames(Stock_data)
        Stock_data = LongTermSetup.long(Stock_data)
        if symbol == 'BTC-USD': 
            BTC_equity_curve = LongStrategy.Long(Capital, symbol, Stock_data, positions)
        #elif symbol == 'ETH-BTC': 
            #ETH_equity_curve = LongStrategy.Long(Capital, symbol, Stock_data, positions)
    Total_equity_curve = []
    for i in range(len(BTC_equity_curve)):
        Total_equity_curve.append(BTC_equity_curve[i])
    return Total_equity_curve

"""
Sentiment? Can do once we have the data.
"""
def simulate_Sentiment(Capital, positions):
    
    
    return

"""
Calculate each strategy equity curve here, calculate the total equity curve of all strategies, plot all of them. 
"""
def Crypto_TotalEquity():

    Capital_per_strategy = 100000
    positions = {'BTC-USD': 0}
    SMA_equity_curve = simulate_Sma_Crypto(Capital_per_strategy, positions)

    positions = resetPositions(positions)
    LongTerm_equity_curve = simulate_LongTerm_Crypto(Capital_per_strategy, positions)

    positions = resetPositions(positions)
    Bollinger_equity_curve = simulate_Bollinger_Crypto(Capital_per_strategy, positions)

    positions = resetPositions(positions)
    # Sentiment_equity_curve = simulate_Sentiment(Capital_per_strategy)

    total_equity_curve = []

    if(len(SMA_equity_curve) == len(Bollinger_equity_curve)) and (len(SMA_equity_curve) == len(LongTerm_equity_curve)):
        for i in range(len(SMA_equity_curve)):
            total_equity_curve.append((SMA_equity_curve[i] + Bollinger_equity_curve[i] + LongTerm_equity_curve[i])/3)
    else:
        print("SMA, Bollinger, and Longterm were not all the same length.")
    
    return total_equity_curve

def theBigShabang():
    stock_index = MultStrategies.getIndex()
    a, b, c, stock_equity_curve = MultStrategies.collectTotalEquityCurves()
    crypto_index = getCryptoIndex()
    crypto_equity_curve = Crypto_TotalEquity()
    total_equity_curve = []
    total_index = []
    i = 0
    j = 0
    while(i < len(stock_index) and j < len(crypto_index)):
        if stock_index[i] == crypto_index[j]:
            total_equity_curve.append((stock_equity_curve[i] + crypto_equity_curve[j]) / 2)
            total_index.append(stock_index[i])
            i+=1
            j+=1
        elif stock_index[i] > crypto_index[j]:
            total_equity_curve.append((stock_equity_curve[i] + crypto_equity_curve[j]) / 2)
            total_index.append(crypto_index[j])
            j+=1
        else:
            total_equity_curve.append((stock_equity_curve[i] + crypto_equity_curve[j]) / 2)
            total_index.append(stock_index[i])
            i+=1


    return total_equity_curve, total_index
            


def plotAll():
    a, b, c, Stock_total_equity = MultStrategies.collectTotalEquityCurves()
    stock_index = MultStrategies.getIndex()

    Crypto_total_equity = Crypto_TotalEquity()
    crypto_index = getCryptoIndex()

    total, total_index = theBigShabang()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x = stock_index, y = Stock_total_equity, name = 'Stock Market Equity Curve',
                                line=dict(color='royalblue'))) 
    fig.add_trace(go.Scatter(x = crypto_index, y = Crypto_total_equity, name = 'Crypto Market Equity Curve',
                                line=dict(color='red'))) 
    fig.add_trace(go.Scatter(x = total_index, y = total, name = 'Total Equity Curve',
                                line=dict(color='black', width=3))) 
    fig.update_layout(title='Combining Multiple Markets',
                   xaxis_title='Date',
                   yaxis_title='Change in Equity(%)')
    #fig.show()
    fig.write_html(WebDisplay.getDjangoPath() + '/multmarkets_norealloc.html')

#plotAll()

