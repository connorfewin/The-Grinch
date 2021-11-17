import sys
import pandas as pd
import math
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import WebDisplay

sys.path.append('../DBMaintenance/')
import accessDB



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

def updateValue(symbol, positions, row, available_cash):
    value = 0
    if positions[symbol]:
        value = row['close'] * positions[symbol] + available_cash
    else:
        value = available_cash
    return value
"""
Run Stock_data through simulation
"""
def simulate(capital, symbol, Stock_data, positions):
    CAPITAL = capital
    available_cash = CAPITAL
    initial_value = CAPITAL
    Stock_equity_curve = []
    stock_value = []
    for index, row in Stock_data.iterrows():
        if positions[symbol]:
            Stock_equity_curve, CAPITAL, available_cash = updateEquityCurve(Stock_equity_curve, symbol, positions, row, CAPITAL, available_cash, initial_value)
            stock_value.append(updateValue(symbol, positions, row, available_cash))
        else:
            if not len(Stock_equity_curve) == 0:
                Stock_equity_curve.append(Stock_equity_curve[-1])
                stock_value.append(stock_value[-1])
            else:
                Stock_equity_curve.append(0)
                stock_value.append(available_cash)

        if not positions[symbol]:
            if row['SMA(9)'] > row['SMA(27)']:
                #print("buy @", row['close'], " data: ", index)
                positions, available_cash = buy(symbol, positions, CAPITAL, available_cash, row)
        elif positions[symbol]:
            if row['SMA(9)'] < row['SMA(27)']:
                #print("sell @", row['close'], " date: ", index)
                positions, available_cash = sell(symbol, positions, available_cash, row)
    return Stock_equity_curve

def buy_and_hold(stock_data):
    stock_equity = []
    stock_value = []
    initial_value = stock_data['close'].iloc[0]
    for index, row in stock_data.iterrows():
        if(len(stock_equity) == 0): 
            stock_equity.append(0)
        else:
            equity_change = ((row['close']/initial_value) * 100) - 100
            stock_equity.append(equity_change)

    return stock_equity
    


def run():
    positions = {'AAPL': 0, 'FB': 0, 'IBM' : 0, 'TSLA' : 0}
    Capital = 100000
    symbol = 'AAPL'
    AAPL_data = accessDB.getStockHistory('AAPL')
    AAPL_data = formatDataFrames(AAPL_data)
    AAPL_buy_and_hold = buy_and_hold(AAPL_data)
    AAPL_equity_curve = simulate(Capital, symbol, AAPL_data, positions)

    positions = {'AAPL': 0, 'FB': 0, 'IBM' : 0, 'TSLA' : 0}
    Capital = 100000
    symbol = 'FB'
    FB_data = accessDB.getStockHistory('FB')
    FB_data = formatDataFrames(FB_data)
    FB_buy_and_hold = buy_and_hold(FB_data)
    FB_equity_curve = simulate(Capital, symbol, FB_data, positions)

    positions = {'AAPL': 0, 'FB': 0, 'IBM' : 0, 'TSLA' : 0}
    Capital = 100000
    symbol = 'IBM'
    IBM_data = accessDB.getStockHistory('IBM')
    IBM_data = formatDataFrames(IBM_data)
    IBM_buy_and_hold = buy_and_hold(IBM_data)
    IBM_equity_curve = simulate(Capital, symbol, IBM_data, positions)

    positions = {'AAPL': 0, 'FB': 0, 'IBM' : 0, 'TSLA' : 0}
    Capital = 100000
    symbol = 'TSLA'
    TSLA_data = accessDB.getStockHistory('TSLA')
    TSLA_data = formatDataFrames(TSLA_data)
    TSLA_buy_and_hold = buy_and_hold(TSLA_data)
    TSLA_equity_curve = simulate(Capital, symbol, TSLA_data, positions)

    

    """
    combine the two and plot
    """
    Total_equity_curve = []
    Total_buy_and_hold = []
    for i in range(len(AAPL_equity_curve)):
        Total_equity_curve.append((AAPL_equity_curve[i] + FB_equity_curve[i] + IBM_equity_curve[i] + TSLA_equity_curve[i])/len(positions))
        Total_buy_and_hold.append((AAPL_buy_and_hold[i] + FB_buy_and_hold[i] + IBM_buy_and_hold[i] + TSLA_buy_and_hold[i])/len(positions))
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x = AAPL_data.index, y = AAPL_equity_curve, name = 'AAPL Equity Curve',
                                line=dict(color='royalblue')))                                             
    fig.add_trace(go.Scatter(x = AAPL_data.index, y = AAPL_buy_and_hold, name = 'AAPL Buy and Hold',
                                line=dict(color='royalblue', width=1, dash='dot')))
    fig.add_trace(go.Scatter(x = FB_data.index, y = FB_equity_curve, name = 'FB Equity Curve',
                                line=dict(color='green')))                                             
    fig.add_trace(go.Scatter(x = FB_data.index, y = FB_buy_and_hold, name = 'FB Buy and Hold',
                                line=dict(color='green', width=1, dash='dot')))
    fig.add_trace(go.Scatter(x = IBM_data.index, y = IBM_equity_curve, name = 'IBM Equity Curve',
                                line=dict(color='firebrick')))                                             
    fig.add_trace(go.Scatter(x = IBM_data.index, y = IBM_buy_and_hold, name = 'IBM Buy and Hold',
                                line=dict(color='firebrick', width=1, dash='dot')))
    fig.add_trace(go.Scatter(x = TSLA_data.index, y = TSLA_equity_curve, name = 'TSLA Equity Curve',
                                line=dict(color='gray')))                                             
    fig.add_trace(go.Scatter(x = TSLA_data.index, y = TSLA_buy_and_hold, name = 'TSLA Buy and Hold',
                                line=dict(color='gray', width=1, dash='dot')))
    fig.add_trace(go.Scatter(x = AAPL_data.index, y = Total_equity_curve, name = 'Total Equity Curve',
                                line=dict(color='black', width=3)))        
    fig.update_layout(title='Multiple Securities Using the Sma Cross Strategy',
                   xaxis_title='Date',
                   yaxis_title='Change in Equity(%)')                                     
                                
    fig.write_html(WebDisplay.getDjangoPath() + '/multstocks_norealloc.html')
    #fig.show()


run()

