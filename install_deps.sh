#!/bin/bash

echo "Make sure you run this script in the root directory of aws-nxp-ai-at-the-edge"

# One needs to install the dependencies locally on each lambda directory
pip3 install -r ./lambda_coreshadow/requirements.txt --system -t ./lambda_coreshadow
pip3 install -r ./lambda_dynamodb/requirements.txt --system -t ./lambda_dynamodb
pip3 install -r ./lambda_system_control/requirements.txt --system -t ./lambda_system_control
pip3 install -r ./lambda_system_status/requirements.txt --system -t ./lambda_system_status