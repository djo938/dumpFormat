#!/bin/bash

#create arborescence
mkdir dumpformat_install
mkdir dumpformat_install/dumpformat

#copy files
cp ./setup.py ./dumpformat_install/.
cp ./README.md ./dumpformat_install/.
#cp ./example.py ./dumpformat_install/.

cp ./dumpformat/__init__.py ./dumpformat_install/dumpformat/.
cp ./dumpformat/exception.py ./dumpformat_install/dumpformat/.
cp ./dumpformat/dumpManager.py ./pytries_install/dumpformat/.

#zip the directory
zip -r dumpformat_v1.0.zip ./dumpformat_install/

rm -r ./dumpformat_install/