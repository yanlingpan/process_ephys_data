import os
import decimal
import xlsxwriter

def write_to_excel(output_fpath, storage, protocol_cellids=None, sweep_ids=None):
		# Create an new Excel file and add a worksheet.
		print(f"\n{'#'*50}\n{output_fpath}\n{'#'*50}\n")
		# # full = "D:\code\process_ephys_data\processed\20200226-RGC-cc-ctrl2-13-5-4-cc6-2AP.xlsx"
		# # workbook = xlsxwriter.Workbook(full)
		# output_fpath = os.path.abspath(output_fpath)
		print(f"\n{'DDD#'*50}\n{os.path.dirname(output_fpath)}\n{'#'*50}\n")
		print(os.path.split(output_fpath))
		assert os.path.exists(os.path.split(output_fpath)[0])
		workbook = xlsxwriter.Workbook(output_fpath)
		worksheet = workbook.add_worksheet()
		# workbook.close()

		# output
		currRow = 0
		if sweep_ids is not None: # write trace
			currCol = 1
			for i in range(len(sweep_ids)) : # sweep ids
				worksheet.write(currRow, currCol, sweep_ids[i])
				currCol += 1
			currRow += 1
			# sort by key
			arr = storage
			arr = [[idx, arr[idx]] for idx in arr]
			write_sorted_arr(worksheet, currRow, currCol, arr, sweep_ids)
		else: # write protocols
			for protocol, _ in storage.items() : 
				currCol = 0
				worksheet.write(currRow, currCol, protocol)  # protocol name
				currCol += 1
				for i in range(len(cell_ids := protocol_cellids[protocol])) :  # cell ids
					worksheet.write(currRow, currCol, cell_ids[i])
					currCol += 1
				currRow += 1
				# sort by key
				arr = storage[protocol]
				arr = [[float(i[0]), i[1]] for i in arr]
				write_sorted_arr(worksheet, currRow, currCol, arr, cell_ids)

		workbook.close()

def write_sorted_arr(worksheet, currRow, currCol, arr, ids):
		arr = sorted(arr, key=lambda l:l[0])
		for key, val in arr :
			currCol = 0
			worksheet.write(currRow, currCol, key)
			currCol += 1
			for i in range(len(ids)) :
				idx = ids[i]
				if idx not in val.keys() :
					worksheet.write(currRow, currCol, '')
				else :
					output = val[idx]
					worksheet.write(currRow, currCol, output)
				currCol += 1
			currRow += 1
		currRow += 1


def extract_value_to_dict(inputLine, extractNum, keyPos, keyvalDict) : 
	"""
	used by process_data()
	extract value from line & store in keyvalDic
	
	extractNum: number of key+values to extract
	keyPos: position of key in inputLine
	keyvalDict: container for extracted values  
	"""
	keyvalDict.clear()
	for i in range (extractNum) :
		keyvalDict[f"val{i}"] = decimal.Decimal(inputLine[keyPos+i])