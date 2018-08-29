import pandas as pd
import matplotlib.pyplot as plt
import numpy
from os import listdir, getcwd, makedirs, name, pardir
from os.path import isfile, isdir, join, splitext, basename, abspath, exists
from math import log10, floor
from collections import defaultdict
import csv

QUIET = False

#***** Global Variables *****
#Data paths
cwd = getcwd()

# ***** Constants *****
PARENT = parent = abspath(join(cwd, pardir))
#root data directory
DATA_DIR = join(parent, "data")
#directory containing currency spread data	
SPREAD_DATA_DIR = join(DATA_DIR, "processed-data")	
#directory containing the statistics data
STATS_DIR = join(DATA_DIR, "currency-stats")

#List of all years and months considered for data directories
years = [2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017]
months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December" ]
#Save cutoff points for each currency based on the base year
cutoff_points = {"AUDJPY": 0.06, "AUDUSD": 0.00045, "EURAUD": 0.0009, \
				"EURGBP": 0.00027, "EURJPY": 0.04, "EURUSD": 0.0003,\
				"GBPAUD": 0.0009, "GBPJPY": 0.07, "GBPUSD": 0.0004, \
				"USDJPY": 0.03}
MAX_BINS = 50 #Maximum number of data bins to use


class CurrencyStats:
	def __init__(self, currency="Currency", df={'spread': [1,2,3]}, year="Year", month="Month"):
		self.full_name = currency
		#Get the 6-character currency name from the cross filename
		self.short_name = currency.split('_', 1)[0]
		self.readable_name = self.short_name[:3] + "/" + self.short_name[3:]
		self.year = year
		self.month = month
		try:
			self.mean = df.spread.mean()
			self.std_dev = df.spread.std()
			self.min = df.spread.min()
			self.max = df.spread.max()
			#The cutoff value for the last bin is pulled from a pre-defined dictionary
			self.cutoff = cutoff_points[self.short_name]

			'''Non-outlier data is defined as all values less than or equal to
			the cutoff point for the currency'''
			non_outlier = df.spread <= self.cutoff
			non_outlier_frame = df[non_outlier]

			#Bin based on unique values up to a cutoff point
			self.bins = non_outlier_frame.spread.nunique()
			#self.bins = df.spread.nunique()

			#Total number of ticks for the currency
			self.ticks = df.spread.count()

			#Clipped data allows for binning outlier values
			self.clipped_data = numpy.clip(\
				df.spread, df.spread.min(), self.cutoff)

			#List of most freqent bid-ask values
			self.frequent_values = []
		except:
			self.mean = 0
			self.std_dev = 0
			self.min = 0
			self.max = 0
			self.cutoff = 0
			self.bins = 0
			self.ticks = 0
			self.frequent_values = []
			#self.clipped_data = None

	'''Save in currency data from a csv file row'''
	def loadData(self, d):
		self.full_name = d[0]
		self.short_name = d[1]
		self.readable_name = d[2]
		self.year = d[3]
		self.month = d[4]
		self.mean = float(d[5])
		self.std_dev = float(d[6])
		self.min = float(d[7])
		self.max = float(d[8])
		self.cutoff = float(d[9])
		self.bins = int(d[10])

#Read in the header of a csv file and return it as a list
def readHeader(file):
	header = []
	with open (file, 'r+') as csvfile:
		reader = csv.reader(csvfile)
		header = next(reader)
	return header

#Read the first @samples number of cells in the given column, and return the
#highest number of decimal points encountered in any of the samples
def getColumnPrecision(dataframe, column, samples):
	precision = 0
	for i in range(0, samples):
		val = str(dataframe[column][i])
		#Get number of values after the decimal
		valStr = val.split('.')[1]
		if (len(valStr) > precision):
			precision = len(valStr)
	return precision


'''
Generate the statistics data for all currencies in a directory
Arguments:
	* stats_list: list of Stats objects to be generated
	* SPREAD_DATA_DIR: root directory containing yearly cross directories
'''
def genStatsData(stats_list, month_dir, month, year):
	for currency in listdir(month_dir):
		print("Generating stats for {}".format(currency))
		stats = CurrencyStats
		currency_path = join(month_dir, currency)
		df = pd.read_csv(currency_path, sep=',', \
			float_precision="round_trip",usecols=["spread"])
		stats = CurrencyStats(currency, df, year, month)
		stats_list[stats.short_name].append(stats)
	return stats_list

'''Save all generated statistics data for currency files'''
def saveStatsData(dir, filename, stats_list):
	filepath = join(dir, filename)
	#If file doesn't exist, create it and write the header
	if not exists(filepath):
		with open(filepath, 'w+', newline='\n') as file:
			writer = csv.writer(file)
			writer.writerow(["Full name"] + ["Short Name"] + ["Readable Name"] + \
			["Year"] + ["Month"] + ["Mean"] + ["Std Dev"] + ["Min"] + ["Max"] + \
			["Cutoff"] + ["Bins"] + ["Ticks"])
	#Write data to file
	for currency in stats_list.keys():
		for stats in stats_list[currency]:
			with open(filepath, 'a+', newline='\n') as file:
				writer = csv.writer(file)
				writer.writerow(\
					[stats.full_name] + [stats.short_name] + \
					[stats.readable_name] + [stats.year] + \
					[stats.month] + [stats.mean] + \
					[stats.std_dev] + [stats.min] + \
					[stats.max] + [stats.cutoff] + [stats.bins] + \
					[stats.ticks])

'''Set the cutoff points for each currency to the base year cutoff value'''
def setCutoffs(stats_list):
	for currency in stats_list.keys():
		for stats in stats_list[currency]:
			stats.cutoff = cutoff_points[stats.short_name]

'''Set the number of bins for each currency to the max number of bins in all years'''
def setBins(stats_list):
	for currency in stats_list.keys():
		max_currency_bins = 0
		for stats in stats_list[currency]:
			if stats.bins > max_currency_bins:
				max_currency_bins = stats.bins
		for stats in stats_list[currency]:
			stats.bins = min(max_currency_bins, MAX_BINS)

'''Generate the statistics data for the key set of currencies if it does not already exist.'''
def genStatsDataKeyYears(stats_list):
	for month, year in sample_data:
		year_dir = join(SPREAD_DATA_DIR, year)
		if not isdir(year_dir):
			print("Error: directory " + year_dir + " not found. Skipping directory...")
			continue
		month_dir = join(year_dir, month)
		currencies = [currency for currency in listdir(month_dir) if \
			(isfile(join(month_dir, currency)))]
		#Generate statistics data for all currencies
		for currency in currencies:
			stats = CurrencyStats
			#path to currency data
			currency_path = join(month_dir, currency)
			#read in the data
			df = pd.read_csv(currency_path, sep=',', float_precision="round_trip",\
				usecols=["spread"])
			#Generate statistics from the raw data
			stats = CurrencyStats(currency, df, year, month)
			'''Add the current currency stats to the dictionary list based on the short name of the currency'''
			stats_list[stats.short_name].append(stats)
	return stats_list

def main():
	stats_list = defaultdict(list) #Dictionary of lists of currencies

	if not exists(STATS_DIR):
		print("Creating stats directory...")
		makedirs(STATS_DIR)

	#Get a list of all directories to generate stats from 
	year_list = [year for year in listdir(SPREAD_DATA_DIR) if year in str(years)]
	for year in year_list:
		year_dir = join(SPREAD_DATA_DIR, year)
		#Generate monthly stats
		for month in listdir(year_dir):
			#Only recurse into actual monthly data directories
			if month not in months:
				continue
			month_dir = join(year_dir, month)
			stats_list = genStatsData(stats_list, month_dir, month, year)

			#Save the raw statistics
			#saveStatsData(STATS_DIR, "currency_statistics_raw.csv", stats_list)

			#Save statistics with cutoff
			saveStatsData(STATS_DIR, "currency_statistics_outlier.csv", stats_list)

			#Save a copy of the data with the altered bins
			setCutoffs(stats_list)
			setBins(stats_list)
			saveStatsData(STATS_DIR, "currency_statistics_50_bins.csv", stats_list)
			
			#Clear the stats list
			stats_list = defaultdict(list)
	
	print("Finished generating statistics...")
	

if (__name__ == "__main__"):
	main()
