"""
This pulls the sentiment data on a given day from the database.
Average the points. 3 class variables.
1. Objectivity: How accurate a point needs to be to be considered.
2. BuySentiment: Value of the sentiment to signal a BUY
3. SellSentiment: Value of the sentiment to signal a SELL
"""

import HelperFunctions as Help


"""
positions = Help.getPositions('stock', 'Sentiment')
print("Sentiment")
print("Total Cash: ", Help.calc_Total_Cash(positions))
print("Total Value per stock: ", Help.calc_value_per_position(positions))
print("Total Available Cash: ", Help.calc_Total_Available(positions))
print("Current Target Cash per stock: ", Help.Cash_Per_Stock())
print("Positions: ", positions)
print("Available Cash for each Position: ", Help.calc_available_per_posistion(positions))
"""

