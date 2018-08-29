from os import listdir, getcwd, pardir, makedirs
from os import name as os_name
from os.path import isfile, isdir, join, splitext, basename, abspath, exists
from time import localtime, asctime

from transCSSR_bc import *
import matplotlib.pyplot as plt
import graphviz
from sklearn.metrics import log_loss
from matplotlib.ticker import MaxNLocator

import pandas as pd

import findLetters

#Data paths	
cwd = getcwd()
parent = abspath(join(cwd, pardir))
dat_path = join(parent, "data", "dat-files-months")
binpath = join(parent, "src", "stats-data", "currency_statistics_altered.csv") #Kevin's path

savepath = join(parent, "data", "transCSSR-results")
if not exists(savepath):
    makedirs(savepath)

#currencies = ["AUDJPY", "AUDUSD", "EURAUD", "EURGBP", "EURJPY", "EURUSD", "GBPAUD", "GBPJPY", "GBPUSD", "USDJPY"]
tempCurrencies = ["AUDJPY"]
#months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December" ]
#years = ["2007", "2012", "2017"]
tempMonths = ["January", 'February', 'April', 'June', 'August', 'October' ]
tempYears = ["2007"]

with open(binpath, 'r') as fd:
    bin_data = pd.read_csv(fd)
bin_2017 = bin_data[bin_data.Year == 2017]

for cross in tempCurrencies: #AUDJPY, AUDUSD, ...
	for year in tempYears: # 2007, 2012, 2017
		for month in tempMonths: # January, February, ,,,


			# contains path of the dat_file
			dat_file = join(join(join(dat_path, cross), year), year + "_" + month + "_" + cross)
			alphabet = join(join(join(dat_path, cross), year), year + "_" + month + "_" + cross) + ".bin"

			#even though bin is a built in file, there is a variable called bin that holds the values of the 
			# output alphabet and we will override the bin function with that and use it for our alphabet.
			# execfile(alphabet) # the varaible bin is now the output variable
			#bin



			data_prefix = join(join(dat_path, cross), year) + "/"

			Yt_name = year + "_" + month + "_" + cross
			Xt_name = ''

			machine_fname = 'transCSSR_results/+.dot'
			transducer_fname = 'transCSSR_results/+{}.dot'.format(Yt_name)

			stringY = open('{}{}.dat'.format(data_prefix, Yt_name)).readline().strip()
			print '{}{}.dat is opened'.format(data_prefix, Yt_name)

			if Xt_name == '':
			    stringX = '0'*len(stringY)
			else:
			    stringX = open('{}{}.dat'.format(data_prefix, Xt_name)).readline().strip()

			axs = ['0']

			ays = findLetters.getOutputAlphabet( dat_file + ".dat")
			ays.sort()
			print "ays is : "
			print ays

			e_symbols = list(itertools.product(axs, ays)) # All of the possible pairs of emission
			                                              # symbols for (x, y)
			alpha = 0.001
			verbose = False
			L_max_words = 3
			L_max_CSSR  = 3
			assert L_max_CSSR <= L_max_words, "L_max_CSSR must be less than or equal to L_max_words"
			inf_alg = 'transCSSR'
			Tx = len(stringX); Ty = len(stringY)
			assert Tx == Ty, 'The two time series must have the same length.'
			T = Tx

			word_lookup_marg, word_lookup_fut = estimate_predictive_distributions(stringX, stringY, L_max_words)
			epsilon, invepsilon, morph_by_state = run_transCSSR(word_lookup_marg, word_lookup_fut, L_max_CSSR, axs, ays, e_symbols, Xt_name, Yt_name, alpha = alpha, all_digits = True)
			print 'The epsilon-transducer has {} states.'.format(len(invepsilon))
			#print_morph_by_states(morph_by_state, axs, ays, e_symbols)

			graphviz.Source.from_file(transducer_fname)

			stringY_train = stringY[:len(stringY)//2]
			stringY_test  = stringY[len(stringY)//2:]

			stringX_train = '0'*len(stringY_train)
			stringX_test  = '0'*len(stringY_test)

			ays_lookup = {}
			y_labels = []

			for y_ind, y in enumerate(ays):
			    ays_lookup[y] = y_ind
			    y_labels.append(y_ind)

			arrayY = numpy.zeros(len(stringY_test), dtype = 'int16')

			for t, y in enumerate(stringY_test):
			    arrayY[t] = ays_lookup[y]

			word_lookup_marg, word_lookup_fut = estimate_predictive_distributions(stringX_train, stringY_train, L_max_words)

			log_loss_by_L = []

			Ls = range(1, L_max_CSSR+1)

			for L in Ls:
			    epsilon, invepsilon, morph_by_state = run_transCSSR(word_lookup_marg, word_lookup_fut, L, axs, ays, e_symbols, Xt_name, Yt_name, alpha = alpha, all_digits = True)
			    
			    try:
			        pred_probs_by_time, cur_states_by_time = filter_and_pred_probs(stringX_test, stringY_test, machine_fname, transducer_fname, axs, ays, inf_alg)
			        log_loss_by_L.append(log_loss(y_pred=pred_probs_by_time, y_true=arrayY[:-1], labels = y_labels))
			    except:
			        log_loss_by_L.append(numpy.nan)
			    
			    print('Using L = {}, the Log-Loss is {}.'.format(L, log_loss_by_L[-1]))

			L_opt = Ls[numpy.nanargmin(log_loss_by_L)]

			print('Train / Test split with log-loss chooses L_opt = {}'.format(L_opt))

			word_lookup_marg, word_lookup_fut = estimate_predictive_distributions(stringX, stringY, L_opt)
			epsilon, invepsilon, morph_by_state = run_transCSSR(word_lookup_marg, word_lookup_fut, L_opt, axs, ays, e_symbols, Xt_name, Yt_name, alpha = alpha, all_digits = True)

			L_max_ict = 20

			HLs, hLs, hmu, ELs, E, Cmu, etas_matrix = compute_ict_measures(transducer_fname, ays, inf_alg, L_max = L_max_ict)

			print('Cmu      = {}\nH[X_{{0}}] = {}\nhmu      = {}\nE        = {}'.format(Cmu, HLs[0], hmu, E))


			with open(savepath + "/" + cross + ".result", "a+") as myfile:
				myfile.write('{},{},{},{},{},{},{},{},{}\n'.format((Yt_name + ".dat"), cross, year, month, len(invepsilon), Cmu, HLs[0], hmu, E))
				#myfile.write('states      = {}\n'.format(len(invepsilon)))
    			#myfile.write('Cmu      = {}\nH[X_{{0}}] = {}\nhmu      = {}\nE        = {}'.format(Cmu, HLs[0], hmu, E))


			print "finished the file " + dat_file + " at "
			print asctime(localtime())

 

		#run the script on the month

		#save the output, and the state, to a file

		#print the time and maybe the file so you know what yo uare doing








			
