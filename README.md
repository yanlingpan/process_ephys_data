
├── README.md
├── Windows_executable
│   └── main.exe
├── data
│   ├── cc.txt
│   ├── cc_trace.asc
│   ├── vc.txt
│   └── vc_trace.asc
├── macOS_executable
│   └── main
├── output
│   ├── cc.xlsx
│   ├── cc_trace.xlsx
│   ├── vc.xlsx
│   └── vc_trace_family.xlsx
└── src
    ├── constants.py
    ├── main.py
    ├── process.py
    └── utils.py


---
Process data from HEKA electrophysiological recordings in .txt or .asc format, re-organize, and output in .xlsx format.

### Directory organization
---
* data
  * input data for processing
    * .txt: Notebook export data
    * .asc: trace data
    * from both voltage-clamp or current-clamp recordings
  * example data included in directory
* output
  * processed data
  * .xlsx
  * example output data included in directory

### Usage
-----
* option 1: double click executable
  * on Windows: use main.exe under Windows_executable/
  * on macOS: use main under macOS_executable/
* option 2: command line execute main.py under src/