#!/bin/bash

LAMBDA_NAME=CoreShadow
LAMBDA_ALIAS=cshadow
LAMBDA_DIRECTORY=lambda_coreshadow

# zip the code
cd ${LAMBDA_DIRECTORY}
rm ${LAMBDA_ALIAS}.zip
zip -rq ${LAMBDA_ALIAS}.zip *
cd -

# update the code
echo "Updating the code..."
aws lambda \
	update-function-code \
	--function-name ${LAMBDA_NAME} \
	--zip-file fileb://$(pwd)/${LAMBDA_DIRECTORY}/${LAMBDA_ALIAS}.zip \
	--publish

# delete the default alias
echo "Deleting old alias..."
aws lambda \
	delete-alias \
	--function-name ${LAMBDA_NAME} \
	--name ${LAMBDA_ALIAS}

# create the alias for the $LATEST TODO get the $LATEST number automatically
echo "Creating new alias..."
aws lambda \
	create-alias \
	--function-name ${LAMBDA_NAME} \
	--name ${LAMBDA_ALIAS} \
	--function-version $1
