import pandas as pd
import numpy as np
from os import listdir, getcwd, pardir, makedirs
from os import name as os_name
from os.path import isfile, isdir, join, splitext, basename, abspath, exists
from time import localtime, asctime

#Data paths
cwd = getcwd()
parent = abspath(join(cwd, pardir))
#datapath = "E:\\stock data\\data" #directory containing all years directories
datapath = abspath(join(parent, "data", "processed-data")) #Kevin's path
#path to the binning data csv
#Directory to currency statistics data
stats_path = join(parent, "data", "trans_cssr_stats") #Kevin's path
#Directory to save the .dat files
savepath = join(parent, "data", "dat-files")
if not exists(savepath):
    makedirs(savepath)

#Global Variables
months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December" ]
years = [2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017]
current_char = '1' #initial character value to use
bins = {}
cutoff = 0
num_bins = 20
FREQ_START_COLUMN = 12
frequency_values = [] #Frequency values for a given currency

def add_values(value):
    global current_char
    '''
    if value > cutoff:
        return '0'
    '''
    if abs(value) not in bins.keys():
        if len(bins) + 1 == num_bins:
            return '0'
        #print value
        current_char = chr(ord(current_char) + 1)
        if ord(current_char) == ':': #skip non-alphanumeric
            current_char = chr(ord(current_char) + 7)
        if ord(current_char) == '[': #skip non-alphanumeric
            current_char = chr(ord(current_char) + 6)
        bins[abs(value)] = current_char

    return bins[abs(value)]

'''
Converts a frequency values into an alpha value.
    * Arguments:
        * value: spread value to be converted
'''
def frequency_to_alpha(value):
    global frequency_values
    begin_alpha = 'a'
    alpha = ''

    #Convert the value to an alpha based on its location in the frequency list
    if value in frequency_values:
        alpha = chr(ord(begin_alpha) + frequency_values.index(value))
    #Give the value a special value if it is not in the frequent-value list
    else:
        alpha = '0'
    
    return alpha

'''
Generates dat files for CSSR based on spread data with cutoff points.
Saves the dat files to the savepath.
'''
def genDatFilesCutoff(stats_path, datapath, savepath):
    #Read in the statistics data
    with open(stats_path, 'r') as fd:
        stats_data = pd.read_csv(fd)
    bin_2017 = stats_data[stats_data.Year == 2017]

    #Set cutoff and bins based on key years
    for cross in bin_2017['Short Name']:
        cutoff = stats_data[stats_data["Short Name"] == cross]["Cutoff"].values[0]
        num_bins = bin_2017[bin_2017["Short Name"] == cross]["Bins"].values[0]

    #Create dat files for each year of spread data
    for year in listdir(datapath):
        for month in months:
            for file in listdir(join(join(datapath, year), month)):
                if file[:6] == cross:
                    bins = {}
                    current_char = '1' #initial character value to use  
                    df = pd.read_csv(join(datapath, year, month, file), index_col = None, header = 0)
                    vf = np.vectorize(add_values)
                    converted = vf(df["spread"].values)
                    copy = np.empty_like(converted)
                    copy[:] = converted
                    dat_file = join(join(join(savepath, cross), year), year + '_' + month + '_' + cross + ".dat")
                    with open(dat_file, "a+") as fd:
                        copy.tofile(fd)
                    print "finished the file " + file + " at "
                    print asctime(localtime())  

'''
Generates .dat files for CSSR based on the top 20 most frequent spread values for each monthly currency data file.
Runs through all yearly directories in the data directory and saves the .dat files to the savepath for each month.
'''
def genDatFilesFrequency(stats_path, datapath, savepath):
    global num_bins
    global frequency_values
    #Get list of all cssr stats data files
    stats_list = listdir(stats_path)
    #Process 1 year of data
    for year in (listdir(datapath)):
        file_created = False #check if any dat files were created for the given year
        #skip non-spread data directories
        if (year not in str(years)):
            #print("skipping directory {}".format(year))
            continue
        #Select stats file based on the current year
        lst = [stats_file for stats_file in stats_list if (stats_file.split("_")[-1] == \
                (year + ".csv"))]
        stats = lst[0]
        #Read in the stats data
        df = pd.read_csv(join(stats_path, stats), sep=',', float_precision="round_trip")
        #Select frequency information
        #frequencies = df.iloc[:,FREQ_START_COLUMN:]
        #print(frequencies.values)
    
        #Generate currency dat files
        for currency in df["Full name"]:
            #Pull the month name from the stats file
            month = df.loc[df["Full name"] == currency, "Month"].values.tolist()[0]
            month_spread_path  = join(datapath, year, month)
            currency_name = currency.split("_")[0]
            year_savepath = join(savepath, year + "_dat_files")
            if not exists(year_savepath):
                makedirs(year_savepath)
            save_file = join(year_savepath, str(year) + "_" + month + "_" + currency_name + ".dat")
            #Skip the file if it already exists
            if exists(save_file):
                print("{} dat file already exists, skipping file...".format(currency))
                continue

            #Get frequency data
            frequency_list = df.loc[df["Full name"] == currency, \
                    ["F" + str(i) for i in range(1,num_bins+1)]]
            frequency_values = frequency_list.values.tolist()[0]
            #Set the alphabet size to the number of frequency values for the currency
            num_bins = len(frequency_values)
            print("Creating alpha data for {}\tAlphabet size: {}".format(currency, num_bins))
            currency_path = join(month_spread_path, currency)
            spread_df = pd.read_csv(currency_path, sep=',', float_precision="round_trip")
            #Vectorize the spread data for turning into alpha characters
            vf = np.vectorize(frequency_to_alpha)
            alpha_chars = vf(spread_df["spread"].values)
            output = np.empty_like(alpha_chars)
            output[:] = alpha_chars
            
            with open(save_file, "w+") as fd:
                output.tofile(fd)
                file_created = True
            frequency_values = [] #Clear out frequency values for the next currency
            #exit() #Stop after 1 currency
        
        if (file_created): exit() #Stop after 1 year



def main():
    print("Generating .dat files...")
    genDatFilesFrequency(stats_path, datapath, savepath)


if (__name__ == "__main__"):
    main()
