#!/usr/bin/env python3

import os, sys
from glob import glob
from pathlib import Path

from process import process_trace, process_data


if __name__ == "__main__":
	# find data directory: recursively traverse up tree maximal n levels
	data_dir = Path(__file__).resolve().parent
	n = 5
	while ( not Path(data_dir, 'data').is_dir() and n>0 ):
		data_dir = Path(data_dir, '..')
		n -= 1
	
	# get data_path for files, make output directory if not exist
	if (data_dir:=Path(data_dir, 'data')).is_dir():
		data_path = Path(data_dir, '*.*')
		if not (output_path:=Path(data_dir, 'output')).is_dir():
			Path(data_dir, 'output').mkdir(parents=False, exist_ok=True)
	else:
		print(f"data directory not found: {data_dir}")
		sys.exit(-1)
	
	# process all files in data_path
	for in_path in glob(str(data_path)):
		out_fname = Path(in_path).stem + ".xlsx"
		out_path = Path(output_path, out_fname)
		if in_path.find(".asc") != -1: # trace data
			process_trace(in_path, out_path)
		else:
			process_data(in_path, out_path)
		print(f"proccessed\t{Path(in_path).name}")
