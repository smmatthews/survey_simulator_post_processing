#!/usr/bin/python
# Utility functions used in the running of surveySimPP.py.

import logging
import os, sys
import pandas as pd
import configparser
from . import PPOutWriteCSV, PPOutWriteSqlite3, PPOutWriteHDF5

def PPGetLogger(    
        LOG_FORMAT     = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s ',
        LOG_NAME       = '',
        LOG_FILE_INFO  = 'postprocessing.log',
        LOG_FILE_ERROR = 'postprocessing.err'):


    #LOG_FORMAT     = '',
    log           = logging.getLogger(LOG_NAME)
    log_formatter = logging.Formatter(LOG_FORMAT)

    # comment this to suppress console output
    #stream_handler = logging.StreamHandler()
    #stream_handler.setFormatter(log_formatter)
    #log.addHandler(stream_handler)

    file_handler_info = logging.FileHandler(LOG_FILE_INFO, mode='w')
    file_handler_info.setFormatter(log_formatter)
    file_handler_info.setLevel(logging.INFO)
    log.addHandler(file_handler_info)

    file_handler_error = logging.FileHandler(LOG_FILE_ERROR, mode='w')
    file_handler_error.setFormatter(log_formatter)
    file_handler_error.setLevel(logging.ERROR)
    log.addHandler(file_handler_error)

    log.setLevel(logging.INFO)

    return log


def PPGetOrExit(config, section, key, message):
    # from Shantanu Naidu, objectInField
    try:
        return config[section][key]
    except KeyError:
        logging.error(message)
        sys.exit(message)
        
        
#def initialisePostProcessing():
            
        
def PPToBool(value):
    valid = {'true': True, 't': True, '1': True, 'True': True,
             'false': False, 'f': False, '0': False, 'False': False
             }   

    if isinstance(value, bool):
        return value

    if not isinstance(value, str):
        raise ValueError('invalid literal for boolean. Not a string.')

    lower_value = value.lower()
    if lower_value in valid:
        return valid[lower_value]
    else:
        raise ValueError('invalid literal for boolean: "%s"' % value)


def PPConfigFileParser(configfile, pplogger):
	"""
	Author: Steph Merritt
	
	Description: Parses the config file, error-handles, then assigns the values into a single 
	dictionary, which is passed out. Mostly copied out of old version of run script.

	Chose not to use the original ConfigParser object for readability: it's a dict of 
	dicts, so calling the various values can become quite unwieldy.

	This could easily be broken up even more, and probably should be.	
	
	Mandatory input:	string, configfile, string filepath of the config pile
						logger object, pplogger
	
	Output: 			dictionary of variables taken from the config file
	
	"""

	config = configparser.ConfigParser()
	config.read(configfile)

	config_dict = {}
	config_dict['testvalue'] = int(config['GENERAL']['testvalue'])	
	config_dict['pointingFormat'] = PPGetOrExit(config, 'INPUTFILES', 'pointingFormat', 'ERROR: no pointing simulation format is specified.')
	config_dict['filesep'] = PPGetOrExit(config, 'INPUTFILES', 'auxFormat', 'ERROR: no auxilliary data (e.g. colour) format specified.')  

	config_dict['objecttype'] = PPGetOrExit(config, 'OBJECTS', 'objecttype', 'ERROR: no object type provided.')    
	if config_dict['objecttype'] not in ['asteroid', 'comet']:
		pplogger.error('ERROR: objecttype is neither an asteroid or a comet.') 
		sys.exit('ERROR: objecttype is neither an asteroid or a comet.')

	config_dict['pointingdatabase'] = PPGetOrExit(config, 'INPUTFILES', 'pointingdatabase', 'ERROR: no pointing database provided.')
	config_dict['ppdbquery'] = PPGetOrExit(config, 'INPUTFILES', 'ppsqldbquery', 'ERROR: no pointing database SQLite3 query provided.')

	config_dict['mainfilter'] = PPGetOrExit(config,'FILTERS', 'mainfilter', 'ERROR: main filter not defined.')
	config_dict['othercolours'] = [e.strip() for e in config.get('FILTERS', 'othercolours').split(',')]
	config_dict['resfilters'] = [e.strip() for e in config.get('FILTERS', 'resfilters').split(',')]    
	if (len(config_dict['othercolours']) != len(config_dict['resfilters'])-1):
		pplogger.error('ERROR: mismatch in input config colours and filters: len(othercolours) != len(resfilters) - 1')
		sys.exit('ERROR: mismatch in input config colours and filters: len(othercolours) != len(resfilters) - 1')
	if config_dict['mainfilter'] != config_dict['resfilters'][0]:
		pplogger.error('ERROR: main filter should be the first among resfilters.')
		sys.exit('ERROR: main filter should be the first among resfilters.') 
	 
	config_dict['phasefunction'] = PPGetOrExit(config,'PHASE', 'phasefunction', 'ERROR: phase function not defined.')
	config_dict['trailingLossesOn'] = PPToBool(config['PERFORMANCE']['trailingLossesOn'])

	config_dict['cameraModel'] = PPGetOrExit(config, 'PERFORMANCE', 'cameraModel', 'ERROR: camera model not defined.')	
	if config_dict['cameraModel'] not in ['circle', 'footprint']:
		pplogger.error('ERROR: cameraModel should be either circle or footprint.')
		sys.exit('ERROR: cameraModel should be either circle or footprint.')        
	elif (config_dict['cameraModel'] == 'footprint'):
		config_dict['footprintPath'] = PPGetOrExit(config, 'INPUTFILES', 'footprintPath', 'ERROR: no camera footprint provided.')
   
	config_dict['SSPDetectionEfficiency'] = float(config['FILTERINGPARAMETERS']['SSPDetectionEfficiency'])
	if (config_dict['SSPDetectionEfficiency'] > 1.0 or config_dict['SSPDetectionEfficiency'] > 1.0 or isinstance(config_dict['SSPDetectionEfficiency'],(float,int))==False):
		pplogger.error('ERROR: SSP detection efficiency out of bounds (should be between 0 and 1.), or not a number.')
		sys.exit('ERROR: SSP detection efficiency out of bounds (should be between 0 and 1.), or not a number.')

	# check that these are sensible values?
	config_dict['fillfactor'] = float(config['FILTERINGPARAMETERS']['fillfactor'])
	config_dict['brightLimit'] = float(config['FILTERINGPARAMETERS']['brightLimit'])
	config_dict['inSepThreshold'] = float(config['FILTERINGPARAMETERS']['inSepThreshold'])

	config_dict['minTracklet'] = int(config['FILTERINGPARAMETERS']['minTracklet'])    
	if (config_dict['minTracklet'] < 1 or isinstance(config_dict['minTracklet'],int)==False):
		pplogger.error('ERROR: minimum length of tracklet is zero or negative, or not an integer.')
		sys.exit('ERROR: minimum length of tracklet is zero or negative, or not an integer.')
	
	config_dict['noTracklets'] = int(config['FILTERINGPARAMETERS']['noTracklets'])
	if (config_dict['noTracklets']  < 1 or isinstance(config_dict['noTracklets'], int)== False):
		pplogger.error('ERROR: number of tracklets is zero or less, or not an integer.')
		sys.exit('ERROR: number of tracklets is zero or less, or not an integer.')

	config_dict['trackletInterval'] = float(config['FILTERINGPARAMETERS']['trackletInterval'])
	if (config_dict['trackletInterval'] <= 0.0 or isinstance(config_dict['trackletInterval'],(float,int))==False):
		pplogger.error('ERROR: tracklet appearance interval is negative, or not a number.')
		sys.exit('ERROR: tracklet appearance interval is negative, or not a number.')
	
	config_dict['outpath'] = PPGetOrExit(config, 'OUTPUTFORMAT', 'outpath', 'ERROR: out path not specified.')   
	config_dict['outfilestem'] = PPGetOrExit(config, 'OUTPUTFORMAT', 'outfilestem', 'ERROR: name of output file stem not specified.')    

	config_dict['outputformat'] = PPGetOrExit(config, 'OUTPUTFORMAT', 'outputformat', 'ERROR: output format not specified.')   
	if config_dict['outputformat'] not in ['csv', 'sqlite3', 'hdf5', 'HDF5', 'h5']:
		pplogger.error('ERROR: output format should be either csv, sqlite3 or hdf5.')
		sys.exit('ERROR: output format should be either csv, sqlite3 or hdf5.')

	config_dict['separatelyCSV'] = PPToBool(config['OUTPUTFORMAT']['separatelyCSV'])
	config_dict['sizeSerialChunk'] = int(config['GENERAL']['sizeSerialChunk'])

	return config_dict


def PPPrintConfigsToLog(configs, pplogger):
	"""
	Author: Steph Merritt
	
	Description: Prints all the values from the config file to the log. Copied out of the runscript.
	
	Mandatory input:	dict, configs, dictionary of config variables created by PPConfigFileParser
						logger object, pplogger, logger object
						
	Output: none
	
	"""

	pplogger.info('Object type is ' + str(configs['objecttype']))

	pplogger.info('Pointing simulation result format is: ' + configs['pointingFormat']) 
	pplogger.info('Pointing simulation result path is: ' + configs['pointingdatabase'])
	pplogger.info('Pointing simulation result required query is: ' +  configs['ppdbquery']) 

	pplogger.info('The main filter in which brightness is defined is ' + configs['mainfilter'])
	othcs=' '.join(str(e) for e in configs['othercolours'])
	pplogger.info('The colour indices included in the simulation are ' + othcs)
	rescs=' '.join(str(f) for f in configs['resfilters'])
	pplogger.info('Hence, the filters included in the post-processing results are ' + rescs)

	pplogger.info('The apparent brightness is calculated using the following phase function model: ' + configs['phasefunction'])
	
	if (configs['trailingLossesOn'] == True):
		pplogger.info('Computation of trailing losses is switched ON.')
	else:
		pplogger.info('Computation of trailing losses is switched OFF.')

	if (configs['cameraModel'] == 'footprint'):
		pplogger.info('Footprint is modelled after the actual camera footprint.')
		pplogger.info('loading camera footprint from ' + configs['footprintPath'])
	else:
		pplogger.info('Footprint is circular')

	pplogger.info('Simulated SSP detection efficiency is ' + str(configs["SSPDetectionEfficiency"]))
	pplogger.info('The filling factor for the circular footprint is ' + str(configs["fillfactor"]))
	pplogger.info('The upper (saturation) limit is ' + str(configs['brightLimit']))
	pplogger.info('For Solar System Processing, the minimum required number of observatrions in a tracklet is ' + str(configs['minTracklet']))
	pplogger.info('For Solar System Processing, the minimum required number of tracklets is' + str(configs['noTracklets']))
	pplogger.info('Fos Solar System Processing, the maximum interval of time in days of tracklets to be contained in is ' + str(configs['trackletInterval']))
	pplogger.info('For Solar System Processing, the minimum angular separation between observations in arcseconds is ' + str(configs['inSepThreshold']))


def PPFindFileOrExit(arg_fn, argname):
	"""
	Author: Steph Merritt
	
	Description: Checks to see if the filename given by arg_fn actually exists. If it doesn't,
	this fails gracefully and exits to the command line.
	
	Mandatory input:	string, arg_fn, string filename passed by command line argument
						string, argname,  name/flag of the argument printed in error message
	
	Output:				string, arg_fn unchanged
	
	"""

	if os.path.exists(arg_fn):
		return arg_fn
	else:
		logging.error('ERROR: filename {} supplied for {} argument does not exist.'.format(arg_fn, argname))
		sys.exit('ERROR: filename {} supplied for {} argument does not exist.'.format(arg_fn, argname))
	

def PPCMDLineParser(parser):
	"""
	Author: Steph Merritt
	
	Description: Parses the command line arguments, makes sure the filenames given actually exist,
	then stores them in a single dict.
	
	Will only look for the comet parameters file if it's actually given at the command line.
	
	Mandatory input:	ArgumentParser object, parser, of command line arguments
	
	output:				dictionary of variables taken from command line arguments
	
	"""

	args = parser.parse_args()

	cmd_args_dict = {}
	
	cmd_args_dict['colourinput'] = PPFindFileOrExit(args.l, '-c --colour')
	cmd_args_dict['orbinfile'] = PPFindFileOrExit(args.o, '-o --orbit')
	cmd_args_dict['oifoutput'] = PPFindFileOrExit(args.p, '-p, --pointing')
	cmd_args_dict['configfile'] = PPFindFileOrExit(args.c, '-c, --config')
	
	if args.m: cmd_args_dict['cometinput'] = PPFindFileOrExit(args.m, '-m, --comet') 
    
	cmd_args_dict['makeIntermediatePointingDatabase']=bool(args.d)

	return cmd_args_dict
	
	
def PPWriteOutput(configs, observations, pplogger, endChunk):
	"""
	Author: Steph Merritt
	
	Description: Writes out the output in the format specified in the config file.
	
	Mandatory input:	dict, configs, dictionary of config variables created by PPConfigFileParser
						pandas DataFrame, observations, table of observations for output
						logger object, pplogger, logger object
	"""
	
	pplogger.info('Constructing output path...')
	if (configs['outputformat'] == 'csv'):
		outputsuffix='.csv'
		if (configs['separatelyCSV'] == True):
			objid_list = observations['ObjID'].unique().tolist() 
			pplogger.info('Output to ' + str(len(objid_list)) + ' separate output CSV files...')
			i=0
			while(i<len(objid_list)):
				 single_object_df=pd.DataFrame(observations[observations['ObjID'] == objid_list[i]])
				 out=configs['outpath'] + str(objid_list[i]) + '_' + configs['outfilestem'] + outputsuffix
				 obsi=PPOutWriteCSV.PPOutWriteCSV(single_object_df,out)
				 i=i+1
		else:
			out= configs['outpath'] + configs['outfilestem'] + outputsuffix
			pplogger.info('Output to CSV file...')
			observations=PPOutWriteCSV.PPOutWriteCSV(observations,out)
	
	elif (configs['outputformat'] == 'sqlite3'):
		outputsuffix='.db'
		out= configs['outpath'] + configs['outfilestem'] + outputsuffix
		pplogger.info('Output to sqlite3 database...')
		observations=PPOutWriteSqlite3.PPOutWriteSqlite3(observations,out)   
	elif (configs['outputformat'] == 'hdf5' or configs['outputformat']=='HDF5'):
		outputsuffix=".h5"   
		out=configs['outpath'] + configs['outfilestem'] + outputsuffix
		pplogger.info('Output to HDF5 binary file...')
		observations=PPOutWriteHDF5.PPOutWriteHDF5(observations,out,str(endChunk))    
	
