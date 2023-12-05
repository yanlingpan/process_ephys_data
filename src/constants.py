"""defines constances"""

"""
used by process_data()
protocols for specific extraction pattern
determines how columns are organized, which values to extract from notebook
fall back to default pattern if not included in this section
"""
cell_capacitance_protocols = ["CC", "tivPPbefore"]
cc_noStim_protocols = ["cc-noST", "CC"]
cc_inputResistence_protocols = ["cc-input R", "input2"]
cc_APcount_protocols = ["cc2", "cc10", "cc-short", "cc-short2", "cc-ramp50", "cc-ramp10", # RGC
												"CC", "CC2", "CC3", "sAP 1ms", "CC3-2", "sAP 1ms-2" # DRG
												] 
vc_persistent_protocols = ["tivPPbefore", "tiv-200ms", "tivPPbefore-200ms"]


"""
used by process_trace()
subset trace if full trace not needed
"""
START_IDX = str(0)
END_IDX = str(float('inf'))


""" 
column index of cell metadata
index number depends exported notebook
examples:
'EPC10, V-Clamp,  1.0364E-11,  2.6536E+06,  8.0504E+01'
	order of line[2], line[3], line[4]: Cslow, Rs, Rcomp
'EPC10, V-Clamp,  1.0000E-03,  1.5974E-11,  1.4597E+06,  8.4989E+01'
	order of line[3], line[4], line[5]: Cslow, Rs, Rcomp 
"""
cell_capacitance_idx, cell_Rs_idx, cell_Rcomp_idx = 2, 3, 4

