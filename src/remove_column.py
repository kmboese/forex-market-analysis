import pandas as pd
import decimal
import sys
from os import listdir, getcwd, remove
from os.path import isfile, join, splitext
from shutil import copyfile

QUIET = 0

cwd = getcwd()
#Select all .csv files
"""
files = [ticks for ticks in listdir(cwd) if \
	( isfile(join(cwd, ticks)) and (splitext(ticks)[1] == '.csv') )]
"""
#First argument is the filename from which to remove the column
data_file = join(cwd, sys.argv[1])
if not QUIET: print("Data file: " + data_file)

#make a temporary backup of the source file
print("Creating backup file of source csv...")
tmp_file = join(cwd, splitext(sys.argv[1])[0] + ".bak")
copyfile(data_file, tmp_file)

#The rest of the arguments are the columns we want to remove
remove_list = sys.argv[2:]
print("Remove list: " + str(remove_list) )
#Reader the header so we can see if the column(s) we want to remove exist
with open (data_file, 'r') as f:
	line = f.readline().splitlines()
	header = []
	for item in line:
		header = item.split(',')

print("Header: " + str(header) )

#Remove the columns specified
modified = False

#read in the data
df = pd.read_csv(data_file, sep=',')

for column in remove_list:
	if column in header:
		modified = True #note that we actually changed the source file
		print("Deleting " + str(column) )
		del df[column]
	else:
		print("Error: " + column + " not present in csv file!")

if not modified:
	print("No changes were made. Exiting now...")
	exit()

#Write the result out to the csv
df.to_csv(data_file, sep=',', index=False, header=True)

#remove the temporary backup file if successful
user_response = raw_input("Would you like to delete the backup file? Y/N > ")
if user_response.lower() == 'y':
	remove(tmp_file)
