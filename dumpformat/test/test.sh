#!/bin/bash

export PYTHONPATH=$(pwd)/../../:$PYTHONPATH
echo $PYTHONPATH
python test.py