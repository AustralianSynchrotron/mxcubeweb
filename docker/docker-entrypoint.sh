#!/bin/bash

# Enable conda for this shell
eval "$(/opt/conda/bin/conda shell.bash hook)"
conda activate mxcube

cd /opt/mxcube3

npm install
npm start &

redis-server &

python3 mxcube3-server -r ANSTO/ --log-file mxcube.log &

wait
