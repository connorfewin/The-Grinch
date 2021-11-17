"""
This will allocate the budget into each market (Stock or Crypto)
"""
from Positions import Positions
from Strategies import Strategies
currPositions = Positions()
import SmaCross

#print(Strategies.LONG_TERM.value)
def update():
    currPositions.reallocate(.5,.5)

update()
