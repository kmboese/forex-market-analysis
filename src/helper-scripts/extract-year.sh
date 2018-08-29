#!/bin/bash

#user variables
year=2009 #name of the zip to be extracted

#Extract each month from the yearly zip
for month in `cat months.txt`
do
	7z x $year.7z -o../ $year/$month
	sleep 5
done
