from gen_frequency import setBins, setClippedData, saveStatsData, genStatsData, CurrencyStats
import pandas as pd
import numpy as np
import csv
from os import listdir, getcwd, makedirs, name
from os.path import isfile, isdir, join, splitext, basename, abspath, exists, dirname
from collections import defaultdict

#Constants
#Windows path
if name == "nt":
    data_dir = abspath\
            ("D:/stock-market/data/processed-data/2017")
    year = data_dir.split("\\")[-1]
#Linux path
else:
    data_dir = abspath\
        ("/home/kevin/davis-projects/ecs192/stock-market/data/cssr-data")
    year = data_dir.split("/")

ROOT_DATA_DIR = join(dirname(getcwd()), "data")
STATS_DIR = join(ROOT_DATA_DIR, "trans_cssr_stats")
STATS_NAME = "trans_cssr_stats" + "_" + year + ".csv"
TRANS_CSSR_BINS = 20 #Alphabet size

#Global variables
months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]


'''Generate the statistics data for the key set of currencies if it does not already exist.'''
def genCSSRStatsData(stats_list, month_dir):
    if name == "nt":
        month = month_dir.split("\\")[-1]
    else:
        month = month_dir.split("/")[-1]
    #Save all the monthly currency spread files into a list
    currencies = [currency for currency in listdir(month_dir) if \
        (isfile(join(month_dir, currency)))]
    #Generate statistics data for all currencies
    for currency in currencies:
        print("Generating stats for {}".format(currency))
        stats = CurrencyStats
        #path to currency data
        currency_path = join(month_dir, currency)
        #read in the data
        df = pd.read_csv(currency_path, sep=',', float_precision="round_trip",\
            usecols=["spread"])
        #Generate statistics from the raw data
        stats = CurrencyStats(currency, df, year, month)
        #Get the top most frequent data points
        stats.frequent_values = (df.spread.value_counts().axes[0][:TRANS_CSSR_BINS].tolist())
        '''Add the current currency stats to the dictionary list based on the short name of the currency'''
        stats_list[stats.short_name].append(stats)
    return stats_list

def saveCSSRData(dir, filename, stats_list):
    filepath = join(dir, filename)
    #If file doesn't exist, create it and write the header
    if not exists(filepath):
        with open(filepath, 'w+', newline="\n") as file:
            writer = csv.writer(file)
            writer.writerow(["Full name"] + ["Short Name"] + ["Readable Name"] + \
            ["Year"] + ["Month"] + ["Mean"] + ["Std Dev"] + ["Min"] + ["Max"] + \
            ["Cutoff"] + ["Bins"] + ["Ticks"] + ["F" + str(i) for i in range(1,21)])
    #Write data to file
    for currency in stats_list.keys():
        for stats in stats_list[currency]:
            with open(filepath, 'a+', newline="\n") as file:
                writer = csv.writer(file)
                writer.writerow(\
                    [stats.full_name] + [stats.short_name] + \
                    [stats.readable_name] + [stats.year] + \
                    [stats.month] + [stats.mean] + \
                    [stats.std_dev] + [stats.min] + \
                    [stats.max] + [stats.cutoff] + [stats.bins] + \
                    [stats.ticks] + [f for f in stats.frequent_values])

'''Set the cutoff points for each currency to the base year cutoff value'''
'''
def setCSSRCutoffs(stats_list):
    for currency in stats_list.keys():
        for stats in stats_list[currency]:
            stats.cutoff = cutoff_points[stats.short_name]
'''

'''Set the number of bins for each currency to the max number of bins in all years'''
def setCSSRBins(stats_list):
    for currency in stats_list.keys():
        max_currency_bins = 0
        for stats in stats_list[currency]:
            if stats.bins > max_currency_bins:
                max_currency_bins = stats.bins
        for stats in stats_list[currency]:
            stats.bins = min(max_currency_bins, TRANS_CSSR_BINS)

def main():
    stats_list = defaultdict(list) #Dictionary of lists of currencies

    #Create the data directory for the stats files, if needed
    if not exists(STATS_DIR):
        makedirs(STATS_DIR)

    #If the stats file already exists, warn the user
    if exists (join(STATS_DIR, STATS_NAME)):
        response = input("Warning: the statistics file for this year already exists. Are you sure you want to append to it? y/n > ")
        if response.lower() == "n":
            print("Exiting now...")
            exit()

    #Generate and save statistics monthly to keep the memory footprint low
    for month in listdir(data_dir):
        #Skip non-month directories
        if month not in months:
            continue
        month_dir = join(data_dir, month)
        stats_list = genCSSRStatsData(stats_list, month_dir)
        #Set the actual bin number
        setCSSRBins(stats_list)
        saveCSSRData(STATS_DIR, STATS_NAME, stats_list)
        stats_list.clear()

if (__name__ == "__main__"):
    main()
