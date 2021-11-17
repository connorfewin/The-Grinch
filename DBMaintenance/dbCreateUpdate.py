from pymongo import *
import os
import sys
import time
from bson import BSON
import json
from datetime import date
from datetime import timedelta
import datetime
#pymongo 3.12.0
#Python 3.9.X

#This append is needed to import
sys.path.append('../CBProScripts/')
import cbprostuff
sys.path.append('../TDA')
sys.path.append('../API_Web_Scrapper')
sys.path.append('../Manager')

#print(sys.path)

import Watchlist
import PriceHistory
from Strategies import Strategies
import Bitcoin_Twitter_scrapper
import WSB_Scrapper
import accessDB

granularityValue = {'1H': 3600, '1D': 86400}
granularityName = {3600: '1H', 86400: '1D'}


## Default Client, dbs are declared per method.
client = MongoClient()


#########################Crypto#########################
#insert all available product pairs to the DB in a single collection, index on ID
def insertProductPairs():
    db = client.managerdb
    collection = db.ProductPairs
    pairs = cbprostuff.getAllPairs()
    result = collection.insert_many(pairs)

#TODO after semester. Fix this to work with actual CBPro, not Sandbox
def updateProductPairs():
    print('Updating Product Pairs')
    db = client.managerdb
    collection = db.ProductPairs
    lastPairs = getProductPairs()
    currPairs = cbprostuff.getAllPairs()
    for pair in currPairs:
        print(pair['id'])
    newPairs = []
    print(lastPairs)
    for curr in currPairs:
        newPairs.append(curr) if curr['id'] not in lastPairs else False
    if newPairs:
        print("New Pairs")
        myColl = db.ProductPairs
        result = collection.insert_many(newPairs)

#get all saved CBPro pairs from DB
def getProductPairs():
    db = client.managerdb
    pairs = []
    collection = db.ProductPairs
    for doc in collection.find():
        pairs.append(doc['id'])
    return pairs

########################Crypto Product History################
#insert the initial info for specified product
def insertProductHistory(productName, granularity):
    db = client.cryptodb
    #Collection: the productName + granularity.ex: XRP-USD
    chosenGranule = granularityName[granularity]
    product = productName + '-' + chosenGranule
    myColl = collection.Collection(db,product)
    # granularity must be {60, 300, 900, 3600, 21600, 86400} 1m,5m,15m,1h,6h,1D
    
    history = cbprostuff.getPairHistory(productName, granularity)
    if history is not None:
        result = myColl.insert_many(history)

#update the specified collection
def updateProductHistory(myColl):
    db = client.cryptodb
    #limit the results to the latest.
    #the result is the entire record.
    cursor = myColl.find().sort('time', -1).limit(1)
    for item in cursor:
        latestTime = item['time']
    cursor.close()
    #must convert the timestamp to ISO 8601
    latestDate = date.fromtimestamp(int(latestTime))
    #get the pair from the current collection name.
    #split on '_' which is the pair delimiter
    splitName = myColl.name.split('-')
    pairName = splitName[0] + '-' + splitName[1]
    granule = splitName[2]
    chosenGranule = granularityValue[granule]

    #this returns all new entries to be made
    history = cbprostuff.getPairHistoryByTime(pairName, chosenGranule, datetime.datetime.fromtimestamp(latestTime + chosenGranule), (datetime.datetime.now()))
    newHistory = []
    if history:
        for item in history:
            print('latest: ', latestTime, 'item: ',  item['time'])
            if (latestTime < item['time']):
                newHistory.append(item)
            
    if newHistory:
        result = myColl.insert_many(newHistory)
            
def makeCryptoDB():
    print('Updating CryptoDB')
    # make the crypto db
    db = client.cryptodb
    #insert all available product pairs.
    insertProductPairs()
    pairs = getProductPairs()
    granules = [3600, 86400]
    for item in pairs:
        for granule in granules:
            insertProductHistory(item, granule)
            
###########################TDA##############
#change a symbol to the name it will have in DB
#This needs to change if there are different timeframes
def symbolToProductName(symbol):
    productName = symbol + '-' + '1D'
    productName = productName.strip("$")
    return productName
def collectionNameToSymbol(collName):
    symbol = collName.split('-')[0]
    return symbol

#extract the latest datetime from a collection
def getLatestTime(name):
    db = client.stockdb
    #limit the results to the latest.
    #the result is the entire record.
    latestTime = 0
    myColl = collection.Collection(db,name)
    cursor = myColl.find().sort('datetime', -1).limit(1)
    for item in cursor:
        latestTime = item['datetime']
    cursor.close()
    latestTime = int(latestTime / 1e3)
    return latestTime

#inserts all stocks from initial watchlist.
def insertWatchlists():
    db = client.stockdb
    names = Watchlist.get_watchlists()
    for name in names:
        symbols = Watchlist.get_symbols(name)
        for symbol in symbols:
            history = PriceHistory.getPrice(symbol)
            extract = history.json()
            #Generalized granularity will break this
            productName = symbolToProductName(symbol)
            #Empty lists are false
            if (extract["candles"]):
                myColl = collection.Collection(db,productName)
                result = myColl.insert_many(extract["candles"])

#Updates all of the stocks based on time and if they are already on watchlist.
            
def updateStocks():
    print('Updating StockDB')
    db = client.stockdb
    names = Watchlist.get_watchlists()
    currStocks = client.stockdb.list_collection_names()
    for name in names:
        symbols = Watchlist.get_symbols(name)
        print('Updating this list: ', symbols)
        for symbol in symbols:
            #if it already exists, then update
            productName = symbolToProductName(symbol)
            if productName in currStocks:
                print('Updating: ', symbol)
                start = datetime.datetime.fromtimestamp(getLatestTime(productName)) +  timedelta(days=1)
                end = datetime.datetime.today()
                history = PriceHistory.getPriceByTime(symbol, start, end)
                extract = history.json()
                print(extract)
                try:
                    if (extract['error']):
                        print(extract['error'])
                except:
                    if (extract["candles"]):
                        myColl = collection.Collection(db,productName)
                        result = myColl.insert_many(extract["candles"])
            #if it's new insert it
            else:
                print('New Symbol: ', symbol)
                history = PriceHistory.getPrice(symbol)
                extract = history.json()
                if (extract["candles"]):
                    myColl = collection.Collection(db,productName)
                    result = myColl.insert_many(extract["candles"])

#################################Sentiment#######

def insertWSB():
    #collect all symbols to be searched. if we could change the subreddit, this would be more useful too
    allSymbols = []
    db = client.stockdb
    stocks = db.list_collection_names()
    for name in stocks:
        allSymbols.append(collectionNameToSymbol(name))
    db = client.cryptodb
    cryptos = db.list_collection_names()
    for name in cryptos:
        allSymbols.append(collectionNameToSymbol(name))

    db = client.sentimentdb
    #https://stackoverflow.com/questions/9724906/python-date-of-the-previous-month
    currDate = date.today()
    first = currDate.replace(day=1)
    #Get a month or year of data
    lastMonth = first - datetime.timedelta(days=1)
    lastYear = currDate - datetime.timedelta(days=365)
    yesterday = currDate - datetime.timedelta(days=1)
    
    for symbol in allSymbols:
        ##WSB
        print("getting sentiment for: ", symbol.lower())
        subreddit = ''
        #data = json.loads(WSB_Scrapper.wsbReddit(yesterday.year, yesterday.month, yesterday.day, 'gme'))
        if symbol in stocks:
            subreddit = 'stock'
        elif symbol in cryptos:
            subreddit = 'crypto'
        data = json.loads(WSB_Scrapper.wsbReddit(lastYear.year, lastYear.month, lastYear.day, symbol.lower(), subreddit))
        print(data)
        if data["Title"]:
            #Make row records from column records
            titles = data["Title"]
            subjectivities = data["Subjectivity"]
            polarities = data["Polarity"]
            sentiments = data["Sentiment"]
            timestamps = data["Timestamp"]
            titleArr = []
            subArr = []
            polArr = []
            sentArr = []
            timeArr = []
            for title in titles:
                titleArr.append(titles[title])
            for subjectivity in subjectivities:
                subArr.append(subjectivities[subjectivity])
            for polarity in polarities:
                polArr.append(polarities[polarity])
            for sentiment in sentiments:
                sentArr.append(sentiments[sentiment])
            for time in timestamps:
                timeArr.append(timestamps[time])
            print(timestamps)
            print(timeArr)
            header = ['title', 'subjectivity', 'polarity', 'sentiment', 'datetime']
            rowStruct = zip(titleArr, subArr, polArr, sentArr, timeArr)
            rows = list(rowStruct)
            formatRows = []
            for item in rows:
                entry = zip(header,item)
                formatRows.append(dict(entry))
            myColl = collection.Collection(db, symbol)
            result = myColl.insert_many(formatRows)

"""
def insertTwitter():
    db = client.cryptodb
    productPairs = db.list_collection_names()
    symbols = []
    for item in productPairs:
        symbols.append(item[0:2])
    symbols = list(set(symbols))
    db = client.sentimentdb
    ##Twitter
    currDate = date.today()
    currDate = currDate.strftime("%Y-%m-%d")
    #print(currDate)
    data = json.loads(Bitcoin_Twitter_scrapper.twitterScrapper(currDate, 'bitcoin', 1000))
    #print(data)
    header = ['tweet', 'subjectivity', 'polarity', 'sentiment']
    titles = data["Cleaned_tweets"]
    subjectivities = data["Subjectivity"]
    polarities = data["Polarity"]
    sentiments = data["Sentiment"]
    titleArr = []
    subArr = []
    polArr = []
    sentArr = []
    for title in titles:
        titleArr.append(titles[title])
    for subjectivity in subjectivities:
        subArr.append(subjectivities[subjectivity])
    for polarity in polarities:
        polArr.append(polarities[polarity])
    for sentiment in sentiments:
        sentArr.append(sentiments[sentiment])
    header = ['title', 'subjectivity', 'polarity', 'sentiment']
    rowStruct = zip(titleArr, subArr, polArr, sentArr)
    rows = list(rowStruct)
    formatRows = []
    for item in rows:
        entry = zip(header,item)
        formatRows.append(dict(entry))
    myColl = collection.Collection(db, 'Twitter-BTC')
    result = myColl.insert_many(formatRows)
"""    

def insertSentiments():
    insertWSB()
    #insertTwitter()
############################# Manager #######################
def insertPositions():
    positions = []
    db = client.cryptodb
    cryptos = list(set(accessDB.getCryptoSymbols()))
    db = client.stockdb
    stocks = list(set(accessDB.getStockSymbols()))
    for strat in Strategies:
        for symbol in cryptos:
            positions.append(dict(product =  symbol, period = "1D", productType= 'crypto', strategy =  strat.value, position = None, buyPrices = None, availableBalance = 0))
        for symbol in stocks:
            positions.append(dict(product =  symbol, period = "1D", productType = 'stock', strategy = strat.value, position = None, buyPrices = None, availableBalance = 0))
    db = client.managerdb
    myColl = collection.Collection(db, 'Positions')
    result = myColl.insert_many(positions)

# for testing purposes mainly.
def updatePositions():
    db = client.managerdb
    myColl = collection.Collection(db, 'Positions')
    
    myColl.update_many(
        {},
        {'$set': {'availableBalance': 0}}
        )
    """
    myColl.delete_many(
        {'strategy': 'SENTIMENT'},
        {}
    )
    """
    
############################# Extras ##########################
    #updates all current collections
def updateAllHistory():
    #update crypto
    db = client.cryptodb
    collections = db.list_collection_names()
    for coll in collections:
            print(coll)
            if coll != 'ProductPairs':
                myColl = collection.Collection(db,coll)
                updateProductHistory(myColl)
    #Update stocks
    updateStocks()

def updateDBs():
    print('Updating All History DBs')
    updateProductPairs()
    updateAllHistory()
    print("Finished Updating!")

def makeOrUpdateDBs():
    names = client.list_database_names()
    if ('cryptodb' not in names):
        makeCryptoDB()
    if ('stockdb' not in names):
        insertWatchlists()
    if ('sentimentdb' not in names):
        insertSentiments()
    if ('managerdb' not in names):
        insertPositions()
    if ('cryptodb' and 'stockdb' and 'sentimentdb' in client.list_database_names()):
        updateDBs()


updatePositions()
