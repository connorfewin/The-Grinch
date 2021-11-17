import Config
import Authenticate as Auth
import json

c = Auth.c

def get_watchlists():
    watchlists = c.get_watchlists_for_single_account(Config.account_id).json()
    watchlistName_list = []
    watchlistsId_list = []

    for key in watchlists:
        watchlistName_list.append(key['name'])
        watchlistsId_list.append(key['watchlistId'])

    return watchlistName_list

def get_symbols(watchName):
    symbol_list = []
    watchlists = c.get_watchlists_for_single_account(Config.account_id).json()
    for key in watchlists:
        #print(key['name'])
        if(key['name'] == watchName):
            for item in key['watchlistItems']:
                instrument = item['instrument']
                symbol_list.append(instrument['symbol'])
    return symbol_list










