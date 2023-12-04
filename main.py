#!/usr/bin/env python3

import os
from glob import glob
from pathlib import Path

from process import process_trace, process_data


if __name__ == "__main__":
	data_path = Path(os.getcwd(), 'data', '*.*')
	for in_path in glob(str(data_path)):
		out_fname = Path(in_path).stem + ".xlsx"
		out_path = Path(os.getcwd(), 'output', out_fname)
		if in_path.find(".asc") != -1: # trace data
			process_trace(in_path, out_path)
		else:
			process_data(in_path, out_path)
		
		print(f"proccessed\t{Path(in_path).name}")
