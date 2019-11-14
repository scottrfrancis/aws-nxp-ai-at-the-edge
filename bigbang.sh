#!/bin/bash

PROGFILE=/progress.txt

###
# god needs the parameters
###
if [ -z "$1" ]
  then
    echo "No argument supplied"
    echo "Please give bucket a name: ./bigbang.sh mybucket"
    exit
fi

###
# said god let there be light and there was light
###

# create the storage for lambda zips
mkdir functions

# create the lambda zip
# CoreShadow
LAMBDA_ALIAS=cshadow
LAMBDA_DIRECTORY=lambda_coreshadow

# zip the code
cd ${LAMBDA_DIRECTORY}
rm ../functions/${LAMBDA_ALIAS}.zip
zip -rq ${LAMBDA_ALIAS}.zip *
mv ${LAMBDA_ALIAS}.zip ../functions
cd -

echo "70" > ${PROGFILE}

# DynamoDB
LAMBDA_ALIAS=ddb
LAMBDA_DIRECTORY=lambda_dynamodb

# zip the code
cd ${LAMBDA_DIRECTORY}
rm ../functions/${LAMBDA_ALIAS}.zip
zip -rq ${LAMBDA_ALIAS}.zip *
mv ${LAMBDA_ALIAS}.zip ../functions
cd -

echo "73" > ${PROGFILE}

# SystemControl
LAMBDA_ALIAS=sysctrl
LAMBDA_DIRECTORY=lambda_system_control

# zip the code
cd ${LAMBDA_DIRECTORY}
rm ../functions/${LAMBDA_ALIAS}.zip
zip -rq ${LAMBDA_ALIAS}.zip *
mv ${LAMBDA_ALIAS}.zip ../functions
cd -

echo "76" > ${PROGFILE}

# SystemStatus
LAMBDA_ALIAS=sysstats
LAMBDA_DIRECTORY=lambda_system_status

# zip the code
cd ${LAMBDA_DIRECTORY}
rm ../functions/${LAMBDA_ALIAS}.zip
zip -rq ${LAMBDA_ALIAS}.zip *
mv ${LAMBDA_ALIAS}.zip ../functions
cd -

echo "79" > ${PROGFILE}

# create the bucket to send zips
aws s3 mb s3://$1

echo "83" > ${PROGFILE}

# send zips
aws s3 sync functions/ s3://$1/functions

echo "85" > ${PROGFILE}

# create the cloud formation stack
aws cloudformation \
    create-stack \
    --stack-name "PastaDemoCFN"$1 \
    --template-body file://pasta_demo_cfn.yml \
    --parameters ParameterKey=S3BucketName,ParameterValue=$1 \
    ParameterKey=CoreName,ParameterValue=$2 \
    --region "us-west-2" \
    --capabilities CAPABILITY_IAM

# wait the stack create
aws cloudformation wait \
    stack-create-complete \
    --stack-name "PastaDemoCFN"$1

echo "90" > ${PROGFILE}

# get the output
aws cloudformation \
    describe-stacks \
    --stack-name "PastaDemoCFN"$1 \
    --output text

# generate the .tar.gz
mkdir certs
mkdir config

certificatePem=$(aws cloudformation describe-stacks --stack-name "PastaDemoCFN"$1 \
    --query 'Stacks[0].Outputs[?OutputKey==`CertificatePem`].OutputValue' \
    --output text)

certificatePrivateKey=$(aws cloudformation describe-stacks --stack-name "PastaDemoCFN"$1 \
    --query 'Stacks[0].Outputs[?OutputKey==`CertificatePrivateKey`].OutputValue' \
    --output text)

ConfigJson=$(aws cloudformation describe-stacks --stack-name "PastaDemoCFN"$1 \
    --query 'Stacks[0].Outputs[?OutputKey==`ConfigJson`].OutputValue' \
    --output text)

iotEndpoint=$(aws cloudformation describe-stacks --stack-name "PastaDemoCFN"$1 \
    --query 'Stacks[0].Outputs[?OutputKey==`IoTEndpoint`].OutputValue' \
    --output text)

echo -n "${certificatePem}" > certs/cert.pem
echo -n "${certificatePrivateKey}" > certs/cert.key
echo -n "${ConfigJson}" > config/config.json

tar -czvf pastaDemo-certs.tar.gz certs/ config/
mv pastaDemo-certs.tar.gz certs/
# move the files
mv certs/cert.pem /greengrass/certs/
mv certs/cert.key /greengrass/certs/
mv config/config.json /greengrass/config/

#update the iotendpoint
cd /aws-nxp-ai-at-the-edge-cloud-dashboard

echo "95" > ${PROGFILE}

echo '// eslint-disable-next-line import/prefer-default-export
export const region = "us-west-2"
export const iotEndpoint = "'$iotEndpoint'"' > src/shared/constants/aws.js

yarn update
echo "100" > ${PROGFILE}