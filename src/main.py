#!/usr/bin/env python3

import os, sys
from glob import glob
from pathlib import Path

from process import process_trace, process_data


if __name__ == "__main__":
	# find data directory: recursively traverse up tree
	data_dir = Path(__file__).resolve().parent
	for _ in range(5):
		try:
			assert os.path.isdir(Path(data_dir, 'data'))
		except AssertionError:
			data_dir = Path(data_dir, '..')
	if os.path.isdir(Path(data_dir, 'data')):
		data_path = Path(data_dir, 'data', '*.*')
		if ~os.path.isdir(output_path:=Path(data_dir, 'output')):
			Path(data_dir, 'output').mkdir(parents=False, exist_ok=True)
	else:
		print(f"data directory not found: {data_dir}")
		sys.exit(-1)
	
	for in_path in glob(str(data_path)):
		out_fname = Path(in_path).stem + ".xlsx"
		out_path = Path(output_path, out_fname)
		if in_path.find(".asc") != -1: # trace data
			process_trace(in_path, out_path)
		else:
			process_data(in_path, out_path)
		print(f"proccessed\t{Path(in_path).name}")
