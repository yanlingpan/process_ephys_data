import decimal
import math
import os
import glob

def writeProtocolLine(protocol) :
	line = protocol + ' : '
	line = line + "\n"
	return line

def writeDataLine(key, val) :
	line = key
	for i in range(len(val)) :
		line = line + ' ' + val[i]
	line = line + "\n"
	return line

def processData(filename) :
	inputFile = filename
	outputFile = inputFile.replace("asc", "xlsx")
	file = open(inputFile)
	memorize = False
	###started = False; # to mark the start of an "SERIES"
	###protocols = {} # data stored here {'protocol':[['voltageData',{'cellIndex': 'currentData'}],...]...}
	storage = {} # THE place data goes in, just as the protocol in the above line
	### currProtocol = ''
	recording = False;
	sweepIndices = []
	for line in file.readlines(): # read one line at a time as a string
		#print("what readlines() do:", line)
		
		# str.split() Return a list of the words in the string, using sep as the 
		# delimiter string
		line = str.split(line, ',')
		#print("after split", line)
		
		# # if protocal definition
		# ### if line[0].find('SERIES') != -1 :
		# # Return the lowest index in line[0] where the substring 'SERIES' is found. 
		# # Return -1 on failure.  
		# 	started = True # mark SERIES started
		# 	### currProtocol = line[1] # "tivPPbefore"
		# 	cellIndex = line[0] # "SERIES_1_1"
		# 	# remove quotes and spaces (can i do this?)
		# 	### currProtocol = currProtocol.replace(' ', '')
		# 	### currProtocol = currProtocol.replace('"', '')
			# if currProtocol not in protocol_index.keys() :
			# 	protocol_index[currProtocol] = [] # why as a list?
			# protocol_index[currProtocol].append(cellIndex)
		
		# extract capacitance (last str) from the line starting with "EPC10"

		# if sweep ### don't even need if sweep?
		if line[0].find('Trace') != -1 or line[0].find('Sweep') != -1: #'Sweep' -> 'Trace' for single trace export
			recording = True # to mark the start of a series of "Sweep" in an "SERIES"
			current_sweep = line[0]
			sweepIndices.append(line[0])
			continue

		# if index ### only memorize index 61-402 
		# if line[0].find('603') != -1 : # end memorizing:: the number is the line you want to stop getting the data 
		if line[0].find('15999') != -1 : # end memorizing:: 650ms 
			memorize = False # to mark the start of a series of "Sweep" in an "SERIES"
			continue # get out of the loop and start finding another 'Sweep'
		else:
			linestrip = line[0].replace(' ', '')
			#print linestrip

		# if linestrip == '4500': # start memorizeing:: the number is the line you want to start collecting the data
		# if linestrip == '0': # start memorizeing:: 60ms
		if linestrip == '1600': 
			memorize = True
		# if recording
		if memorize == True:
			key = float(line[1]) * 1000 # convert to ms
			val = float(line[2]) * 1000 # convert to mV
			if key not in storage:
				storage[key] = {current_sweep: val}
			else : # another cell recorded [currProtocol] with the same key(voltage)
				for index in storage:
					if index == key :
						storage[index][current_sweep] = val # generate KeyError
					else : # next loop if not the corrent voltage pair[0]
						continue
				#break
				
	import xlsxwriter

	# Create an new Excel file and add a worksheet.
	workbook = xlsxwriter.Workbook(outputFile)
	worksheet = workbook.add_worksheet()

	# output
	currRow = 0
	currCol = 1 # start writing sweep_index on 2nd column, 1st column reserved for index writing
	for i in range(len(sweepIndices)) : 
		worksheet.write(currRow, currCol, sweepIndices[i])
		currCol += 1
	currRow += 1
	# sort according to voltage (key) ### is this absolutely necessary??
	arr = storage
	arr = [[index, arr[index]] for index in arr] # cast index as int for sorting? or not necessary?
	arr = sorted(arr, key=lambda l:l[0])

	for pair in arr :
		key = pair[0]
		val = pair[1]

		currCol = 0
		worksheet.write(currRow, currCol, key)
		currCol += 1
		for i in range(len(sweepIndices)) : # #of column to write
			sweepindexx = sweepIndices[i]
			if sweepindexx not in val.keys() : ### what's this for???
				worksheet.write(currRow, currCol, '')
			else :
				output = val[sweepindexx]
				worksheet.write(currRow, currCol, output)
			currCol += 1
		currRow += 1
	currRow += 1

	workbook.close()

# process all data file in the directory
path = os.getcwd() + "/data"
os.chdir(path)
for filename in glob.glob('*.asc'):
# for filename in os.listdir(path):
	processData(filename)

