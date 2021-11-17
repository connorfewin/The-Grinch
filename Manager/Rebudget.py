"""
If it is the first day of the month, our portfolio will go through a reallocation process.
This is to limit risk. Reallocates Stock Market vs Crypto, then each strategy in each, 
and then the money each stock has within the strategy.
"""
#import HelperFunctions as Help
#import Portfolio
from Positions import Positions
positions = Positions()

def updateBudget():
    """
    market = Help.getMarkets()
    strategy = []
    positions = []
    for i in range(len(market)):
        strategy = Help.getStrategies(market[i])
        for j in range(len(strategy)):
            positions = Help.getPositions(market[i], strategy[j])
            Help.updateDB(market[i], strategy[j], positions)
    """
    #I don't know what this does.
    print('updateBudget?')

def reallocate():
    """
    updateBudget()  # first things first, want to make sure the DB is current.
    market = Help.getMarkets()
    strategy = []
    positions = []
    portfolio_value = Portfolio.TotalCash()
    portfolio_available = Portfolio.AvailableCash()
    market_target_value = portfolio_value / len(market)
    temp = 0

    market_stop = (len(market) * 2) - 1
    for i in range(market_stop):
        last = market_stop - 1
        if i > last / 2: market_index = last - i 
        else: market_index = i

        strategy = Help.getStrategies(market[market_index])
        strategy_target_value = market_target_value / len(strategy)

        strategy_stop = (len(strategy) * 2) - 1
        for j in range(strategy_stop):
            last = len(strategy) - 1
            if i > last / 2: strategy_index = last - i
            else: strategy_index = i

            positions = Help.getPositions(market[market_index], strategy[strategy_index])
            positions, temp = Help.Reallocate(positions, strategy_target_value, temp)
            Help.updateDB(market[market_index], strategy[strategy_index], positions)
    """
    print(positions.totalValue)
    print(positions.getPositionsArray("crypto", Strategies.LONG_TERM.value))
    
