import numpy as np
import pandas as pd
from math import sqrt
import matplotlib.pyplot as plt
from scipy.ndimage.measurements import label
from scipy.signal import savgol_filter
from sklearn.linear_model import LinearRegression
import json

# Method used to create the lower linear regression line.
def pythag(pt1, pt2):
    a_sq = (pt2[0] - pt1[0]) ** 2
    b_sq = (pt2[1] - pt1[1]) ** 2
    return sqrt(a_sq + b_sq)

# Calculates the regression coefficient
def regression_ceof(pts):
    X = np.array([pt[0] for pt in pts]).reshape(-1, 1)
    y = np.array([pt[1] for pt in pts])
    model = LinearRegression()
    model.fit(X, y)
    return model.coef_[0], model.intercept_

# Gets the local min and max points
def local_min_max(pts):
    local_min = []
    local_max = []
    prev_pts = [(0, pts[0]), (1, pts[1])]
    for i in range(1, len(pts) - 1):
        append_to = ''
        if pts[i-1] > pts[i] < pts[i+1]:
            append_to = 'min'
        elif pts[i-1] < pts[i] > pts[i+1]:
            append_to = 'max'
        if append_to:
            if local_min or local_max:
                prev_distance = pythag(prev_pts[0], prev_pts[1]) * 0.5
                curr_distance = pythag(prev_pts[1], (i, pts[i]))
                if curr_distance >= prev_distance:
                    prev_pts[0] = prev_pts[1]
                    prev_pts[1] = (i, pts[i])
                    if append_to == 'min':
                        local_min.append((i, pts[i]))
                    else:
                        local_max.append((i, pts[i]))
            else:
                prev_pts[0] = prev_pts[1]
                prev_pts[1] = (i, pts[i])
                if append_to == 'min':
                    local_min.append((i, pts[i]))
                else:
                    local_max.append((i, pts[i]))
    return local_min, local_max

def long(df):

    series = df['close']
    i = df.index
    series.index = np.arange(series.shape[0])

    month_diff = series.shape[0] // 30

    if month_diff == 0:
        month_diff = 1

    smooth = int(2 * 1 + 3)

    pts = savgol_filter(series, smooth, 3)

    local_min, local_max = local_min_max(pts)
    
    series = df['close']
    series.index = np.arange(series.shape[0])

    month_diff = series.shape[0] // 30

    if month_diff == 0:
        month_diff = 1

    smooth = int(2 * 1 + 3)

    pts = savgol_filter(series, smooth, 3)

    local_min, local_max = local_min_max(pts)

    local_min_slope, local_min_int = regression_ceof(local_min)
    local_max_slope, local_max_int = regression_ceof(local_max)
    support = (local_min_slope * np.array(series.index)) + local_min_int
    resistance = (local_max_slope * np.array(series.index)) + local_max_int

    data = df
    data.index = np.arange(data.shape[0])
    data['min_line'] = (data.index * local_min_slope) + local_min_int
    data['max_line'] = (data.index * local_max_slope) + local_max_int
    data.index = df.index
    custom = []

    # this for loop creates the custom column, if it is a buy, it gets a -1,
    # if it is a sell it gets a 1, else it gets 0.
    for index, row in data.iterrows():
        if row['close'] < row['min_line']:
            custom.append(-1)
                
        elif row['close'] > row['max_line']:
           custom.append(1)
        else:
            custom.append(0)

    # reformat df to use for backtester.
    # Add the custom column to the dataframe
    df["custom"] = custom
    # Reset the dataframe index to the dates.
    df.index = i

    return df

