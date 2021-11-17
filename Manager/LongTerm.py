"""
This is the long term strategy. It creates a line of best fit amongst all the bottoms of a given stock,
and increases the position if it dips below said line. The idea is not to have a sell indicator, this
is someting that is continueously added to over time, but if we include a function to take profit when 
available, the sell indicator will be a best fit line of local max points.
"""
"""
Return Total_Value of this strategy and the available cash for this strategy
"""
import sys
sys.path.append('../DBMaintenance/')
import accessDB

def get_Total_Cash():
    positions = getPositions()
    cash_per_stock = get_Cash_Per_Stock()
    total_cash = 0
    available_cash = 0
    available_per_position = []
    for i in range(len(positions)):
        shares = positions[i][1]
        if shares == 0: 
            total_cash += cash_per_stock
            available_cash += cash_per_stock
            available_per_position.append(cash_per_stock)

        else:
            value_when_bought = shares * price_when_bought()
            stock_available = cash_per_stock - value_when_bought
            holdings_current_value = get_current_price() * shares
            total_cash += (holdings_current_value + stock_available)
            available_cash += stock_available
            available_per_position.append(stock_available)
    return total_cash, available_cash, available_per_position

"""
Get this data from the database, for now I'll create an example
"""
def get_Cash_Per_Stock():
    cash_per_stock = 1000
    return cash_per_stock

"""
Get this data from the database, for now I'll create an example
"""
def getPositions():
    positions = [['SPTM', 19], ['QQQ', 0], ['BX', 0]]
    accessDB.getStockSymbols()
    return positions


def price_when_bought():
    return 52

def get_current_price():
    return 56

def CalculateNewSma(data):
    return 1, 0

def hasPositions(positions, i):
    if positions[i][0] == 0:
        return False
    else: return True

"""
Possible parameters: positions, position index
"""
def Buy():
    print("Buy")
def Sell():
    print("Sell")

"""
Once the data has been updated, it goes through each symbol or the strategy and calculates new SMA values, and then
determines whether to buy or sell.
"""
def update():
    positions = getPositions()
    for i in range(len(positions)):
        data = 0
        Sma1, Sma2 = CalculateNewSma(data)
        if not hasPositions(positions, i):
            if Sma1 > Sma2: Buy()
        else:
            if Sma1 < Sma2: Sell()

getPositions()

















TOTAL_CASH, AVAILABLE_CASH, AVAILABLE_EACH_POSITION = get_Total_Cash()
Target_Cash_Per_Stock = get_Cash_Per_Stock() 
Positions = getPositions()
update()
print("LONG")
print("Total Cash: ", TOTAL_CASH)
print("Total Available Cash: ", AVAILABLE_CASH)
print("Target Cash per stock: ", Target_Cash_Per_Stock)
print("Positions: ", Positions)
print("Available Cash for each Position: ", AVAILABLE_EACH_POSITION)

