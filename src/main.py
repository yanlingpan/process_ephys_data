#!/usr/bin/env python3

import os, sys
from glob import glob
from pathlib import Path

from process import process_trace, process_data


if __name__ == "__main__":
	# Get the path of the current file (script)
	script_path = os.path.realpath(__file__)
	# Get the directory containing the current file (script)
	script_dir = os.path.dirname(script_path)
	# Change the current working directory to the directory containing the current file (script)
	os.chdir(script_dir)

	if os.path.isdir(Path(os.getcwd(), 'data')):
		data_path = Path(os.getcwd(), 'data', '*.*')
		output_path = Path(os.getcwd(), 'output')
	else:
		data_path = Path(os.getcwd(), '..', 'data', '*.*')
		output_path = Path(os.getcwd(), '..', 'output')
	# print("data dir", os.path.isdir(Path(os.getcwd(), 'data')))
	# data_path = Path(os.getcwd(), '..', 'data', '*.*')
	for in_path in glob(str(data_path)):
		out_fname = Path(in_path).stem + ".xlsx"
		# out_path = Path(os.getcwd(), '..', 'output', out_fname)
		out_path = Path(output_path, out_fname)
		if in_path.find(".asc") != -1: # trace data
			process_trace(in_path, out_path)
		else:
			process_data(in_path, out_path)
		print(f"proccessed\t{Path(in_path).name}")
