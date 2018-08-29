"""
A script that returns the date based on percent change of ask price
"""

import pandas as pd
from os import listdir, getcwd
from os.path import isfile, isdir, join, splitext, basename, abspath
import time

QUIET = 0 #set to 1 to suppress progam feedback

data_dir = abspath("/media/kboese/Vertex4/stock-market/data/processed-data/2012")
if not isdir(data_dir):
    print("Error: data directory does not exist! Exiting...")
    exit()

#Process months (Kevin's code for reading multiple csv files)
months = [month for month in listdir(data_dir) if (isdir(join(data_dir, month)))]
for month in months:
    if not QUIET: print("\nProcessing " + month + " data:\n")

    #Save the absolute path to the current month
    month_dir = join(data_dir, month)

    #Select all .csv files in the current directory
    currency_crosses = [currency for currency in listdir(month_dir) if \
    ( isfile(join(month_dir, currency)) and (splitext(currency)[1] == '.csv') )]

    #Process tick data (Print out the date based on the percent change of ask price)
    for currency_cross in currency_crosses:
        print("Processing " + currency_cross[0:6] + ":")
        #df = pd.read_csv(join(month_dir,currency_cross), sep=',', header=[0], parse_dates=["Time (UTC)"])
        df = pd.read_csv(join(month_dir,currency_cross), sep=',', parse_dates=["Time (UTC)"])
        #df = pd.read_csv(join(month_dir, currency_cross), sep=',', parse_dates=[0], float_precision='round_trip')
        #df = pd.read_csv(join(month_dir, currency_cross), sep=',', float_precision='round_trip')
        print("\tDEBUG: read in the file to the dataframe")
        df.set_index("Time (UTC)", drop=True, inplace=True)
        daily_ask = df.resample("D")["Ask"]
        df["daily_ask_min"] = daily_ask.transform("min")
        df["daily_ask_max"] = daily_ask.transform("max")
        df["daily_ask_change"] = (df["daily_ask_max"] - df["daily_ask_min"]) / df["daily_ask_max"]
        # Change the percent change threshold below
        print(df[df.daily_ask_change > 0.05]["daily_ask_change"].resample("D").mean())
        print("\n")
        #break #single currency
    #break #single month
