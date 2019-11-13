#!/bin/bash

mkdir ~/.aws
cd ~/.aws

# add the credentias
echo '[default]
aws_access_key_id='$2'
aws_secret_access_key='$3 > credentials

# add the config
echo '[default]
region=us-west-2
output=json' > config

# run the script
export PATH=$PATH:/root/.local/bin
cd /aws-nxp-ai-at-the-edge.git
./bigbang.sh $1
