from pymongo import *
from bson.json_util import dumps, loads
import pymongo
client = MongoClient()

#edit crypto & stock to make toDataframe
def getCryptoHistory(productPair, period):
    db = client.cryptodb
    collectionName = productPair + "-" + period
    if collectionName not in client.cryptodb.list_collection_names():
        print(productPair)
        raise Exception("Invalid crypto collection")
    else:
        myColl = collection.Collection(db, collectionName)
        cursor = myColl.find().sort('time', 1)
        data = dumps(list(cursor))
        json_data = loads(data)
        #rename the time header to datetime
        for item in json_data:
            item["datetime"] = item["time"]
        return json_data

def getStockHistory(symbol):
    db = client.stockdb
    collectionName = symbol + "-1D"
    if collectionName not in db.list_collection_names():
        raise Exception("Invalid stock collection")
    else:
        myColl = collection.Collection(db, collectionName)
        cursor = myColl.find().sort('datetime', 1)
        data = dumps(list(cursor))
        json_data = loads(data)
        return json_data

def getStockSymbols():
    db = client.stockdb
    symbols = []
    for name in db.list_collection_names():
        symbol = name.split('-')[0]
        symbols.append(symbol)
    return symbols

def getCryptoSymbols():
    db = client.cryptodb
    symbols = []
    for name in db.list_collection_names():
        symbol = name.split('-')[0]
        symbols.append(symbol)
    return symbols

def getSentimentHistory(platform):
    db = client.sentimentdb
    collectionName = platform + "-BTC"
    if collectionName not in client.sentimentdb.list_collection_names():
        raise Exception("Invalid stock collection")
    else:
        myColl = collection.Collection(db, collectionName)
        data = dumps(list(cursor))
        json_data = loads(data)
        return json_data

# This can only return from history!
def getLatestPriceBySymbol(marketType, symbol):
    db = openDB(marketType)
    collections = db.list_collection_names()
    latestPrice = 0
    myColl = None
    cursor = None
    for coll in collections:
        if symbol in coll and 'USDC' not in coll:
            myColl = collection.Collection(db, coll)
            if db.name == 'cryptodb':
                cursor = myColl.find().sort('time', -1).limit(1)
            else:
                cursor = myColl.find().sort('datetime', -1).limit(1)
            for item in cursor:
                latestPrice = item['close']
            #THERES A PROBLEM WHEN WE DONT GET MANAGERDB Prices.
    #print("latestPrice: ", latestPrice)
    return latestPrice

# This can return from history or position!
def getLatestPrice(position):
    #print(position)
    db = openDB(position['productType'])
    collections = db.list_collection_names()
    latestPrice = 0
    cursor = None
    for coll in collections:
        #this if is needed for crypto prices
        #if there is a position on a product, there is always a price
        if (position['product'] in coll and 'USD' in coll and 'USDC' not in coll):
            collName = coll
            myColl = collection.Collection(db, collName)
            if db.name == 'cryptodb':
                cursor = myColl.find().sort('time', -1).limit(1)
            else:
                cursor = myColl.find().sort('datetime', -1).limit(1)
            for item in cursor:
                latestPrice = item["close"]
        elif position['buyPrices']:
            latestPrice = position['buyPrices'].index(position['buyPrices'].count - 1)
            #print("No USD record for: ", position['product'], " returning last buy price")
        else:
            continue
            #print("No USD price record.")
    #print("latestPrice: ", latestPrice)
    return latestPrice
    
def updatePositionByStrategy(position):
    print(position)
    #WHY
    if (position == 'crypto' or position == 'stock'):
        return
    print("Updating Positions...")
    db = client.managerdb
    myColl = collection.Collection(db, 'Positions')
    myColl.update_one(
        {'productType': position['productType'], 'strategy': position['strategy'], 'product': position['product']},
        {'$set': {'availableBalance': position['availableBalance']}}
    )
    print("Finished Updating Positions")
#StrategyManager
# It goes to each strat, treats it as a portfolio and checks if the new point has cause a buy or sell.
# if it doesn't have positions, check buy. If it has one sell.

def getPositions():
    positions = []
    db = client.managerdb
    coll = db.Positions
    #I can return the positions sorted if desired.
    docs = coll.find().sort('product', pymongo.DESCENDING)
    for doc in docs:
        positions.append(doc)
    return positions

def openDB(productType):
    if productType == 'crypto':
        db = client.cryptodb 
    else:
        db = client.stockdb
    return db
"""
def updatePositions(newBalance):
    db = client.managerdb
    coll = db.Positions
    result = coll.update_many({}, {'$set': { 'availableBalance': newBalance}})
    #print(result)
"""
