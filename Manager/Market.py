"""
This will allocate money into each strategy with the money allocated to the Stock Market portfolio
"""
import HelperFunctions as Help

# return the total cash of all strategies in a given market (Stock or crypto)
def TotalCash(Market):
    strategies = Help.getStrategies(Market)
    total_cash = 0
    for i in range(len(strategies)):
        positions = Help.getPositions(Market, strategies[i])
        total_cash += Help.calc_Total_Cash(positions)
    return total_cash

# return the total available cash of all strategies in a given market (Stock or Crypto)
def AvailableCash(Market):
    strategies = Help.getStrategies(Market)
    available_cash = 0
    for i in range(len(strategies)):
        positions = Help.getPositions(Market, strategies[i])
        available_cash += Help.calc_Total_Available(positions)
    return available_cash

# return the value of each strategy in a given market (Stock or Crypto)
def Value_Per_Strategy(Market):
    strategies = Help.getStrategies(Market)
    value_per_str = []
    for i in range(len(strategies)):
        positions = Help.getPositions(Market, strategies[i])
        strategy_total = Help.calc_Total_Cash(positions)
        value_per_str.append(strategy_total)
    return value_per_str

# return the available cash of each strategy in a given market (Stock or Crypto)
def Available_Per_Strategy(Market):
    strategies = Help.getStrategies(Market)
    available_per_str = []
    for i in range(len(strategies)):
        positions = Help.getPositions(Market, strategies[i])
        strategy_available = Help.calc_Total_Available(positions)
        available_per_str.append(strategy_available)
    return available_per_str

print("                     TOTAL CASH STOCK MARKET: ", TotalCash('Stock'))
print("                 AVAILABLE CASH STOCK MARKET: ", AvailableCash('Stock'))
print("             VALUE PER STRATEGY STOCK MARKET: ", Value_Per_Strategy('Stock'))
print("    AVAILABLE CASH PER STRATEGY STOCK MARKET: ", Available_Per_Strategy('Stock'))




