Usage
-----
* 

TODO
----
* README.md

DONE
----

BUILD COMMAND
---
pyinstaller --collect-submodules utils.py --collect-submodules constants.py --collect-submodules process.py  --add-data="/Users/giraffecolor/Documents/code/process_ephys_data/data/*:data/" --add-data="/Users/giraffecolor/Documents/code/process_ephys_data/output/*:output/"  main.py

pyinstaller --noconfirm --collect-submodules utils.py --collect-submodules constants.py --collect-submodules process.py main.py
