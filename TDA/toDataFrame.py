import pandas as pd
from ta.utils import dropna

def toPandas(data):
    df = pd.DataFrame(data['candles'])
    #df = pd.DataFrame.drop(df, labels='volume', axis=1)
    df.rename(columns={"open": "Open", "high": "High", "low": "Low", "close": "Close", "volume": "Volume"}, inplace=True)
    df.index = df['datetime']
    df = pd.DataFrame.drop(df, labels='datetime', axis=1)
    df.index = pd.to_datetime(df.index, unit='ms')

    return df

