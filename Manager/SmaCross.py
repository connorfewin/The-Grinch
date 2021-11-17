"""
This will take two SMA Lines of different lengths. 
When the smaller one crosses above the long: BUY
When the smaller one corsses below the long: SELL
"""
"""
The database needs a section for each strategy in each market that
Stocks, how many shares owned in each stock, cash per stock calculated
during most recent rebudget session, target cash per stock (based on even
allocation). Order history (for now just on shares being held - what was the price when bought)
"""
"""
Return Total_Value of this strategy and the available cash for this strategy
"""
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
    positions = [['AAPL', 0], ['TSLA', 0], ['ROKU', 3]]
    return positions


def price_when_bought():
    return 330

def get_current_price():
    return 345

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

def update():
    positions = getPositions()
    for i in range(len(positions)):
        data = 0
        Sma1, Sma2 = CalculateNewSma(data)
        if not hasPositions(positions, i):
            if Sma1 > Sma2: Buy()
        else:
            if Sma1 < Sma2: Sell()
"""

def update(positions):
    print('calculating new SMA positions')
    #this is where we would do internal calculations and assign new values.
"""
TOTAL_CASH, AVAILABLE_CASH, AVAILABLE_EACH_POSITION = get_Total_Cash()
Target_Cash_Per_Stock = get_Cash_Per_Stock() 
Positions = getPositions()
update()
print("SMA CROSS")
print("Total Cash: ", TOTAL_CASH)
print("Total Available Cash: ", AVAILABLE_CASH)
print("Target Cash per stock: ", Target_Cash_Per_Stock)
print("Positions: ", Positions)
print("Available Cash for each Position: ", AVAILABLE_EACH_POSITION)
"""
