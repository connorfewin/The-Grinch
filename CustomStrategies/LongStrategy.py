import math
import pandas as pd


def formatDataFrames(Stock_data):

    Stock_data = pd.DataFrame(Stock_data)
    

    
    Stock_data['datetime'] = pd.to_datetime(Stock_data['datetime'], unit='ms')
    Stock_data['datetime'] = Stock_data['datetime'].dt.date
    

    Stock_data = pd.DataFrame.drop(Stock_data, labels='_id', axis=1)

    Stock_data.index = Stock_data['datetime']

    Stock_data = pd.DataFrame.drop(Stock_data, labels='datetime', axis=1)

    Stock_data['std'] = Stock_data['close'].rolling(20).std(ddof=0)
    Stock_data['MA-TP'] = Stock_data['close'].rolling(20).mean()
    Stock_data['BOLU'] = Stock_data['MA-TP'] + 2*Stock_data['std']
    Stock_data['BOLD'] = Stock_data['MA-TP'] - 2*Stock_data['std']

    Stock_data = pd.DataFrame.drop(Stock_data, labels='std', axis=1)
    Stock_data = pd.DataFrame.drop(Stock_data, labels='MA-TP', axis=1)

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
    capital = (positions[symbol] * row['close']) + available_cash
    equity_curve.append(((capital/initial_value) * 100) - 100)
    
    return equity_curve, capital, available_cash



def Long(capital, symbol, Stock_data, positions):
    CAPITAL = capital
    available_cash = CAPITAL
    initial_value = CAPITAL
    Stock_equity_curve = []
    for index, row in Stock_data.iterrows():
        if positions[symbol]:
            Stock_equity_curve, CAPITAL, available_cash = updateEquityCurve(Stock_equity_curve, symbol, positions, row, CAPITAL, available_cash, initial_value)
        else:
            if not len(Stock_equity_curve) == 0:
                #repeat the last entry
                Stock_equity_curve.append(Stock_equity_curve[-1])
            else:
                Stock_equity_curve.append(0)

        if not positions[symbol]:
            if row['custom'] == -1:
                #print("buy @", row['close'], " data: ", index)
                positions, available_cash = buy(symbol, positions, CAPITAL, available_cash, row)
        elif positions[symbol]:
            if row['custom'] == 1:
                #print("sell @", row['close'], " date: ", index)
                positions, available_cash = sell(symbol, positions, available_cash, row)
    return Stock_equity_curve