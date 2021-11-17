import Config
import Authenticate as Auth
import json

c = Auth.c

def getBalance():
    balance = c.get_account(Config.account_id, fields=None)
    return balance.json()

def getPositions():
    p = c.Account.Fields.POSITIONS
    positions = c.get_account(Config.account_id, fields=p)
    return positions.json()

def getOrders():
    o = c.Account.Fields.ORDERS
    orders = c.get_account(Config.account_id, fields=o)
    return orders.json()

b = getBalance()
p = getPositions()
o = getOrders()

print(json.dumps(b, indent=4))