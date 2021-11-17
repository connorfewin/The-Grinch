"""
These funcitons are used for each strategy in each market, I will pass it the market, and the symbol,
Pull from the data base here, apply it everywhere else.
"""

def calc_Total_Cash(positions):
    total_cash = 0
    for i in range(len(positions)):
        shares = positions[i][1]
        symbol = positions[i][0]
        total_cash += (shares * get_current_price(symbol)) + (Cash_Per_Stock() - (shares * price_when_bought(symbol)))
    return total_cash

def calc_Total_Available(positions):
    available_cash = 0
    for i in range(len(positions)):
        shares = positions[i][1]
        symbol = positions[i][0]
        available_cash += Cash_Per_Stock() - (shares * price_when_bought(symbol))
    return available_cash

# Gets the current value of every holding, return in an array
# @param positions: paired list of [[symbol, #of shares]]
def calc_value_per_position(positions):
    current_value_per_position = []
    for i in range(len(positions)):
        shares = positions[i][1]
        symbol = positions[i][0]
        total = (shares * get_current_price(symbol))
        available = (Cash_Per_Stock() - (shares * price_when_bought(symbol)))
        current_value_per_position.append(total + available)
    return current_value_per_position

# Gets the current available cash for every holding, return in an array
# @param positions: paired list of [[symbol, #of shares]]
def calc_available_per_posistion(positions):
    available_per_position = []
    for i in range(len(positions)):
        shares = positions[i][1]
        symbol = positions[i][0]
        available_cash = Cash_Per_Stock() - (shares * price_when_bought(symbol))
        available_per_position.append(available_cash)
    return available_per_position

"""
Get this data from the database, for now I'll create an example
"""
def Cash_Per_Stock():
    cash_per_stock = 1000
    return cash_per_stock

def getPositions(Market, Strategy):
    positions = [['AAPL', 0], ['TSLA', 0], ['ROKU', 3]]
    return positions

def getStrategies(Market):
    if Market == 'Stock':
        return ['LongTerm', 'SmaCross', 'BollingerBands', 'Sentiment']
    else:
        return ['SmaCross', 'BollingerBands', 'Sentiment']

def getMarkets():
    Markets = ['Stock', 'Crypto']
    return Markets

def price_when_bought(symbol):
    return 330

def get_current_price(symbol):
    return 345

def updateDB(market, strategy, positions):
    # update the DB from here, the rebudget class will call this.
    print("updating DB with", market, "market", strategy, "data...")
    Total_Cash = calc_Total_Cash(positions)
    Value_per_position = calc_value_per_position(positions)
    available_cash = calc_Total_Available(positions)
    Available_per_stock = calc_available_per_posistion(positions)
    print("Update Complete.")



def Reallocate(positions, strategy_target_value, temp):
    total_value = calc_Total_Cash(positions)
    position_value = calc_value_per_position(positions)
    position_available = calc_available_per_posistion(positions)
    
    position_target_value = strategy_target_value / len(positions)

    # sets up a for loop that goes through positions and back. iterate using index
    stop = (len(positions) * 2) - 1
    for i in range(stop):
        last = stop - 1
        index = 0
        if i > (last / 2): index = last - i
        else: index = i

        move = 0
        #if the total value of a position is > the target value for that position
        if position_value[index] > position_target_value:
            move = position_value[index] - position_target_value # move is the amount of money that needs to get moved
            # is there enough available cash to move? if so move it
            if position_available[index] > move: 
                temp += move
                position_value[index] -= move 
                position_available[index] -= move                               
            # if not move as much as possible
            else:
                temp += position_available[index]
                position_value[index] -= position_available[index]
                position_available[index] = 0
        
        #if the total value of a position is less than the target value for that position
        elif position_value[index] < position_target_value:
            move = position_target_value - position_value[index]
            #does temp have enough funds to get the value of the position up to the target value?
            if temp >= move:
                temp -= move
                position_value[index] += move
                position_available[index] += move
            #if thers not enoough money in temp, just move whatever is in there.
            else:
                position_value[index] += temp
                position_available[index] += temp
                temp = 0

    return positions, temp
