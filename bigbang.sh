#!/bin/bash

###
# god needs the parameters
###
if [ -z "$1" ]
  then
    echo "No unique hash supplied"
    echo "Please give bucket an unique name: ./bigbang.sh mybucket-unique-hash"
    exit
fi

###
# said god let there be light and there was light
###

export PATH=$PATH:/root/.local/bin
APP=/app
PROGFILE=/progress.txt
UNIQUEHASH=$1
GGNAME=$2
STACKNAME="pasta-demo-cfn-"$UNIQUEHASH

echo "Packaging lambdas as ZIP and uploading to S3 bucket"

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

echo "Lambdas packages. Uploading to S3..."

echo "79" > ${PROGFILE}

# create the bucket to send zips
aws s3 mb s3://$STACKNAME

echo "83" > ${PROGFILE}

# send zips
aws s3 sync functions/ s3://$STACKNAME/functions

echo "Lambdas uploaded to S3"

echo "85" > ${PROGFILE}

# create the cloud formation stack
echo "Creating Greengrass Cloudformation Stack"
aws cloudformation \
    create-stack \
    --stack-name $STACKNAME \
    --template-body file://pasta_demo_cfn.yml \
    --parameters ParameterKey=S3BucketName,ParameterValue=$STACKNAME \
    ParameterKey=CoreName,ParameterValue=$GGNAME \
    --region "us-west-2" \
    --capabilities CAPABILITY_IAM

# wait the stack create
aws cloudformation wait \
    stack-create-complete \
    --stack-name $STACKNAME

echo "Greengrass Cloudformation Stack created"

echo "90" > ${PROGFILE}

# get the output
aws cloudformation \
    describe-stacks \
    --stack-name $STACKNAME \
    --output text

# generate the .tar.gz
echo "Creating Core device certificates and installing on the board"
mkdir certs
mkdir config

certificatePem=$(aws cloudformation describe-stacks --stack-name $STACKNAME \
    --query 'Stacks[0].Outputs[?OutputKey==`CertificatePem`].OutputValue' \
    --output text)

certificatePrivateKey=$(aws cloudformation describe-stacks --stack-name $STACKNAME \
    --query 'Stacks[0].Outputs[?OutputKey==`CertificatePrivateKey`].OutputValue' \
    --output text)

ConfigJson=$(aws cloudformation describe-stacks --stack-name $STACKNAME \
    --query 'Stacks[0].Outputs[?OutputKey==`ConfigJson`].OutputValue' \
    --output text)

iotEndpoint=$(aws cloudformation describe-stacks --stack-name $STACKNAME \
    --query 'Stacks[0].Outputs[?OutputKey==`IoTEndpoint`].OutputValue' \
    --output text)

roleArn=$(aws cloudformation describe-stacks --stack-name $STACKNAME \
    --query 'Stacks[0].Outputs[?OutputKey==`RoleARN`].OutputValue' \
    --output text)

groupId=$(aws cloudformation describe-stacks --stack-name $STACKNAME \
    --query 'Stacks[0].Outputs[?OutputKey==`GroupId`].OutputValue' \
    --output text)

groupLatestVersion=$(aws cloudformation describe-stacks --stack-name $STACKNAME \
    --query 'Stacks[0].Outputs[?OutputKey==`GroupLatestVersion`].OutputValue' \
    --output text)

echo -n "${certificatePem}" > certs/cert.pem
echo -n "${certificatePrivateKey}" > certs/cert.key
echo -n "${ConfigJson}" > config/config.json

echo "Certificates created"

tar -czvf pastaDemo-certs.tar.gz certs/ config/
mv pastaDemo-certs.tar.gz certs/
# move the files
mv certs/cert.pem /greengrass/certs/
mv certs/cert.key /greengrass/certs/
mv config/config.json /greengrass/config/

echo "Certificates installed"
echo "Associating service role to account"

# associate service role to account
# I think this could be done with Cloudformation, not exactly sure how
roles=$(aws iam list-roles)
roleArnOk=$(echo $roles | jshon -e Roles -a -e Arn -u | grep -E "$STACKNAME.*Greengrass")
if [ -z "$roleArnOk" ]; then
    echo "Service Role retrieved is empty"
    aws greengrass associate-service-role-to-account --role-arn "$roleArn"
else
    echo "Role exists"
fi

[ "$?" == "0" ] && echo "Success on service role association:" || echo "Service role association failed:"
aws greengrass get-service-role-for-account

# deploy to greengrass core
echo "Starting greengrass core deployment - will be queued until the device connects to Cloud"

ggGroups=$(aws greengrass list-groups)
ggMyGroup=$(echo $ggGroups | jshon -e Groups -a -e Name -u -p -e Id -u -p \
    -e LatestVersion -u | grep -A 2 ${GGNAME} | grep -v ${GGNAME})
ggId=$(echo $ggMyGroup | cut -d " " -f1)
ggLatestVersion=$(echo $ggMyGroup | cut -d " " -f2)
echo "Greengrass group ID: $ggId"
echo "Greengrass group latest version ID: $ddLatestVersion"
aws greengrass create-deployment \
    --deployment-type NewDeployment \
    --group-id "$ggId" \
    --group-version-id "$ggLatestVersion"

#update the iotendpoint
echo "Updating the IoT endpoint from the web dashboard. Takes a few minutes..."

cd $APP/aws-nxp-ai-at-the-edge-cloud-dashboard

echo "95" > ${PROGFILE}

echo '// eslint-disable-next-line import/prefer-default-export
export const region = "us-west-2"
export const iotEndpoint = "'$iotEndpoint'"' > src/shared/constants/aws.js

yarn update
echo "Deployment process completed! :)"
echo "100" > ${PROGFILE}