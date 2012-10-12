'''
Utilities to parse pyrate.conf and PyRate general config files

Created on 17/09/2012
@author: bpd900
'''

import numpy
from numpy import unique, reshape, histogram

from shared import Ifg, IfgException, PyRateException
from ifgconstants import X_FIRST, Y_FIRST, WIDTH, FILE_LENGTH, X_STEP, Y_STEP


# constants for lookups
NUMBER_OF_SETS = 'nsets'
IFG_FILE_LIST = 'ifgfilelist'
OBS_DIR = 'obsdir'
OUT_DIR = 'outdir'
NUM_SETS = 'nsets'
SIM_DIR = 'simdir'
AMPLITUDE_FLAG = 'ampflag'
PERP_BASELINE_FLAG = 'basepflag'

IFG_CROP_OPT = 'ifgcropopt' # 1: minimum, 2: maximum, 3: customize, 4: all ifms already same size
IFG_LKSX = 'ifglksx'
IFG_LKSY = 'ifglksy'

IFG_XFIRST = 'ifgxfirst'
IFG_XLAST = 'ifgxlast'
IFG_YFIRST = 'ifgyfirst'
IFG_YLAST = 'ifgylast'


# Lookup to help convert args to correct type/defaults
# format is    key : (conversion, default value)
# None = no conversion
PARAM_CONVERSION = { OBS_DIR : (None, "obs"),
					IFG_FILE_LIST : (None, "ifg.list"),
					OUT_DIR : (None, "out"),
					PERP_BASELINE_FLAG : (bool, True),
					AMPLITUDE_FLAG : (bool, False),
					NUM_SETS : (int, 1),
					IFG_CROP_OPT : (int, None),
					IFG_LKSX : (int, 0),
					IFG_LKSY : (int, 0),
					IFG_XFIRST : (float, None),
					IFG_XLAST : (float, None),
					IFG_YFIRST : (float, None),
					IFG_YLAST : (float, None),
				}


def parse_conf_file(conf_file):
	"""Returns a dict for the key:value pairs from the .conf file"""
	with open(conf_file) as f:
		txt = f.read().splitlines()
		lines = [line.split() for line in txt if line != "" and line[0] not in "%#"]
		lines = [(e[0].rstrip(":"), e[1]) for e in lines] # strip colons from keys
		parameters = dict(lines)
		_parse_pars(parameters)
		return parameters


def _parse_pars(pars):
	"""Parses and converts config file params from text"""
	for k in PARAM_CONVERSION.keys():
		if pars.has_key(k):
			conversion_func = PARAM_CONVERSION[k][0]
			if conversion_func:
				pars[k] = conversion_func(pars[k])
		else:
			# revert empty options to default value
			pars[k] = PARAM_CONVERSION[k][1]

	return pars


def parse_namelist(nml):
	"""Parses name list file into array of paths"""
	with open(nml) as f:
		return [ln.strip() for ln in f.readlines() if ln != ""]



class EpochList(object):
	'''TODO'''

	def __init__(self, date=None, repeat=None, span=None):
		self.date = date
		self.repeat = repeat
		self.span = span


def get_epochs(ifgs):
	masters = [i.MASTER for i in ifgs]
	slaves = [i.SLAVE for i in ifgs]

	combined = masters + slaves
	dates, n = unique(combined, False, True)
	repeat, _ = histogram(n, bins=len(set(n)))

	# absolute span for each date from the zero/start point
	span = [ (dates[i] - dates[0]).days / 365.25 for i in range(len(dates)) ]
	return EpochList(dates, repeat, span)


def prepare_ifgs(ifgs, params, conversion=None, amplitude=None, projection=None):
	'''TODO: partial port of the ugly prepifg.m code'''
	res = _check_xy_extents(ifgs)
	if res is not True:
		msg = res + " unequal for supplied interferograms"
		raise IfgException(msg)

	# handle conversion, line of sight etc of the data?


def _check_xy_extents(ifgs):
	'''Validates data extents, origin and pixel sizes for given interferograms.
	Returns True if extents match, otherwise name of mismatching element.'''
	for var in [X_FIRST, Y_FIRST, WIDTH, FILE_LENGTH, X_STEP, Y_STEP]:
		values = numpy.array([getattr(i, var) for i in ifgs])
		if not (values == values[0]).all():
			return var

	return True