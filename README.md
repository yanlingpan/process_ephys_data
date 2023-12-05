Process data from HEKA electrophysiological recordings in .txt or .asc, re-organize, and output as .xlsx.

### Directory organization
---
```bash
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
```

* ```data```
  * input data for processing
    * ```.txt```: notebook exported data
    * ```.asc```: trace data
    * from both voltage-clamp or current-clamp recordings
  * example data included in directory
* ```output```
  * processed data
  * .xlsx
  * example output data included in directory
* ```src/constants.py```
  * defines names of recording protocols

### Usage
-----
* Option 1 (simplest): double click executable
  * on Windows: use ```main.exe``` under ```Windows_executable```
  * on macOS: use ```main``` under ```macOS_executable```
* Option 2 (if you need to modify code): command line execute ```main.py``` under ```src```
  * requirements:
    * Python version: 3.10.10
    * packge: XlsxWriter==3.1.9
  ```bash
  python src/main.py
  ```
  on macOS, also
  ```bash
  ./src/main.py
  ```