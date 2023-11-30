import os
import glob
import math
import math
import decimal
import xlsxwriter
from datetime import datetime
from collections import defaultdict

# default protocols, extract 2, keyPos 1: extract_value_to_dict(line, 2, 1, keyvalDict)
# persistent current protocol: extract 3, keyPos 1 : extract_value_to_dict(line, 3, 1, keyvalDict)
# extractNumcc_APcount_protocols: extract 2, keyPos 1


cell_capacitance_idx, cell_Rs_idx, cell_Rcomp_idx = 2, 3, 4
""" 
index number determined by exported notebook
examples:
'EPC10, V-Clamp,  1.0364E-11,  2.6536E+06,  8.0504E+01'
	order of line[2], line[3], line[4]: Cslow, Rs, Rcomp
'EPC10, V-Clamp,  1.0000E-03,  1.5974E-11,  1.4597E+06,  8.4989E+01'
	order of line[3], line[4], line[5]: Cslow, Rs, Rcomp 
"""
cell_capacitance_protocols = ["CC", "tivPPbefore"]
cc_noStim_protocols = ["cc-noST", "CC"]
cc_inputResistence_protocols = ["cc-input R", "input2"]
cc_APcount_protocols = ["cc2", "cc10", "cc-short", "cc-short2", "cc-ramp50", "cc-ramp10", # RGC
												"CC", "CC2", "CC3", "sAP 1ms", "CC3-2", "sAP 1ms-2" # DRG
												] 
vc_persistent_protocols = ["tivPPbefore", "tiv-200ms", "tivPPbefore-200ms"]

# extract value from line & store in keyvalDic
def extract_value_to_dict(inputLine, extractNum, keyPos, keyvalDict) : 
	"""
	extractNum: number of key+values to extract
	keyPos: position of key in inputLine
	keyvalDict: container for extracted values  
	"""
	keyvalDict.clear()
	for i in range (extractNum) :
		keyvalDict[f"val{i}"] = decimal.Decimal(inputLine[keyPos+i])

# read file, process data, output to excel
def process_data(input_file_name) :
	series_started, sweep_started = False, False
	protocols, protocol_to_cellids = defaultdict(list), defaultdict(list)
	Cslow_ids = []
	curr_protocol = ''
	keyvalDict = {} # dict for extracted value
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
					if key not in [pair[0] for pair in protocols["Cslow"]] :
						protocols["Cslow"].append([key, {cell_id : val}])
					else :
						for pair in protocols["Cslow"] :
							if pair[0] == key :
								pair[1][cell_id] = val
							else :
								continue
					# try:
					# 	if key not in [pair[0] for pair in protocols["Rs"]] :
					# 		protocols["Rs"].append([key, {cell_id : val_Rs}])
					# 	else :
					# 		for pair in protocols["Rs"] :
					# 			if pair[0] == key :
					# 				pair[1][cell_id] = val_Rs
					# 			else :
					# 				continue
					# except UnboundLocalError: # not recorded
					# 	pass
					# if key not in [pair[0] for pair in protocols["RsUnComp"]] :
					# 	protocols["RsUnComp"].append([key, {cell_id : val_RsUnComp}])
					# else :
					# 	for pair in protocols["RsUnComp"] :
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
					# extract_value_to_dict(inputLine, extractNum, keyPos, keyvalDict)
					extract_value_to_dict(line, 4, 0, keyvalDict) # DRG
					key = keyvalDict["val0"]
					val1 = 10 ** 3 * keyvalDict["val3"] # convert to mV
					val2 = int(keyvalDict["val2"]) # AP count	
					# spontaneous AP
					if cell_id not in protocol_to_cellids["Spont"]:
						protocol_to_cellids["Spont"].append(cell_id) # new for each cell
						holding = int(round(val1 / 10)*10) # round holding to nearest 10mV
						if holding not in [pair[0] for pair in protocols["Spont"]] :
							protocols["Spont"].append([holding, {cell_id : val2}])
						else :
							for pair in protocols["Spont"] :
								if pair[0] == holding :
									pair[1][cell_id] = val2
								else :
									continue
				elif curr_protocol == "cc-50mV" : # get AP count of spont @-50mV
					extract_value_to_dict(line, 3, 0, keyvalDict)
					key = keyvalDict["val0"]
					val1 = int(keyvalDict["val2"]) # convert to mV
				elif curr_protocol in cc_inputResistence_protocols:
					extract_value_to_dict(line, 3, 0, keyvalDict) #inputLine, extractNum, keyPos, keyvalDict
					key = keyvalDict["val0"]
					if math.isinf(keyvalDict["val2"]):
						val1 = "INF"
					else:
						val1 = keyvalDict["val2"] / (10 ** 9) # DRG?
				elif curr_protocol in cc_APcount_protocols:
					extract_value_to_dict(line, 2, 1, keyvalDict)
					key = int(round(10 ** 11 * keyvalDict["val0"]) * 10) # round holding to nearest 10pA
					val1 = int(keyvalDict["val1"])
				
				# vc
				elif curr_protocol in vc_persistent_protocols:
					extract_value_to_dict(line, 3, 1, keyvalDict) # change (inputLine, extractNum, keyPos, keyvalDict) for older files
					key = int(round(10 ** 3 * keyvalDict["val0"]))
					val1 = keyvalDict["val1"] # convert to nA
					val2 = keyvalDict["val2"] # convert to nA
					# persistent current
					if cell_id not in protocol_to_cellids["Ipersist"] :
						protocol_to_cellids["Ipersist"].append(cell_id) # new for each cell
					if key not in [pair[0] for pair in protocols["Ipersist"]] :
						protocols["Ipersist"].append([key, {cell_id : val2}])
					else :
						for pair in protocols["Ipersist"] :
							if pair[0] == key :
								pair[1][cell_id] = val2
							else :
								continue				
				else : # default
					extract_value_to_dict(line, 2, 1, keyvalDict)
					key = int(round(10 ** 3 * keyvalDict["val0"])) # # round holding to nearest 10mV
					val1 = keyvalDict["val1"]
				if key not in [pair[0] for pair in protocols[curr_protocol]] :
					protocols[curr_protocol].append([key, {cell_id : val1}])
				else :
					for pair in protocols[curr_protocol] :
						if pair[0] == key :
							pair[1][cell_id] = val1
						else :
							continue

	write_to_excel(output_file_name, protocols, protocol_to_cellids)

# write processed data to excel
def write_to_excel(out_fname, protocols, protocol_cellids):
	# Create an new Excel file and add a worksheet.
	path = os.getcwd() + "/../output/"
	workbook = xlsxwriter.Workbook(path+out_fname)
	worksheet = workbook.add_worksheet()

	# output
	currRow = 0
	for protocol, _ in protocols.items() : 
		currCol = 0
		worksheet.write(currRow, currCol, protocol)
		currCol += 1
		cellIndices = protocol_cellids[protocol]

		for i in range(len(cellIndices)) :
			worksheet.write(currRow, currCol, cellIndices[i])
			currCol += 1
		currRow += 1
		
		# sort by key
		arr = protocols[protocol]
		arr = [[float(i[0]), i[1]] for i in arr]
		arr = sorted(arr, key=lambda l:l[0])

		for pair in arr :
			key = pair[0]
			val = pair[1]
			currCol = 0
			worksheet.write(currRow, currCol, key)
			currCol += 1
			for i in range(len(protocol_cellids[protocol])) :
				index = protocol_cellids[protocol][i]
				if index not in val.keys() :
					worksheet.write(currRow, currCol, '')
				else :
					output = val[index]
					try:
						worksheet.write(currRow, currCol, output)
					except TypeError:
						worksheet.write(currRow, currCol, str(output))
				currCol += 1
			currRow += 1
		currRow += 1

	workbook.close()

# process all data file in the directory
path = os.getcwd() + "/../data/"
# os.chdir(path)
for file in glob.glob(path+'*.txt'):
	process_data(file)
	fname = file.split("/")[-1]
	print(f"{fname}\t proccessed")





