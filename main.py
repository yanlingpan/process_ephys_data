#!/usr/bin/env python3
import os
from glob import glob

from process import process_trace, process_data


if __name__ == "__main__":
	data_directory = os.getcwd() + '/data/'
	for file in glob(data_directory + '*.asc') + glob(data_directory + '*.txt'):
		fname = file.split("/")[-1]
		if fname.find(".asc") != -1: # trace data
			process_trace(file)
		else:
			process_data(file)
		print(f"proccessed\t{fname}")
