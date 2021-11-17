"""
This strategy takes the bollinger bands of a stock.
When the price is below the bottom band: BUY
When the price is below the top band: SELL
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
import HelperFunctions as Help

"""
positions = Help.getPositions('stock', 'Sma_Cross')
print("BOLLINGER BANDS")
print("Total Cash: ", Help.calc_Total_Cash(positions))
print("Total Value per stock: ", Help.calc_value_per_position(positions))
print("Total Available Cash: ", Help.calc_Total_Available(positions))
print("Current Target Cash per stock: ", Help.Cash_Per_Stock())
print("Positions: ", positions)
print("Available Cash for each Position: ", Help.calc_available_per_posistion(positions))
"""