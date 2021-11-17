import sys
sys.path.append('../DBMaintenance/')
import accessDB
from Strategies import Strategies

class Positions:
    positions = None
    numPositions = 0
    totalValue = 0
    overPositions = []
    underPositions = []
    newPositions = []
    distribution = 0
    
    def __init__(self):
        self.calculate()
    """
    #close of the last record to represent the position's value
    def getPositionValue(self, symbol):
        #symbol lists for stock and crypto
        stockSymbols = accessDB.getStockSymbols()
        cryptoSymbols = accessDB.getCryptoSymbols()
        if symbol in stockSymbols:
            db = client.stockdb
            positionVal = accessDB.getLatestPrice(db, symbol)
        elif symbol in cryptoSymbols:
            db = db.cryptodb
            positionVal = accessDB.getLatestPrice(db, symbol)
        else:
            print("Something broken in getPositionValue")
        return positionVal
    """
    
    def getPositionValue(self, position):
        value = 0
        if  position['position']:
            value += (position['position'] * accessDB.getLatestPriceBySymbol(position['productType'], position['product']))
        return value
    
    def calculate(self):
        self.positions = accessDB.getPositions()
        self.numPositions = len(self.positions)
        for position in self.positions:
            self.totalValue += self.getPositionValue(position)

    def positionsByStrat(self, strategy):
        positions = []
        for item in self.positions:
            positions.append(item) if item['strategy'] == strategy.value else None
        return positions

    def positionsByMarket(self, market):
        positions = []
        for item in self.positions:
            positions.append(item) if item['market'] == market else None
        return positions

    #this could also get some complicated params for how to update
    def updateAvailableBalance(self, equalAmount):
        accessDB.updatePositions(equalAmount)
    
    #this prolly should be somewhere else.
    #returns the enums of the strats
    def listStrategies(self):
        currStrats = [] 
        for strat in Strategies:
            currStrats.append(strat)
        return currStrats

    
    def generatePositionsDictionary(self):
        #total value
        #position value
        #position target value
        #first, get a list of lists with each combination of market/strategy positions
        strats = self.listStrategies()
        cryptoPositions = {}
        stockPositions = {}
        for item in strats:
            cryptoPositions[item.value] = []
            stockPositions[item.value] = []

        positionsDict = {'crypto': cryptoPositions, 'stock' : stockPositions}
        #this can be accessed using key-value pairs
        #crypto['strategyName'] / stock['strategyName']
        #each element of that array can be accessed as a json element. ex: item['position'], item['product']
        for item in self.positions: 
                if item['productType'] == 'crypto':
                    positionsDict['crypto'][item['strategy']].append(item)
                else:
                    positionsDict['stock'][item['strategy']].append(item)
        return positionsDict

    def generateSpecificPositionsDictionary(self, market, strategy):
        #total value
        #position value
        #position target value
        #first, get a list of lists with each combination of market/strategy positions
        positions = []
        for item in self.generatePositionsDictionary()[market][strategy]:
            item['value'] = []
            if market == 'stock':
                if(item['product'] == 'AAPL'):
                    positions.append(item)
                elif(item['product'] == 'FB'):
                    positions.append(item)
                elif(item['product'] == 'IBM'):
                    positions.append(item)
                elif(item['product'] == 'TSLA'):
                    positions.append(item)
            else:
                if(item['product'] == 'BTC'):
                    positions.append(item)

        return positions

    def backtestReallocate(self, allPositions):
        numMarketStrats = len(allPositions)
        portfolioValue = 0
        numPositions = 0
        # Need the portfolio value so I can even it out among positions
        for marketStrategy in allPositions:
            for position in marketStrategy:
                portfolioValue += position['value'][-1]
                numPositions += 1
        evenMarketStratValue = portfolioValue / numMarketStrats
        numUnderPositions = 0
        #print("portfolio value: ", portfolioValue)
        #print("even market strat val: ", evenMarketStratValue)
        for marketStrategy in allPositions:
            evenPositionValue = evenMarketStratValue / len(marketStrategy)
            for position in marketStrategy:
                if position['value'][-1] >= evenPositionValue:
                    diffValue = position['value'][-1] - evenPositionValue
                    #take money out
                    if position['availableBalance'] < diffValue:
                        #print("Removing: ", position['availableBalance'])
                        self.distribution += position['availableBalance']
                        position['availableBalance'] = 0
                    else:
                        self.distribution += diffValue
                        #print("Removing: ", diffValue)
                        position['availableBalance'] -= diffValue
                else:
                    numUnderPositions += 1
        #this ensures the distribution is capped to the evenPositionValue AND the maxDistributeValue
        # I need both because if there's not enough to go around then I want to be equitable
        for marketStrategy in allPositions:
            evenPositionValue = evenMarketStratValue / len(marketStrategy)
            for position in marketStrategy:
                maxDistributeValue = self.distribution / numUnderPositions
                if position['value'][-1] < evenPositionValue:
                    diff = evenPositionValue - position['value'][-1]
                    if diff <= maxDistributeValue:
                        self.distribution -= diff
                        position['availableBalance'] += diff
                    else:
                        self.distribution -= maxDistributeValue
                        position['availableBalance'] += maxDistributeValue
                    numUnderPositions -= 1
        if (self.distribution > 0):
            extra = self.distribution / numPositions
            for marketStrategy in allPositions:
                for position in marketStrategy:
                    self.distribution -= extra
                    position['availableBalance'] += extra
        return allPositions
    
    def distributeAmongMarketStrategy(self, marketType, strategy, stratValue, positions):
        #calculate the strategy value for this market/strat pair
        #print("current positions: ", positions[marketType][strategy])
        target_position_value = stratValue / len(positions[marketType][strategy])
        #print(marketType,"/", strategy, " target value: ", target_position_value, " numPositions: ", len(positions[marketType][strategy]))

        underPositions = []
        underPositionsTotal = 0
        overPositionsTotal = 0
        for position in positions[marketType][strategy]:
            #get the position value if we sold right now
            positionVal = self.getPositionValue(position)
            totalVal = positionVal + position['availableBalance']
            diffValue = totalVal - target_position_value
            # check over value or correct value
            if diffValue >= 0:
                #print(position['product'], " over valued: ", totalVal, "by: ", diffValue)
                #see how much to take
                if position['availableBalance'] < diffValue:
                    #print("Removing: ", position['availableBalance'])
                    self.distribution += position['availableBalance']
                    position['availableBalance'] = 0
                else:
                    excessBalance = position['availableBalance'] - diffValue
                    self.distribution += diffValue
                    #print("Removing: ", diffValue)
                    position['availableBalance'] -= diffValue
                overPositionsTotal += target_position_value
            else:
                underPositions.append(position['product'])
                underPositionsTotal += totalVal
                                      
        #print("Left overs to distribute", self.distribution)
        #print("Strategy value: ", stratValue, " numUnderValued: ", len(underPositions))
        if (self.distribution > 0):
            #how much to give to each position, based on the strategy value and under positions
            strategyUnderValue = stratValue - (overPositionsTotal + underPositionsTotal)
            equalAmounts = strategyUnderValue / len(underPositions)
            if (self.distribution < strategyUnderValue):
                equalAmounts = self.distribution / len(underPositions)
            #redistribute among the strategy
            for position in positions[marketType][strategy]:
                if position['product'] in underPositions:
                    position['availableBalance'] += equalAmounts
                    self.distribution -= equalAmounts

        print("New positions: ", positions[marketType][strategy])
        for position in positions[marketType][strategy]:
            accessDB.updatePositionByStrategy(position)
        
    # def reallocate(self, stockPercentage, cryptoPercentage):
    def reallocate(self, allPositions, stockPercentage, cryptoPercentage):
        positions = allPositions
        #positions_even_value = self.totalValue / self.numPositions
        #must disallocate before allocating!
        stock_value = self.totalValue * stockPercentage
        crypto_value = self.totalValue * cryptoPercentage
        stock_strat_value = stock_value / len(self.listStrategies())
        crypto_strat_value = crypto_value / len(self.listStrategies())
        #print(positions)
        #for each strategy, do this
        for strategy in self.listStrategies():
            print("Market Value: ", stock_value)
            self.distributeAmongMarketStrategy('stock', strategy.value, stock_strat_value, positions)
            print("Market Value: ", crypto_value)
            self.distributeAmongMarketStrategy('crypto', strategy.value, crypto_strat_value, positions)
        return positions
        
