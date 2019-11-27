#!/bin/bash

APP=/app
PROGFILE=/progress.txt
WEBDASHB=/webdashboards.txt
AWSPROFILE=default
UNIQUEHASH=$1
GGNAME=$2
AWSID=$3
AWSSECRET=$4

export PATH=$PATH:/root/.local/bin

echo "Starting the provisioning of the AWS and Toradex AI at the Edge Demo"

# cleanup
if [ -d "~/.aws" ]
then
	echo "AWS folder exist"
	echo "Deleting ..."
	rm -rf ~/.aws
fi

if [ -d "$PROGFILE" ]
then
	echo "$PROGFILE folder exist"
	echo "Deleting ..."
	rm -rf $PROGFILE
fi

if [ -d "$WEBDASHB" ]
then
	echo "$WEBDASHB folder exist"
	echo "Deleting ..."
	rm -rf $WEBDASHB
fi

# clean up the repos
cd $APP/aws-nxp-ai-at-the-edge-cloud-dashboard
git reset --hard HEAD
cd -

cd $APP/aws-nxp-ai-at-the-edge
git reset --hard HEAD
cd -
# end cleanup

mkdir ~/.aws
cd ~/.aws

echo "0" > ${PROGFILE}

# add the credentias
echo '['$AWSPROFILE']
aws_access_key_id='$AWSID'
aws_secret_access_key='$AWSSECRET > credentials

# add the config
echo '['$AWSPROFILE']
region=us-west-2
output=json' > config

# dashboard big bang
cd $APP/aws-nxp-ai-at-the-edge-cloud-dashboard

# Change defualt demo name. Use unique name appending seconds since epoch
demoName=pastaDemo$(date +%s)
cat appConfig.json | jshon -s $(echo $demoName) -i name > appConfig.json
# Use default AWS CLI profile
cat appConfig.json | jshon -s $(echo default) -i awsAdminProfile > appConfig.json

echo "The unique prefix for this deployment is: $demoName"
echo "The unique hash for this deployment is $UNIQUEHASH"
echo "The string used for Greengrass name is: $GGNAME"
echo "Running the web Dashboard Cloudformation. It will take some 20 minutes..."

echo "10" > ${PROGFILE}

yarn deploy
echo "40" > ${PROGFILE}
yarn update # It is mandatory even for deployment from scratch
echo "60" > ${PROGFILE}

# get the web dashboard URL
CFR=$(aws cloudfront list-distributions --no-paginate)
echo $CFR | jshon -e DistributionList -e Items -a -e DomainName -u -p \
	-e DefaultCacheBehavior -e TargetOriginId -u | grep -B 1 pastademo | grep \
	-vE 'pastademo|^--$' >> ${WEBDASHB}
echo "Web dashboard available at: $(cat ${WEBDASHB})"

# run the script
cd $APP/aws-nxp-ai-at-the-edge

# update the core shadow lambda with Cloudformation specific variable
sed -i "s/coreplaceholder/${GGNAME}_Core/g" lambda_coreshadow/main.py

# update the dynamo table name with Cloudformation specific variable
tableName=$(aws dynamodb list-tables --output=text | grep -o "\w*${demoName}.*")
sed -i "s/PastaDemoPlaceholder/${tableName}/g" lambda_dynamodb/main.py
echo "65" > ${PROGFILE}

# GG big bang
./bigbang.sh $UNIQUEHASH $GGNAME