import numpy
import scipy.stats
import itertools
import copy
import string
from os import listdir, getcwd, pardir, makedirs
from os import name as os_name
from os.path import isfile, isdir, join, splitext, basename, abspath, exists

from collections import Counter, defaultdict
from filter_data_methods import *
from igraph import *

from transCSSR import *

#Data paths
cwd = getcwd()
parent = abspath(join(cwd, pardir))
cssr_datapath = join(parent, 'dat_files')
cssr_filename = '2007_April_AUDJPY.dat'
cssr_filepath = join(cssr_datapath, cssr_filename)

#Global variables
ALPHABET_SIZE = 20

# Yt is the output. Xt should be set to the null string.

data_prefix = ''

# Yt_name = 'coinflip_through_even'
# Yt_name = 'coinflip_through_evenflip'
# Yt_name = 'coinflip_through_periodickick'
# Yt_name = 'coinflip_through_periodicevenkick'
# Yt_name = 'even_through_even'
# Yt_name = 'even'
# Yt_name = 'rip'
# Yt_name = 'rip-rev'
# Yt_name = 'barnettY'
# Yt_name = 'even-excite_w_refrac'
# Yt_name = 'coinflip-excite_w_refrac'
# Yt_name = 'coinflip'
# Yt_name = 'period4'
# Yt_name = 'golden-mean'
# Yt_name = 'golden-mean-rev'
# Yt_name = 'complex-csm'
# Yt_name = 'tricoin_through_singh-machine'
# Yt_name = 'coinflip_through_floatreset'
Yt_name = cssr_filename

Xt_name = ''

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#
# Load in the data for each process.
#
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

#stringY = open('/home/james/Desktop/git-folder/stock-market/data/dat-files-months/AUDJPY/2007/{}{}.dat'.format(data_prefix, Yt_name)).readline().strip()
stringY = cssr_filepath

if Xt_name == '':
	stringX = '0'*len(stringY)
else:
	stringX = open('data/{}{}.dat'.format(data_prefix, Xt_name)).readline().strip()

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#
# Set the parameters and associated quantities:
# 	axs, ays -- the input / output alphabets
# 	alpha    -- the significance level associated with
# 	            CSSR's hypothesis tests.
# 	L        -- The maximum history length to look
#               back when inferring predictive
#               distributions.
#
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

axs = ['0']
#ays = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', ':', ';', '<', '=', '>', '?', '@', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
ays = [chr(ord('a') + i) for i in range(0,ALPHABET_SIZE)]

e_symbols = list(itertools.product(axs, ays)) # All of the possible pairs of emission
                                              # symbols for (x, y)

alpha = 0.001

verbose = False

# L is the maximum amount we want to ever look back.

L_max = 15

Tx = len(stringX); Ty = len(stringY)

assert Tx == Ty, 'The two time series must have the same length.'

T = Tx

word_lookup_marg, word_lookup_fut = estimate_predictive_distributions(stringX, stringY, L_max)

epsilon, invepsilon, morph_by_state = run_transCSSR(word_lookup_marg, word_lookup_fut, L_max, axs, ays, e_symbols, Xt_name, Yt_name, alpha = alpha, is_eM = True)

print 'The epsilon-transducer has {} states.'.format(len(invepsilon))

print_morph_by_states(morph_by_state)

filtered_states, filtered_probs, stringY_pred = filter_and_predict(stringX, stringY, epsilon, invepsilon, morph_by_state, axs, ays, e_symbols, L_max)

word = '11'

p_L = compute_word_probability_eM(word, 'transCSSR_results/+{}.dot'.format(Yt_name), ays, 'transCSSR')

L_word = 3

L_pow = 2**L_word

p_tot = 0

for i_word in range(L_pow):
	xs = format(i_word, '0{}b'.format(L_word))
	
	p_word = compute_word_probability_eM(xs, 'transCSSR_results/{}+{}.dot'.format(Xt_name, Yt_name), axs, 'transCSSR')
	
	print xs, p_word
	
	p_tot += p_word

print 'All words sum to {}...'.format(p_tot)