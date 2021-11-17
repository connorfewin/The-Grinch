from asyncio.windows_events import NULL
from os import sys
import Authenticate as Auth
import Config
from tda import auth, client
import json
c = Auth.c

def getPrice(s):
    r = c.get_price_history(s,
            period_type=client.Client.PriceHistory.PeriodType.YEAR,
            period=client.Client.PriceHistory.Period.ONE_YEAR,
            frequency_type=client.Client.PriceHistory.FrequencyType.DAILY,
            frequency=client.Client.PriceHistory.Frequency.DAILY)
    return r

def getPriceByTime(symbol, start, end):
    result = c.get_price_history(symbol,period_type=client.Client.PriceHistory.PeriodType.YEAR, start_datetime=start, end_datetime=end,
            frequency_type=client.Client.PriceHistory.FrequencyType.DAILY,
            frequency=client.Client.PriceHistory.Frequency.DAILY)
    return result

#This would output the price history to a text file named output.txt
"""
def txt(r):
    sys.stdout = open("output.txt", "w")
    print(json.dumps(r.json(), indent=4))
    sys.stdout.close()
"""




