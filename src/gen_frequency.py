'''
A program that takes in a set of bid-ask spread stock tick data and outputs a histogram of the data, where:
	* bins = number of unique bid-ask spread values present in the data (base)
	* min value = minimum bid-ask spread value observed
	* max value = maximum bid-ask spread value observed/values (2 or 3) std. deviations away from the mean

Usage: python gen_frequency.py

Setup:
	1. Download bid-ask spread data for years 2007, 2012, and 2017
	2. Unzip these three years into a directory
	3. Set "SPREAD_DATA_DIR" equal to the directory containing these three directories of spread data
	4. Run the script

Output: A directory in the parent directory of the spread data titled "Histograms" that contains the histogram data for each currency during each of the three months within it.
'''

import pandas as pd
import matplotlib.pyplot as plt
import numpy
import importlib
from pylab import figure
from os import listdir, getcwd, makedirs, name, pardir
from os.path import isfile, isdir, join, splitext, basename, abspath, exists
from math import log10, floor
importlib.import_module("gen_yearly_stats")
from gen_yearly_stats import genStatsData, saveStatsData, setBins, setCutoffs 
from collections import defaultdict
import pickle
import csv
#import time

#Global Variables
fig = plt.figure()
#Base the graph color on the year being graphed
colors = {"2007": 'b', "2012": 'g', "2017": 'r'}
#Data directory from which we are selecting years
cwd = getcwd()
parent = abspath(join(cwd, pardir))

#Constants
DATA_DIR = join(parent, "data")
SPREAD_DATA_DIR = join(DATA_DIR, "processed-data")
STATS_DIR = join(DATA_DIR, "stats")

QUIET = False
DEBUG = False

#Year from which to base the binning cut-off point
base_year = "2007"
#Year from which to base the number of bins for each currency
last_year = "2017"
#Month/year combinations we are sampling for histogram data
sample_data = [("January", "2007"), ("August", "2012"), ("December", "2017")]
years = [2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017]

'''Print statements if DEBUG flag is on'''
def dPrint(message):
	if DEBUG:
		print("DEBUG: {}".format(message))

'''Load the statistics data from a generated csv file into a dictionary that holds lists of the yearly/monthly data for each currency'''
def loadStatsData(filepath, filename, stats_list):
	file = join(filepath, filename)
	if not exists(file):
		print("Error: stats file does not exist")
		return stats_list
	else:
		with open(file, 'r') as file:
			reader = csv.reader(file)
			header = True
			for row in reader:
				stats = CurrencyStats()
				#Skip the header
				if header:
					header = False
				else:
					stats.loadData(row)
					stats_list[stats.short_name].append(stats)
		return stats_list

'''Returns the absolute path to a statistic's csv file'''
def getStatsPath(stats):
	return (join(SPREAD_DATA_DIR, stats.year, stats.month, stats.full_name))

'''Returns the absolute path to the histogram file for a CurrencyStats object'''
def getHistPath(stats, hist_dir):
	return join(hist_dir, stats.year, \
		(stats.year + "_" + stats.month + "_" + stats.full_name + \
			"_histogram.png"))

'''Set the upper cutoff bin for spread data to be at the base year maximum'''
def setClippedData(stats_list):
	for currency in stats_list.keys():
		for stats in stats_list[currency]:
			currency_path = getStatsPath(stats)
			df = pd.read_csv(currency_path, sep=',', \
				float_precision='round_trip', usecols=["spread"])
			#Standard clipped data import
			'''
			stats.clipped_data = numpy.clip(\
				df.spread, df.spread.min(), stats.cutoff)
			'''
			#Altered clipped data to manual value from cutoff_points
			stats.clipped_data = numpy.clip(\
				df.spread, df.spread.min(), cutoff_points[stats.short_name])


'''Generate the cutoff point for each currency based on the January 2007
outlier value'''
def getCutoffPoint(stats):
	return (stats.mean + 3*(stats.std_dev))


'''Generate a series of histograms from a list of currencies'''
def genHistograms(stats_list, hist_dir, replace_existing=False):
	#Set the bins for all currencies equal to 2017 bins, set cutoff point equal to 2007 cutoff
	if not QUIET: print("Generating histograms...")
	for currency in stats_list.keys():
		if not QUIET: print("Generating histograms for {}"\
			.format(stats_list[currency][0].readable_name))
		dPrint("bins = {}, {}, {}"\
			.format(stats_list[currency][0].bins, \
			stats_list[currency][1].bins, \
			stats_list[currency][2].bins))
		dPrint("cutoff = {}, {}, {}"\
			.format(stats_list[currency][0].cutoff, \
			stats_list[currency][1].cutoff, \
			stats_list[currency][2].cutoff))
		#Generate the histograms
		for stats in stats_list[currency]:
			save_path = getHistPath(stats, hist_dir)
			if exists(save_path) and not replace_existing:
				print("Histogram for {} already exists, skipping file..."\
					.format(stats.full_name))
			else:
				createHistogram(stats, stats.year, stats.month, hist_dir, save_path)


'''Creates and saves a histogram for a given currency dataset'''
def createHistogram(stats, year, month, hist_dir, save_path):
	#Choose graph color based on year
	color = colors[year]

	#plt.hist(data, bins=bins, density=True, facecolor=color, edgecolor='black', alpha=0.7)
	plt.hist(stats.clipped_data, bins=stats.bins, facecolor=color, edgecolor='black', alpha=0.7)
	plt.xlim([stats.min, stats.cutoff])

	#Title the graph and label the axes
	plt.title(str(month) + " " + str(year) + " Bid-Ask Spread Values: " +\
		stats.readable_name)
	plt.xlabel("Bid-Ask Spread", fontsize=15)
	plt.ylabel("Frequency", fontsize=15)

	#Format the graph so axis labels show
	plt.tight_layout()
	#plt.show() #Uncomment this to show the pyplot image on your computer
	plt.savefig(save_path)
	#don't close the graph to overlay multiple histograms on one graph
	plt.close()


def main():
	#Generate currency statistics: Jan07/Aug2012/Dec2017
	stats_list = defaultdict(list) #Dictionary of lists of currencies

	#Save histogram directory information
	hist_dir = join(SPREAD_DATA_DIR, "Histogram")
	if not exists(hist_dir):
		makedirs(hist_dir)
	for month, year in sample_data:
		if not exists (join(hist_dir, year) ):
			makedirs(join(hist_dir, year))

	#Load in existing currency data, otherwise create and save the data
	#if exists(STATS_SPREAD_DATA_DIR):
	if exists(""):
		print("Loading stats data from file...")
		stats_list = loadStatsData(STATS_DIR, "currency_statistics_altered", stats_list)
		#Set clipped data for all currencies to the base year maximum
		print("Setting data range to base year maximum for all currencies...")
		setClippedData(stats_list)
		#Set the cutoff for all currencies to base year maximum
		setCutoffs(stats_list)
		#Set number of bins for all currencies to 2017 bins
		print("Setting bins to 2017 bin number for all currencies...")
		setBins(stats_list)

	else:
		print("Statistics file doesn't exist. Please generate one using \"gen_yearly_stats.py\" before running this script.\nExiting...")

	#Generate the histograms for the currency data
	#genHistograms(stats_list, hist_dir, replace_existing=True)

if (__name__ == "__main__"):
	main()
