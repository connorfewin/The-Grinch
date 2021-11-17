import cbpro
import SandboxKey
import json
from pymongo import MongoClient
# The public client is open without API Keys, but cannot do certain things
#public_client = cbpro.PublicClient()
# authenticated clients can do more things.

#Everything returned out of here should be able to go straight into the DB!
#this means a list of dicts or BSON!

mongo_client = MongoClient()
auth_client = cbpro.AuthenticatedClient(SandboxKey.key, SandboxKey.b64secret, SandboxKey.passphrase,
                                            api_url="https://api-public.sandbox.pro.coinbase.com")
def getAllPairs():
    products = auth_client.get_products()
    # get_products returns a list of dicts
    return products

def getAccounts():
    accountsInfo = auth_client.get_accounts()
    print(accountsInfo)

def openSocket():
    ## This subscribes to a single product, you can use an array in products instead.
    wsClient = cbpro.WebsocketClient(url="wss://ws-feed.pro.coinbase.com", products="BTC-USD", channels=["ticker"])
    wsClient.close()

def mongoStuff():
    ## collections are created when inserted into, this could keep the DB updated while running
    db = mongo_client.cryptocurrency_database
    BTC_collection = db.BTC_collection
    wsClient = cbpro.WebsocketClient(url="wss://ws-feed.pro.coinbase.com", products = "BTC-USD", mongo_collection=BTC_collection, should_print=False)
    wsClient.start()

#returns a list of dicts, each dict is an entry.
def getPairHistory(pairname, granule):
    # get the history for one pair
    # granularity must be {60, 300, 900, 3600, 21600, 86400} 1m,5m,15m,1h,6h,1D

    #max data for a request is 300 data points. Make multiple to fill entire DB
    #get_product_history returns a list
    # data format: [[time,low,high,open,close,volume]]

    header = ['time', 'low', 'high', 'open', 'close', 'volume']
    history = auth_client.get_product_historic_rates(pairname, granularity=granule)
    if ('message' in history):
        return None
    historyDicts = []
    for record in history:
        entry = zip(header, record)
        historyDicts.append(dict(entry))
    return historyDicts

def getPairHistoryByTime(pairname, granule, last, now):
    header = ['time', 'low', 'high', 'open', 'close', 'volume']
    history = auth_client.get_product_historic_rates(pairname, granularity=granule, start=last, end=now)
    if ('message' in history):
            print("failed to return history of: ", pairname, "-", granule)
            return None
    historyDicts = []
    for record in history:
        entry = zip(header, record)
        historyDicts.append(dict(entry))
    return historyDicts

