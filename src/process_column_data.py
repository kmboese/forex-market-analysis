import pandas as pd
#import decimal
import sys
from os import listdir, getcwd
from os import name as os_name
from os.path import isfile, isdir, join, splitext, basename, abspath
import time

'''Checks if the column to be processed, and skips it if it does. Otherwise,
calculates the column data and adds it to the spreadsheet '''
def processTickData(header, filepath):
	decimals = 8
	for column in calculated_columns:
		if column in header:
			print(column + " already exists for " + basename(filepath))
		else:
			if column == 'spread':
				df = pd.read_csv(filepath, sep=',', float_precision='round_trip') #read in the tick data
				df[column] = (df.Ask - df.Bid).round(decimals=decimals)
				#float_format option preserves original precision without
				#introducing float errors 
				df.to_csv(filepath, sep=',', index=False, header=True, float_format='%g')

def parseArgs():
	data_dir = abspath\
		("/media/kevin/ESD-USB/stock-market/processed-data/Test")
	#List of cmd line arguments
	options = []
	quiet = False
	#By default, run script on all months in a directory
	process_single_month = False
	argc = len(sys.argv)
	if (argc == 1):
		if os_name == "nt":
			year = data_dir.split('\\')[-1]
		else:
			year = data_dir.split('/')[-1]
	elif argc > 1:
		#Help command: print help and exit
		if sys.argv[1] == "--help" or sys.argv[1] == "-h":
			print(
				'Help:\n'
				'Syntax:'
					' python process_column_data.py <directory name> <options>'
				'\n\t* If no directory name is given, the path in the script will be used.'
				'\nOptions:'
				'\n\t--single:\tProcess spread data for a single month of a given year.'
				'\n\t--quiet (--q):\tSuppress program print statements, except errors.'
			)
			exit()
		#Standard command: process flags and assign year based on whether
		#year is passed explicitly or not
		else:
			if isinstance(sys.argv[1], int):
				year = sys.argv[1]
				data_dir = join(cwd, year)
				options = sys.argv[2:]
			if os_name == "nt":
				year = data_dir.split('\\')[-1]
			else:
				year = data_dir.split('/')[-1]
			options = sys.argv[1:]

			#Process options:
			for option in options:
				if option == "--single":
					process_single_month = True
				elif option == "--quiet" or option == "--q":
					quiet = True
	#Validate data directory
	if not isdir(data_dir):
		print("Error: given directory " + data_dir + " does not exist!"\
		+ " Exiting now...")
		exit()

	return data_dir, year, process_single_month, quiet


calculated_columns = ['spread'] #columns we wish to calculate for the csv data

#Determine the directory to recurse into
cwd = getcwd()

#Select directory
data_dir, year, process_single_month, quiet = parseArgs()

#Process months
#Don't process the stats directory with the script
stats_dirname = str(year) + "_Statistics"
months = [month for month in listdir(data_dir) if \
(isdir(join(data_dir, month)) and not (month == stats_dirname) )]
start = time.time()
for month in months:
	if not quiet: print("\nProcessing " + month + " data:")

	#Save the absolute path to the current month
	month_dir = join(data_dir, month)
	#Select all .csv files in the current directory
	currencies = [currency for currency in listdir(month_dir) if \
	(isfile(join(month_dir, currency)) and (splitext(currency)[1] == '.csv') )]

	#Process tick data
	skip = False
	for currency in currencies:
		'''If the spread has already been calculated, don't re-calculate and go
		to the next file'''
		with open(join(month_dir, currency), 'r') as file:
			header = file.readline()
		for column in calculated_columns:
			if column in header:
				if not quiet: print(column + " already computed in file " + currency \
					+ ". Skipping file...")
				skip = True
		if skip:
			continue
		processTickData(header, join(month_dir, currency))

	if process_single_month:
		break

end = time.time()
if not quiet: print("Time elapsed: " + str(round((end-start), 1)) + " seconds.")
