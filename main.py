#!/usr/bin/env python3

import os
from glob import glob
from pathlib import Path

from process import process_trace, process_data


if __name__ == "__main__":
	data_path = Path(os.getcwd(), 'data', '*.*')
	output_dir = Path(os.getcwd(), 'processed')
	for input_path in glob(str(data_path)):
		fname = Path(input_path).name
		output_fname = fname.replace("asc", "xlsx").replace("txt", "xlsx")
		output_path = Path(output_dir, output_fname)
		if fname.find(".asc") != -1: # trace data
			process_trace(input_path, output_path)
		else:
			process_data(input_path, output_path)

		print(f"proccessed\t{fname}")
