import math
import decimal
from datetime import datetime
from collections import defaultdict

from utils import *
from constants import *

# read file, process trace, output to excel
def process_trace(input_file_name, start_idx=str(0), end_idx=str('np.inf')) :
	'''
	process vc or cc trace data in .asc file with 3 data columns:

		Sweep_1_2_1,  6.114596920E+04, 16:59:05.969, "YLP"
		"Index", "Time[s]"       , "I-mon[A]"      
		0,  0.000000000E+00,  4.461249078E-12
	
	`Sweep` line is required for process.
	
	start_idx, end_idx: used to subset trace if full trace not needed
	'''
	process_started = False
	storage = {}
	sweep_ids = []
	
	output_file_name = input_file_name.split("/")[-1].replace("asc", "xlsx")
	with open(input_file_name, encoding="utf-8") as file:
		for line in file.readlines():
			line = line.split(',')
			# `Sweep` marks the start of a trace
			if line[0].find('Trace') != -1 or line[0].find('Sweep') != -1: #'Sweep' -> 'Trace' for single trace export
				process_started = False
				curr_sweep = line[0]
				sweep_ids.append(line[0])
				continue
			# set cc bool. for unit conversion
			if line[0].find("Index") != -1 :
				cc = True if line[2].find('V-mon') != -1 else False
				continue

			time_idx = line[0].strip()
			if time_idx == end_idx:
				process_started = False
				continue
			if time_idx == start_idx:
				process_started = True
			
			if process_started:
				try:
					time_stamp = decimal.Decimal(line[1]) * 1000 # convert to ms
					val = decimal.Decimal(line[2]) 
					val = val * 1000 if cc else val * decimal.Decimal(1e+9) # cc: convert to mV, vc: convert to nA
					if time_stamp not in storage:
						storage[time_stamp] = {curr_sweep: val}
					else :
						storage[time_stamp][curr_sweep] = val
				except IndexError:
					continue
		
		write_to_excel(output_file_name, storage, sweep_ids=sweep_ids)


# read file, process data, output to excel
def process_data(input_file_name) :
	'''
	process vc or cc data in .txt file with 2-4 data columns:

		SERIES_2_2, "tivPPbefore", 03-Jul-2023, 11:13:03.494, 00:03:01.932, "1uM TTX"
		EPC10, V-Clamp,  9.4841E-12,  2.3655E+06,  8.5450E+01
		Sweep #,     Ampl3[V],  peak - init,   end - init
					1,  -1.2000E-01,  -5.9854E-11,   1.1365E-11

	both `SERIES` and `Sweep` line is required for process.
	`EPC10` line can be used for extract metadata of the cell: Cslow), Rseries, ect.
	'''
	series_started, sweep_started = False, False
	storage, protocol_to_cellids = defaultdict(list), defaultdict(list)
	Cslow_ids = []
	curr_protocol = ''
	keyvalDict = {} # dict for extracted value, used by extract_value_to_dict()

	output_file_name = input_file_name.split("/")[-1].replace("txt", "xlsx")
	with open(input_file_name, encoding="utf-8") as file:
		for line in file.readlines() :
			line = line.split(',')			
			# `SERIES_x_y` marks the start of a protocol
			# x: cell_id; y: protocol_id
			# example: SERIES_2_2, "tivPPbefore", 03-Jul-2023, 11:13:03.494, 00:03:01.932, "1uM TTX"
			# extract meta of this cell: cell_id, curr_protocol, Cslow, Rseries (if available), RsUnComp (if available)
			if line[0].find('SERIES') != -1 :
				series_started = True
				curr_protocol = line[1].strip().replace('"', '')
				date = datetime.strptime(line[2].strip(), '%d-%b-%Y').date().strftime('%y%m%d') # parse date
				cell_id = line[0] + "_"  + date
				protocol_to_cellids[curr_protocol].append(cell_id)
			
			# extract cell capacitance (Cslow), Rseries, RsUnComp from certain protocols
			if line[0].find('EPC10') != -1 and curr_protocol in cell_capacitance_protocols :
				key = 47 # dummy num for sorting
				val = 10 ** 12 * decimal.Decimal(line[cell_capacitance_idx]) # in pF
				# try:
				# 	val_Rs = decimal.Decimal(line[cell_Rs_idx])
				# 	val_RsUnComp = 1 - decimal.Decimal(0.01) * decimal.Decimal(line[5]) # convert to fraction
				# except IndexError: # not recorded
				# 	pass
				if (curr_cell := cell_id.split("_")[1]) not in Cslow_ids:
					Cslow_ids.append(curr_cell)
					# Cslow, Rseries, RsUnComp (uncompensated fraction)
					protocol_to_cellids["Cslow"].append(cell_id)
					# protocol_to_cellids["Rs"].append(cell_id)
					# protocol_to_cellids["RsUnComp"].append(cell_id)
					if key not in [pair[0] for pair in storage["Cslow"]] :
						storage["Cslow"].append([key, {cell_id : val}])
					else :
						for pair in storage["Cslow"] :
							if pair[0] == key :
								pair[1][cell_id] = val
							else :
								continue
					# try:
					# 	if key not in [pair[0] for pair in storage["Rs"]] :
					# 		storage["Rs"].append([key, {cell_id : val_Rs}])
					# 	else :
					# 		for pair in storage["Rs"] :
					# 			if pair[0] == key :
					# 				pair[1][cell_id] = val_Rs
					# 			else :
					# 				continue
					# except UnboundLocalError: # not recorded
					# 	pass
					# if key not in [pair[0] for pair in storage["RsUnComp"]] :
					# 	storage["RsUnComp"].append([key, {cell_id : val_RsUnComp}])
					# else :
					# 	for pair in storage["RsUnComp"] :
					# 		if pair[0] == key :
					# 			pair[1][cell_id] = val_RsUnComp
					# 		else :
					# 			continue			
				continue

			# `Sweep` marks the start of recording of sweeps in a protocol
			# example: Sweep #,     Ampl3[V],  peak - init,   end - init
			if line[0].find('Sweep') != -1 :
				sweep_started = True
				continue
			if len(line) == 1 and series_started:
				sweep_started = False
				continue
			# extract key,value pair, convert val according to protocol
			if sweep_started:
				# cc
				if curr_protocol in cc_noStim_protocols:
					extract_value_to_dict(line, 4, 0, keyvalDict)
					key = keyvalDict["val0"]
					val1 = 10 ** 3 * keyvalDict["val3"] # convert to mV
					val2 = int(keyvalDict["val2"]) # AP count	
					# spontaneous AP
					if cell_id not in protocol_to_cellids["Spont"]:
						protocol_to_cellids["Spont"].append(cell_id) # new for each cell
						holding = int(round(val1 / 10)*10) # round holding to nearest 10mV
						if holding not in [pair[0] for pair in storage["Spont"]] :
							storage["Spont"].append([holding, {cell_id : val2}])
						else :
							for pair in storage["Spont"] :
								if pair[0] == holding :
									pair[1][cell_id] = val2
								else :
									continue
				elif curr_protocol == "cc-50mV" : # get AP count of spont @-50mV
					extract_value_to_dict(line, 3, 0, keyvalDict)
					key = keyvalDict["val0"]
					val1 = int(keyvalDict["val2"]) # convert to mV
				elif curr_protocol in cc_inputResistence_protocols:
					extract_value_to_dict(line, 3, 0, keyvalDict)
					key = keyvalDict["val0"]
					if math.isinf(keyvalDict["val2"]):
						val1 = "INF"
					else:
						val1 = keyvalDict["val2"] / (10 ** 9)
				elif curr_protocol in cc_APcount_protocols:
					extract_value_to_dict(line, 2, 1, keyvalDict)
					key = int(round(10 ** 11 * keyvalDict["val0"]) * 10) # round holding to nearest 10pA
					val1 = int(keyvalDict["val1"])
				
				# vc
				elif curr_protocol in vc_persistent_protocols:
					extract_value_to_dict(line, 3, 1, keyvalDict)
					key = int(round(10 ** 3 * keyvalDict["val0"]))
					val1 = keyvalDict["val1"] # convert to nA
					val2 = keyvalDict["val2"] # convert to nA
					# persistent current
					if cell_id not in protocol_to_cellids["Ipersist"] :
						protocol_to_cellids["Ipersist"].append(cell_id) # new for each cell
					if key not in [pair[0] for pair in storage["Ipersist"]] :
						storage["Ipersist"].append([key, {cell_id : val2}])
					else :
						for pair in storage["Ipersist"] :
							if pair[0] == key :
								pair[1][cell_id] = val2
							else :
								continue				
				else : # default
					extract_value_to_dict(line, 2, 1, keyvalDict)
					key = int(round(10 ** 3 * keyvalDict["val0"])) # round holding to nearest 10mV
					val1 = keyvalDict["val1"]
				if key not in [pair[0] for pair in storage[curr_protocol]] :
					storage[curr_protocol].append([key, {cell_id : val1}])
				else :
					for pair in storage[curr_protocol] :
						if pair[0] == key :
							pair[1][cell_id] = val1
						else :
							continue

	write_to_excel(output_file_name, storage, protocol_to_cellids)