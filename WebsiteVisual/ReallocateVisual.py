import sys
sys.path.append('../DBMaintenance/')
import accessDB
sys.path.append('../Manager/')
from Strategies import Strategies
from Positions import Positions
import pandas as pd
import math
import matplotlib.pyplot as plt
sys.path.append('../CustomStrategies/')
from LongTermSetup import long
import Bollinger_Simulation
import LongStrategy
import WebDisplay
from MultMarkets import theBigShabang

sys.path.append('../BackTest/')
from toDataFrame import toPandas as format

import plotly.express as px
import plotly.graph_objects as go

#Look at the table for more details.
positions = Positions()

# you can get all positions with a certain strategy by passing the ENUM to this
# positionsByStrat(stratEnum) ex: LONG_TERM see Manager/Strategies.py
# or all strategies/markets can be accessed using positions.positions (positions is an attribute holding them all)
# I can easily make a subset of positions see Manager/Positions.py for more details.
# example:     stock_positions = positions.positionsByMarket('stock')

# this could hold ALL of the columns we need for each strategy? see appendTechnicals
def getStockDataFrame(symbol):
    data = accessDB.getStockHistory(symbol)
    Stock_data = pd.DataFrame(data)
    Stock_data['datetime'] = pd.to_datetime(Stock_data['datetime'], unit='ms')
    Stock_data['datetime'] = Stock_data['datetime'].dt.date
    Stock_data = pd.DataFrame.drop(Stock_data, labels='_id', axis=1)
    Stock_data.index = Stock_data['datetime']
    Stock_data = pd.DataFrame.drop(Stock_data, labels='datetime', axis=1)
    Stock_data = appendTechnicals(Stock_data)
    return Stock_data

def getCryptoDataFrame(symbol):
    data = accessDB.getCryptoHistory(symbol, '1D')
    data = pd.DataFrame(data)
    data['datetime'] = pd.to_datetime(data['datetime'], unit='s')
    data['datetime'] = data['datetime'].dt.date
    data = pd.DataFrame.drop(data, labels='_id', axis=1)
    data.index = data['datetime']
    data = pd.DataFrame.drop(data, labels='datetime', axis=1)
    data = appendTechnicals(data)
    return data

#Could we combine these things?
def appendTechnicals(Stock_data):
    Stock_data['SMA(9)'] = Stock_data.iloc[:,1].rolling(window=9).mean()
    Stock_data['SMA(27)'] = Stock_data.iloc[:,1].rolling(window=27).mean()
    Stock_data['std'] = Stock_data['close'].rolling(20).std(ddof=0)
    Stock_data['MA-TP'] = Stock_data['close'].rolling(20).mean()
    Stock_data['BOLU'] = Stock_data['MA-TP'] + 2*Stock_data['std']
    Stock_data['BOLD'] = Stock_data['MA-TP'] - 2*Stock_data['std']
    Stock_data = pd.DataFrame.drop(Stock_data, labels='std', axis=1)
    Stock_data = pd.DataFrame.drop(Stock_data, labels='MA-TP', axis=1)
    Stock_data = long(Stock_data)
    # Add custom column from long term strategy:

    return Stock_data

def buy(positions, row):
    num_shares = math.floor(positions['availableBalance']/row['close'])
    positions['position'] = num_shares
    positions['availableBalance'] = positions['availableBalance'] - (num_shares * row['close'])
    return positions

def sell(positions, row):
    positions['availableBalance'] += row['close'] * positions['position']
    positions['position'] = 0
    return positions

def updateValue(position):
    positionEquity = 0
    if position['position']:
        positionEquity = (position['position'] * position['buyPrices']) + position['availableBalance']
    else:
        positionEquity = position['availableBalance']

    return positionEquity

def calculateEquityCurve(allPositions):
    totalEquityCurve = []
    totalValueList = []
    for i in range(len(allPositions[0][0]['value'])):
        dayValue = 0
        for strat in allPositions:
            stratValue = 0
            for position in strat:
                stratValue += position['value'][i]
            dayValue += stratValue
        if(len(totalEquityCurve) != 0):
            #print(dayValue)
            totalEquityCurve.append(((dayValue - totalValueList[0])/totalValueList[0]) * 100)
        else:
            totalEquityCurve.append(0)
        totalValueList.append(dayValue)
    return totalEquityCurve

def calculateStockEquityCurve(allPositions):
    stockEquityCurve = {}
    stockValueDict = {}
    productList = []
    for marketStrategy in allPositions:
        for position in marketStrategy:
            if position['product'] not in productList:
                productList.append(position['product'])
    #initialize a dictionary of values for the stock! The stock symbol is the keyyyyy to the value list 
    for item in productList:
        stockValueDict[item] = []
        stockEquityCurve[item] = []
    for i in range(len(allPositions[0][0]['value'])):
        for item in productList:
            stockValueDict[item].append(0)
        for marketStrategy in allPositions:
            for position in marketStrategy:
                stockValueDict[position['product']][i] += position['value'][i]
        for item in productList:
            if len(stockValueDict[item]) >= 2:
                stockEquityCurve[item].append(((stockValueDict[item][i] - stockValueDict[item][0])/ stockValueDict[item][0]) * 100)
            else:
                stockEquityCurve[item].append(0)
    #print(stockEquityCurve)
    return stockEquityCurve

def getTotalIndex(stockIndex, cryptoIndex):
    totalIndex = []
    i = 0
    j = 0
    while i < len(stockIndex) - 1 or j < len(cryptoIndex) - 1:
        if stockIndex[i] < cryptoIndex[j]:
            totalIndex.append(stockIndex[i])
            i+=1
        elif stockIndex[i] > cryptoIndex[j]:
            totalIndex.append(cryptoIndex[j])
            j+=1
        else:
            totalIndex.append(stockIndex[i])
            i+=1
            j+=1
    return totalIndex

"""
Returns the index of the specific positions
"""
def getSpecificPositions(allPositions, market, strat):
    for item in allPositions:
        #print(item[0]['productType'], " ", item[0]['strategy'], " ", market, " ", strat)
        if item[0]['productType'] == market and item[0]['strategy'] == strat:
            return allPositions.index(item)
    return None
    

def simulate():
    # Get the different positions that we wanna work on
    # allPositions is a list of lists, those lists have dictionary elements that represent rows in the db.
    allPositions = []
    symbols = ['AAPL', 'FB', 'IBM', 'TSLA', 'BTC-USD']
    for strat in Strategies:
        allPositions.append(positions.generateSpecificPositionsDictionary('stock', strat.value))
        allPositions.append(positions.generateSpecificPositionsDictionary('crypto', strat.value))
    # We want to simulate for the symbols, markets, strats in allPositions at the same time so that it will rebalance
    # rebudget after 30 trading days
    #Make sure the dataframes 
    AAPL_Data = getStockDataFrame('AAPL')
    FB_Data = getStockDataFrame('FB')
    IBM_Data = getStockDataFrame('IBM')
    TSLA_Data = getStockDataFrame('TSLA')
    BTC_Data = getCryptoDataFrame('BTC-USD')
    #I made this to reduce if statements in the for loops!
    allData = [AAPL_Data, FB_Data, IBM_Data, TSLA_Data, BTC_Data]
    allDataIndex = ['AAPL', 'FB', 'IBM', 'TSLA', 'BTC']
    stockIndexCount = 0
    stockIndex = AAPL_Data.index
    cryptoIndexCount = 0
    cryptoIndex = BTC_Data.index
    allDates = getTotalIndex(stockIndex, cryptoIndex)

    totalEquityCurve = []
    count = 0

    specificPositions = {}
    markets = ['stock', 'crypto']
    #assign initial available balance
    for market in markets:
            for strat in Strategies:
                capitalPerStrategy = 100000
                index = getSpecificPositions(allPositions, market, strat.value)
                specificPositions = allPositions[index]
                for position in specificPositions:
                    position['availableBalance'] = capitalPerStrategy/len(specificPositions)

    for date in allDates:
        #This iterates through every date that could have data.
        if count == 30:
            allPositions = positions.backtestReallocate(allPositions)
            count = 0
        for market in markets:
            marketEquity = []
            for strat in Strategies:
                stratEquity = []
                # I actually return the index here of the matching position list. this is to use the same object
                # we can edit specific positions and it will transfer to allPositions.
                index = getSpecificPositions(allPositions, market, strat.value)
                specificPositions = allPositions[index]
                dfCount = 0
                for position in specificPositions:
                    # no if statements this way/
                    dfIndex = allDataIndex.index(position['product'])
                    df = allData[dfIndex]
                    if market=='stock' and date==stockIndex[stockIndexCount]:
                        """
                        print()
                        print(market)
                        print(strat)
                        print(position)
                        print(df.loc[date])
                        """
                        row = df.loc[date]
                        if strat.value == 'SMA_CROSS':
                            if position['position'] != 0 and row['SMA(9)'] > row['SMA(27)']:
                                position = buy(position, row)
                            elif position['position'] == 0 and row['SMA(9)'] < row['SMA(27)']:
                                position = sell(position, row)
                        elif strat.value == 'BBANDS':
                            if position['position'] == 0 and row['close'] < row['BOLD']:
                                position = buy(position, row)
                            elif position['position'] != 0 and row['close'] > row['BOLU']:
                                position = sell(position, row)
                        elif strat.value == 'LONG_TERM':
                            if position['position'] == 0 and row['custom'] < 0.9:
                                position = buy(position, row)
                            elif position['position'] != 0 and row['custom'] > 0.9:
                                position = sell(position, row)
                        position['buyPrices'] = row['close']

                    elif market=='crypto' and date==cryptoIndex[cryptoIndexCount]:
                        """
                        print()
                        print(market)
                        print(strat)
                        print(position)
                        print(df.loc[date])
                        """
                        row = df.loc[date]
                        if strat.value == 'SMA_CROSS':
                            if position['position'] == 0 and row['SMA(9)'] > row['SMA(27)']:
                                position = buy(position, row)
                            elif position['position'] != 0 and row['SMA(9)'] < row['SMA(27)']:
                                position = sell(position, row)
                        elif strat.value == 'BBANDS':
                            if position['position'] == 0 and row['close'] < row['BOLD']:
                                position = buy(position, row)
                            elif position['position'] != 0 and row['close'] > row['BOLU']:
                                position = sell(position, row)
                        elif strat.value == 'LONG_TERM':
                            if position['position'] == 0 and row['custom'] < 0.9:
                                position = buy(position, row)
                            elif position['position'] != 0 and row['custom'] > 0.9:
                                position = sell(position, row)
                        position['buyPrices'] = row['close']
                        
                    position['value'].append(updateValue(position))
                    
        if date == stockIndex[stockIndexCount] and stockIndexCount < len(stockIndex):
            stockIndexCount += 1
        if date == cryptoIndex[cryptoIndexCount] and cryptoIndexCount < len(cryptoIndex):
            cryptoIndexCount += 1
        
        count+=1
    """
    totalEquityCurve = calculateEquityCurve(allPositions)
    return totalEquityCurve
    """
    return allPositions, allDates

def plotTotalEquityCurve(allPositions, dates):
    totalEquity = calculateEquityCurve(allPositions)
    withoutReallocate, index = theBigShabang()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x = index, y = totalEquity, name = 'Total Equity with a monthly reallocation',
                                line=dict(color='royalblue'))) 
    fig.add_trace(go.Scatter(x = index, y = withoutReallocate, name = 'Total Equity without a monthly reallocation',
                                line=dict(color='red')))
    fig.update_layout(title='Total Equity',
                   xaxis_title='Date',
                   yaxis_title='Change in Equity(%)')
    fig.write_html(WebDisplay.getDjangoPath() + '/totalequity.html')

def plotStockEquityCurve(allPositions, dates):
    stockEquity = calculateStockEquityCurve(allPositions)
    AAPL_curve = []
    FB_curve = []
    IBM_curve = []
    TSLA_curve = []
    BTC_curve = []
    for item in stockEquity.items():
        if item[0] == 'AAPL': AAPL_curve = item[1]
        elif item[0] == 'FB': FB_curve = item[1]
        elif item[0] == 'IBM': IBM_curve = item[1]
        elif item[0] == 'TSLA': TSLA_curve = item[1]
        elif item[0] == 'BTC': BTC_curve = item[1]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x = dates, y = AAPL_curve, name = 'AAPL with a monthly reallocation',
                                line=dict(color='royalblue'))) 
    fig.add_trace(go.Scatter(x = dates, y = FB_curve, name = 'FB without a monthly reallocation',
                                line=dict(color='red'))) 
    fig.add_trace(go.Scatter(x = dates, y = IBM_curve, name = 'IBM with a monthly reallocation',
                                line=dict(color='green'))) 
    fig.add_trace(go.Scatter(x = dates, y = TSLA_curve, name = 'TSLA without a monthly reallocation',
                                line=dict(color='gray'))) 
    fig.add_trace(go.Scatter(x = dates, y = BTC_curve, name = 'BTC without a monthly reallocation',
                                line=dict(color='purple')))
    fig.update_layout(title='Stock Performance with Reallocation',
                   xaxis_title='Date',
                   yaxis_title='Change in Equity(%)')
    fig.write_html(WebDisplay.getDjangoPath() + '/multstocks.html')

def plotMarketEquityCurve():
    fig = go.Figure()
    fig.write_html(WebDisplay.getDjangoPath() + '/multmarkets.html')
    return

def plotStrategyEquityCurve():
    fig = go.Figure()
    fig.write_html(WebDisplay.getDjangoPath() + '/multstrategies.html')
    return

allPositions, dates = simulate()
#plotTotalEquityCurve(allPositions, dates)
plotStockEquityCurve(allPositions, dates)
plotTotalEquityCurve(allPositions, dates)
