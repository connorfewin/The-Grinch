import Config
import Authenticate as auth
import tda.orders

client = auth.c
"""
If the order is successfully placed, then resp will be the order id, if it is not successfully placed
it will return <Response [400 ]>. In order to use these methods in your strategy, import
"""
# This will buy at the market value for the given stock
def buy_market(symbol, quantity):
    builder = tda.orders.equities.equity_buy_market(symbol, quantity)
    resp = client.place_order(Config.account_id, builder.build())

# This will place a buy order that gets executed at a specified price
def buy_limit(symbol, quantity, price):
    builder = tda.orders.equities.equity_buy_limit(symbol, quantity, price)
    resp = client.place_order(Config.account_id, builder.build())

# This will sell a specified amount of a given security at the market value
def sell_market(symbol, quantity):
    builder = tda.orders.equities.equity_sell_market(symbol, quantity)
    resp = client.place_order(Config.account_id, builder.build())

# This will sell a specified amount of a given security at a specific price
def sell_limit(symbol, quantity, price):
    builder = tda.orders.equities.equity_sell_limit(symbol, quantity, price)
    resp = client.place_order(Config.account_id, builder.build())

# This will sell short at the market value. DO NOT USE if you do not understand what selling short means.
def sell_short_market(symbol, quantity):
    builder = tda.orders.equities.equity_sell_short_market(symbol, quantity)
    resp = client.place_order(Config.account_id, builder.build())

# This will sell short at a specified price. DO NOT USE if you do not understand what selling short means.
def sell_short_limit(symbol, quantity, price):
    builder = tda.orders.equities.equity_sell_short_limit(symbol, quantity, price)
    resp = client.place_order(Config.account_id, builder.build())




