#!/bin/bash

PROGFILE=/progress.txt
WEBDASHB=/webdashboards.txt

export PATH=$PATH:/root/.local/bin

mkdir ~/.aws
cd ~/.aws

echo "0" > ${PROGFILE}

# add the credentias
echo '[default]
aws_access_key_id='$3'
aws_secret_access_key='$4 > credentials

# add the config
echo '[default]
region=us-west-2
output=json' > config

# dashboard big bang
cd /aws-nxp-ai-at-the-edge-cloud-dashboard

# Change defualt demo name. Use unique name appending seconds since epoch
demoName=pastaDemo$(date +%s)
sed -i "s/boardName/pastaDemo${demoName}/g" appConfig.json

echo "10" > ${PROGFILE}

yarn deploy
echo "40" > ${PROGFILE}
yarn update
echo "60" > ${PROGFILE}

# get the web dashboard URL
CFR=$(aws cloudfront list-distributions --no-paginate)
echo $CFR | jshon -e DistributionList -e Items -a -e DomainName -u -p \
	-e DefaultCacheBehavior -e TargetOriginId -u | grep -B 1 pastademo | grep \
	-vE 'pastademo|^--$' >> ${WEBDASHB}

# run the script
cd /aws-nxp-ai-at-the-edge

# update the core shadow lambda with Cloudformation specific variable
sed -i "s/coreplaceholder/${2}_Core/g" lambda_coreshadow/main.py

# update the dynamo table name with Cloudformation specific variable
tableName=$(aws dynamodb list-tables --output=text | grep -o "\w*${demoName}.*")
sed -i "s/PastaDemoPlaceholder/${tableName}/g" lambda_dynamodb/main.py
echo "65" > ${PROGFILE}

# GG big bang
./bigbang.sh $1 $2
