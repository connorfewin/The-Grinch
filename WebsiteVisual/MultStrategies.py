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
import urllib
import sys
import pandas as pd
import math
import matplotlib.pyplot as plt
import matplotlib
#matplotlib.use('Agg')
from MultStocks import simulate
from MultStocks import formatDataFrames
import base64
from io import BytesIO
from io import StringIO
import plotly.graph_objects as go

sys.path.append('../DBMaintenance/')
import accessDB

sys.path.append('../CustomStrategies/')
import Bollinger_Simulation
import LongTermSetup
import LongStrategy
import WebDisplay
sys.path.append('../BackTest/')
from toDataFrame import toPandas as format

"""
All the similar funcitons as multi stocks that simulate will refrence: Buy(), Sell(), FormatData(), equityCurve()
"""
def formatDataFrames(Stock_data):

    Stock_data = pd.DataFrame(Stock_data)
    

    
    Stock_data['datetime'] = pd.to_datetime(Stock_data['datetime'], unit='ms')
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
    positions['AAPL'] = 0
    positions['FB'] = 0
    positions['IBM'] = 0
    positions['TSLA'] = 0

    return positions

def getIndex():

    AAPL_data = accessDB.getStockHistory('AAPL')
    AAPL_data = formatDataFrames(AAPL_data)
    index = AAPL_data.index

    return index
"""
Simulate SmaCross(), can call the MultiStocks() simulate, (it uses the SmaCross strategy). So call call that method and just pull the data for the total
equity curve.
"""
def simulate_Sma(Capital, positions):
    AAPL_equity_curve = []
    FB_equity_curve = []
    IBM_equity_curve = []
    TSLA_equity_curve = []
    for symbol in positions:
        Stock_data = accessDB.getStockHistory(symbol)
        Stock_data = formatDataFrames(Stock_data)
        if symbol == 'AAPL': AAPL_equity_curve = simulate(Capital, symbol, Stock_data, positions)
        elif symbol == 'FB': FB_equity_curve = simulate(Capital, symbol, Stock_data, positions)
        elif symbol == 'IBM': IBM_equity_curve = simulate(Capital, symbol, Stock_data, positions)
        elif symbol == 'TSLA': TSLA_equity_curve = simulate(Capital, symbol, Stock_data, positions)

    Total_equity_curve = []
    for i in range(len(AAPL_equity_curve)):
        Total_equity_curve.append((AAPL_equity_curve[i] + FB_equity_curve[i] + IBM_equity_curve[i] + TSLA_equity_curve[i])/len(positions))
    return Total_equity_curve


"""
Simualte the BollingerBands with multiple stocks, very similar code as the Multistocks, just different buy/sell signals and technical analysis.
"""
def simulate_Bollinger(Capital, positions):
    AAPL_equity_curve = []
    FB_equity_curve = []
    IBM_equity_curve = []
    TSLA_equity_curve = []
    Total_equity_curve = []

    for symbol in positions:
        Stock_data = accessDB.getStockHistory(symbol)
        Stock_data = Bollinger_Simulation.formatDataFrames(Stock_data)
        Stock_data = LongTermSetup.long(Stock_data)
        if symbol == 'AAPL': 
            AAPL_equity_curve = Bollinger_Simulation.Bollinger(Capital, symbol, Stock_data, positions)
        elif symbol == 'FB': 
            FB_equity_curve = Bollinger_Simulation.Bollinger(Capital, symbol, Stock_data, positions)
        elif symbol == 'IBM': 
            IBM_equity_curve = Bollinger_Simulation.Bollinger(Capital, symbol, Stock_data, positions)
        elif symbol == 'TSLA': 
            TSLA_equity_curve = Bollinger_Simulation.Bollinger(Capital, symbol, Stock_data, positions)

    Total_equity_curve = []
    for i in range(len(AAPL_equity_curve)):
        Total_equity_curve.append((AAPL_equity_curve[i] + FB_equity_curve[i] + IBM_equity_curve[i] + TSLA_equity_curve[i])/len(positions))
    return Total_equity_curve

"""
Simulate the LongTerm strategy total equity curve. The strategy is in the custom strategies folder. Should run it on a givin dataframe, might need to edit it
a bit so it returns the correct things. Need to run the strategy on multiple stocks, and then calculate the total equity curve.
"""
def simulate_LongTerm(Capital, positions):
    AAPL_equity_curve = []
    FB_equity_curve = []
    IBM_equity_curve = []
    TSLA_equity_curve = []
    Total_equity_curve = []
    
    for symbol in positions:
        Stock_data = accessDB.getStockHistory(symbol)
        Stock_data = format(Stock_data)
        Stock_data = LongTermSetup.long(Stock_data)
        if symbol == 'AAPL': 
            AAPL_equity_curve = LongStrategy.Long(Capital, symbol, Stock_data, positions)
        elif symbol == 'FB': 
            FB_equity_curve = LongStrategy.Long(Capital, symbol, Stock_data, positions)
        elif symbol == 'IBM': 
            IBM_equity_curve = LongStrategy.Long(Capital, symbol, Stock_data, positions)
        elif symbol == 'TSLA': 
            TSLA_equity_curve = LongStrategy.Long(Capital, symbol, Stock_data, positions)

    Total_equity_curve = []
    for i in range(len(AAPL_equity_curve)):
        Total_equity_curve.append((AAPL_equity_curve[i] + FB_equity_curve[i] + IBM_equity_curve[i] + TSLA_equity_curve[i])/len(positions))
    return Total_equity_curve

"""
Sentiment? Can do once we have the data.
"""
def simulate_Sentiment(Capital, positions):
    
    
    return

"""
Calculate each strategy equity curve here, calculate the total equity curve of all strategies, plot all of them. 
"""
def collectTotalEquityCurves():

    Capital_per_strategy = 100000
    positions = {'AAPL': 0, 'FB': 0, 'IBM' : 0, 'TSLA' : 0}
    SMA_equity_curve = simulate_Sma(Capital_per_strategy, positions)

    positions = resetPositions(positions)
    LongTerm_equity_curve = simulate_LongTerm(Capital_per_strategy, positions)

    positions = resetPositions(positions)
    Bollinger_equity_curve = simulate_Bollinger(Capital_per_strategy, positions)

    positions = resetPositions(positions)
    # Sentiment_equity_curve = simulate_Sentiment(Capital_per_strategy)

    total_equity_curve = []

    if(len(SMA_equity_curve) == len(Bollinger_equity_curve)) and (len(SMA_equity_curve) == len(LongTerm_equity_curve)):
        for i in range(0, len(SMA_equity_curve)):
            total_equity_curve.append((SMA_equity_curve[i] + Bollinger_equity_curve[i] + LongTerm_equity_curve[i])/3)
    else:
        print("SMA, Bollinger, and Longterm were not all the same length.")
    
    return SMA_equity_curve, Bollinger_equity_curve, LongTerm_equity_curve, total_equity_curve

def plotAll():
    sma, Bollinger, LongTerm, Total = collectTotalEquityCurves()
    index = getIndex()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x = index, y = sma, name = 'SmaCross Equity Curve',
                                line=dict(color='royalblue'))) 
    fig.add_trace(go.Scatter(x = index, y = Bollinger, name = 'Bollinger Equity Curve',
                                line=dict(color='green'))) 
    fig.add_trace(go.Scatter(x = index, y = LongTerm, name = 'LongTerm Equity Curve',
                                line=dict(color='red'))) 
    fig.add_trace(go.Scatter(x = index, y = Total, name = 'Total Equity Curve',
                                line=dict(color='black', width=3))) 
    fig.update_layout(title='Combining Multiple Strategies',
                   xaxis_title='Date',
                   yaxis_title='Change in Equity(%)')
    #print(WebDisplay.getDjangoPath())
    fig.write_html(WebDisplay.getDjangoPath() + '/multstrategies_norealloc.html')
    #fig.show()

#plotAll()
