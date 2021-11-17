import numpy as np
import pandas as pd
import math
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import PriceHistory as p
import json
import matplotlib.dates as mpl_dates

#Change this symbol to plot significant lines onto any stock market security you want
symbol = 'AMZN'
data = p.getPrice(symbol)
data = data.json()
sig_points = []


#print(json.dumps(data.json(), indent=4))

df = pd.DataFrame(data['candles'])
df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')

#s is the average candle size in the dataframe
s =  np.mean(df['high'] - df['low'])

def isSupport(df,i):
    support = df['low'][i] < df['low'][i-1] and df['low'][i] < df['low'][i+1] \
            and df['low'][i+1] < df['low'][i+2] and df['low'][i-1] < df['low'][i-2]
    return support

def isResistance(df,i):
    resistance = df['high'][i] > df['high'][i-1]  and df['high'][i] > df['high'][i+1] \
                and df['high'][i+1] > df['high'][i+2] and df['high'][i-1] > df['high'][i-2]
    return resistance

def isFarFromLevel(l):
   return np.sum([abs(l-x) < s  for x in sig_points]) == 0

#scans the data frame, filters based on if the points are close to each other. if they are 
#further away than the average candle size, it'll add it to sig_points
for i in range(2,df.shape[0]-2):
  if isSupport(df,i):
    l = df['low'][i]

    if isFarFromLevel(l):
      sig_points.append((i,l))
  elif isResistance(df,i):
    l = df['high'][i]

    if isFarFromLevel(l):
      sig_points.append((i,l))

def plot_all(df):
  
  fig = go.Figure(data=[go.Candlestick(x=df.index,
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'])])
  
  for i in sig_points:
    fig.add_shape(type='line',
                x0=i[0],
                y0=i[1],
                x1=252,
                y1=i[1],
                line=dict(color='Red',),
                xref='x',
                yref='y'
)

  
  fig.update_layout(
    title = symbol,
    yaxis_title = 'Price',
    xaxis_title = 'Date'
  )

  fig.show()

plot_all(df)




  