#!/bin/bash

#Recurse through all directories in "Histograms" and compile all .png files
#into pdf files in each subdirectory

hist_dir="/media/kboese/Vertex4/stock-market/data/processed-data/Histogram"
save_dir="/media/kboese/Vertex4/stock-market/data/processed-data/yearly-histograms"
for dir in `ls $hist_dir/`
do
	cmd="convert $hist_dir/$dir/*.png $save_dir/$dir-hist.pdf"
	if [ $dir == "2007" ]; then
		eval $cmd
	else if [ $dir == "2012" ]; then
		eval $cmd
	else if [ $dir == "2017" ]; then
		eval $cmd
	fi
	fi
	fi
done
