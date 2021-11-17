"""
This is going to act as a template for a custom function. If the function is not in the 
libary on the fastquant github, you can use this template to construct and test a custom
strategy.

The important thing to remember here is that the backtester takes a single custom column of values,
an upper_limit value and a lower_limit value. It will go through the custom column and if it is above 
the upper_limit it will sell and if it is below the lower_limit it will buy. Keep that in mind when
you go to format your data. 

*** For how to use the FastQuant for custom strategies, look at the BackTest/LongTest.py***
"""
# Imports:
import sys

# This is a technical analysis file that can add a lot of technical analysis tools to your dataframe
sys.path.append('../TDA')
import TechnicalAnalysis

# data vizualization library to make sure the strategy is working like you want it to
import matplotlib.pyplot as plt


# This going to be the strategy itself.
def strategy(dataframe):
    # append your custom strategy data into this list
    custom = []
    """
    
    Implement Custom Strategy based on your dataframe here: 

    """
    # add custom strategy data into the data frame, This is how I did it, but you can import it right
    # into the data frame within the strategy.
    dataframe["custom"] = custom

    return dataframe
