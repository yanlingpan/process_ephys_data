#!/usr/bin/env python3

import os
import sys
from pathlib import Path

sys.path.append("lib/macosx")
sys.path.append("lib/linux")

from glob import glob

from process import process_trace, process_data


if __name__ == "__main__":
	data_path = os.path.join(os.getcwd(), 'data')
	output_path = os.path.join(os.getcwd(), 'processed')
	# for file in glob(str(data_path + '*.asc')) + glob(str(data_path + '*.txt')):
	for file in glob(os.path.join(data_path, '*.asc')) + glob(os.path.join(data_path, '*.txt')):
		fname = Path(file).parts[-1]
		out_file = fname.replace("asc", "xlsx").replace("txt", "xlsx").replace(" ", "")
		output_path_str = str(os.path.join(output_path, out_file))
		print(os.path.dirname(output_path_str))
		assert os.path.exists(os.path.split( os.path.join(output_path, out_file))[0])
		# print(output_path_str)
		if fname.find(".asc") != -1: # trace data
			process_trace(file, os.path.join(output_path, out_file))
		else:
			process_data(file, os.path.join(output_path, out_file))
		print(f"proccessed\t{fname}")
