import pandas as pd
import sys
import csv
from os import listdir, getcwd, makedirs, name
from os import name as os_name
from os.path import isfile, isdir, join, splitext, basename, abspath, exists
from math import log10, floor
import time

def getSpreadMean(src_filepath, precision):
	df = pd.read_csv(src_filepath, sep=',', float_precision='round_trip',\
		usecols=["spread"])
	#spread_mean = df.spread.mean().round(precision)
	spread_mean = round_to_n(df.spread.mean(), precision)
	#print("Mean: " + bid_ask_spread_mean)
	#print("Unrounded Mean: " + str(dataframe.spread.mean()))
	return spread_mean


def getSpreadStdDev(src_filepath, precision):
	df = pd.read_csv(src_filepath, sep=',', float_precision='round_trip',\
		usecols=["spread"])
	#spread_std_dev = df.spread.std().round(precision)
	spread_std_dev = round_to_n(df.spread.std(), precision)
	return spread_std_dev


#Returns the mean spread +- the standard deviation
def getSpreadMeanBounds(spread_mean, spread_std_dev, precision):
	'''
	Ensure lower bound isn't rounded to zero if it drops a decimal place.
	Since the bid-ask spread can't be negative, simply return 0 for the
	lower bound if this occurs.
	'''
	if (spread_mean - spread_std_dev < 0):
		lower_bound = 0
	else:
		#lower_bound = (spread_mean-spread_std_dev).round(precision)
		lower_bound = round_to_n((spread_mean-spread_std_dev), precision)
	#upper_bound = (spread_mean + spread_std_dev).round(precision)
	upper_bound = round_to_n((spread_mean + spread_std_dev), precision)
	return lower_bound, upper_bound


#Calculates all requested statistics and writes them out to the statistics
#file.
def calcStatistics(currency_name, statistics_filepath, src_filepath):
	#Calculate the bid-ask spread mean and write it to the statistics file
	#IMPORTANT: use float_precision='round_trip' to preserve source precision!
	precision = currency_sig_figs[currency_name]
	#print("DEBUG: precision for " + currency_name + " is " + str(precision) )
	spread_mean = getSpreadMean(src_filepath, precision)
	#Note: not sure how many sig figs desired for std dev.
	spread_std_dev = getSpreadStdDev(src_filepath, precision)
	spread_mean_lower_bound, spread_mean_upper_bound =\
		getSpreadMeanBounds(spread_mean, spread_std_dev, precision)

	with open(statistics_filepath, 'a+') as csvfile:
		writer = csv.writer(csvfile)
		writer.writerow(\
			[currency_name] + \
			[spread_mean] + \
			[spread_std_dev] + \
			[spread_mean_lower_bound] + \
			[spread_mean_upper_bound])


#Constants
QUIET = False

#Lambda functions
#Round a number to exactly n digits, rather than n decimal points
round_to_n = lambda x, n: round(x, -int(floor(log10(x)))+(n-1))

# Global Variables
currency_sig_figs = {\
'AUDJPY': 6, 'AUDUSD': 5, 'EURAUD': 6,\
'EURGBP': 5, 'EURJPY': 6, 'EURUSD': 6,\
'GBPAUD': 6, 'GBPJPY': 5, 'GBPUSD': 6,\
'USDJPY': 6, 'EURCHF': 6}

#Determine the directory to recurse into
cwd = getcwd()
#If no extra arguments given, use the fixed path
if len(sys.argv) == 1:
	data_dir = abspath("D:/stock-market/data/processed-data/2007")
else:
	data_dir = join(cwd, sys.argv[1]) #user passes in directory name on command line

#Save statistics directory information
if os_name == "nt":
	year = data_dir.split('\\')[-1]
	print("Windows system detected")
else:
	year = data_dir.split('/')[-1]
	print("Linux system detected")
stats_dirname = year + "_Statistics"

#Process months
start = time.time()
months = [month for month in listdir(data_dir) if \
( (isdir(join(data_dir, month))) and not (month == stats_dirname) ) ]
for month in months:
	if not QUIET: print("\nProcessing " + month + " data:")

	#Save absolute paths to local files and directories
	month_dir = join(data_dir, month)
	statistics_filename = month + "_spread_statistics.csv"
	stats_dir = join(data_dir, stats_dirname)
	#create the statistics directory if it does not exist
	if not exists(stats_dir):
		makedirs(stats_dir)
	statistics_filepath = join(stats_dir, statistics_filename)

	#If the statistics file for the month already exists, skip it and go to the
	#next currency
	if exists(statistics_filepath):
		print("Statistics for " + month + " already exists, "\
			+ "skipping file...")
		continue
	else:
		#Create the statistics file
		with open(statistics_filepath, 'w+') as csvfile:
			writer = csv.writer(csvfile)
			#Write the header
			writer.writerow(["Currency"] + ["Mean"] + ["Std Dev"] + \
			["Mean Lower Bound"] + ["Mean Upper Bound"])

	#Select all .csv files in the current directory
	currency_crosses = [currency for currency in listdir(month_dir) if \
	(isfile(join(month_dir, currency)) and splitext(currency)[1] == '.csv')]

	#Process tick data
	for currency_cross in currency_crosses:
		'''splitting on the underscore from the csv filename yields
		the currency name'''
		currency_name = currency_cross.split('_', 1)[0]
		calcStatistics(currency_name, statistics_filepath, join(month_dir, currency_cross))
	#break #break here to calculate only a single month

end = time.time()
if not QUIET: print("Generated statistics in " + str(round(end-start, 1)) + "seconds.")
