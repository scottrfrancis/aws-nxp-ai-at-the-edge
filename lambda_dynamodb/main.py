#
# Copyright 2019 Toradex AG. or its affiliates. All Rights Reserved.
#

# greengrass
import greengrasssdk
import boto3
from botocore.exceptions import ClientError
import logging
import pprint

# helper
from random import *
import time
from datetime import datetime
import json
from decimal import Decimal

pp = pprint.PrettyPrinter(indent=4)

shadowTopic = "$aws/things/colibri_imx6_leo_Core/shadow/update"

dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
#tableName = "PastaDemo"
tableName = "sebaPastaNewRepoDev-sebaPastaNewRepoDevApiDynamoDbTable-5KJC1F84OO7F"

# Create the dynamo db table if needed
try:
    table = dynamodb.create_table(
        TableName=tableName,
        KeySchema=[
            {
                'AttributeName': 'pk',
                'KeyType': 'HASH'  #Partition key
            },
			{
                'AttributeName': 'sk',
                'KeyType': 'RANGE'  #Sort key
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'pk',
                'AttributeType': 'S'
            },
			{
                'AttributeName': 'sk',
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )

    # Wait until the table exists.
    table.meta.client.get_waiter('table_exists').wait(TableName=tableName)
except ClientError as e:
    if e.response['Error']['Code'] == 'ResourceInUseException':
        print("Table already created")
    else:
        raise e

# initialize the logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# This handler is called when an event is sent via MQTT
# Event targets are set in subscriptions settings
# This should be set up to listen to shadow document updates
# This function gets traffic light updates from the shadow MQTT event
def function_handler(event, context):


	# Record full system snapshot to DynamoDB
	global tableName


	# Calculate timestamps for each piece of data
	cpudatetime = datetime.utcfromtimestamp(int(event["current"]["metadata"]["reported"]["cpu"]["temperatures"]["A53"]["timestamp"])).strftime('%Y-%m-%d %H:%M:%S')
	gpudatetime = datetime.utcfromtimestamp(int(event["current"]["metadata"]["reported"]["gpu"]["temperatures"]["GPU0"]["timestamp"])).strftime('%Y-%m-%d %H:%M:%S')
	ramdatetime = datetime.utcfromtimestamp(int(event["current"]["metadata"]["reported"]["ram"]["free"]["timestamp"])).strftime('%Y-%m-%d %H:%M:%S')
	inferencedatetime = datetime.utcfromtimestamp(int(event["current"]["metadata"]["reported"]["ram"]["free"]["timestamp"])).strftime('%Y-%m-%d %H:%M:%S')
	cbdatetime = datetime.utcfromtimestamp(int(event["current"]["metadata"]["reported"]["ram"]["free"]["timestamp"])).strftime('%Y-%m-%d %H:%M:%S')
	leddatetime = datetime.utcfromtimestamp(int(event["current"]["metadata"]["reported"]["ram"]["free"]["timestamp"])).strftime('%Y-%m-%d %H:%M:%S')
	infodatetime = datetime.utcfromtimestamp(int(event["current"]["metadata"]["reported"]["info"]["board-serial"]["timestamp"])).strftime('%Y-%m-%d %H:%M:%S')

	boardSerial = event["current"]["state"]["reported"]["info"]["board-serial"]

	res = dynamodb.batch_write_item(
		RequestItems={
			tableName : [
				{
					'PutRequest' : {
						'Item': {
							'pk' : cpudatetime.split()[0],
							'sk' : cpudatetime.split()[1] + '-cpu-' + str(boardSerial),
							'system': 'cpu',
							'a53-temperature': Decimal(str(event["current"]["state"]["reported"]["cpu"]["temperatures"]["A53"])),
							'a72-temperature': Decimal(str(event["current"]["state"]["reported"]["cpu"]["temperatures"]["A72"])),
							'processing-load': Decimal(str(event["current"]["state"]["reported"]["cpu"]["usage"])),
							'a53-0-load': Decimal(str(event["current"]["state"]["reported"]["cpu"]["usageDetailed"]["A53-0"])),
							'a53-1-load': Decimal(str(event["current"]["state"]["reported"]["cpu"]["usageDetailed"]["A53-1"])),
							'a53-2-load': Decimal(str(event["current"]["state"]["reported"]["cpu"]["usageDetailed"]["A53-2"])),
							'a53-3-load': Decimal(str(event["current"]["state"]["reported"]["cpu"]["usageDetailed"]["A53-3"])),
							'a72-0-load': Decimal(str(event["current"]["state"]["reported"]["cpu"]["usageDetailed"]["A72-0"])),
							'a72-1-load': Decimal(str(event["current"]["state"]["reported"]["cpu"]["usageDetailed"]["A72-1"]))
						}
					}
				},
				{
					'PutRequest' :{
						'Item': {
							'pk' : gpudatetime.split()[0],
							'sk' : gpudatetime.split()[1] + '-gpu-' + str(boardSerial),
							'system': 'gpu',
							'gpu0-temperature' : Decimal(str(event["current"]["state"]["reported"]["gpu"]["temperatures"]["GPU0"])),
							'gpu1-temperature' : Decimal(str(event["current"]["state"]["reported"]["gpu"]["temperatures"]["GPU1"])),
							'memory-load' : Decimal(str(event["current"]["state"]["reported"]["gpu"]["memoryUsage"]))
						}
					}
				},
				{
					'PutRequest' :{
						'Item': {
							'pk' : ramdatetime.split()[0],
							'sk' : ramdatetime.split()[1] + '-ram-' + str(boardSerial),
							'system': 'ram',
							'memory-free' : Decimal(str(event["current"]["state"]["reported"]["ram"]["free"])),
							'memory-load' : Decimal(str(event["current"]["state"]["reported"]["ram"]["usage"]))
						}
					}
				},
				{
					'PutRequest' :{
						'Item': {
							'pk' : cbdatetime.split()[0],
							'sk' : cbdatetime.split()[1] + '-cb-' + str(boardSerial),
							'system': 'cb',
							'speed' : Decimal(str(event["current"]["state"]["reported"]["cb"]["speed"]))
						}
					}
				},
				{
					'PutRequest' :{
						'Item': {
							'pk' : leddatetime.split()[0],
							'sk' : leddatetime.split()[1] + '-led-' + str(boardSerial),
							'system': 'led',
							'brightness' : Decimal(str(event["current"]["state"]["reported"]["led"]["brightness"]))
						}
					}
				},
				{
					'PutRequest' :{
						'Item': {
							'pk' : 'board-detail',
							'sk' : str(boardSerial),
							'board-revision' : event["current"]["state"]["reported"]["info"]["board-revision"],
							'board-type': event["current"]["state"]["reported"]["info"]["board-type"],
							'last-update-time': infodatetime
						}
					}
				}
			]
		}
	)
	logger.info("Response from DynaomDB generic request: ")
	logger.info(res)

	try:
		infres = {'result-list': []}
		infcount = 0
		for inference_timestamp in event["current"]["state"]["reported"]["inference"]["history"]:
			inferencedatetime = datetime.utcfromtimestamp(int(float(inference_timestamp['timestamp']))).strftime('%Y-%m-%d %H:%M:%S')
			inferenceCalcTime = int(1000*float(inference_timestamp['inference_time']))
			for inference_result in inference_timestamp['last']:
				infres['result-list'].append({
					'PutRequest': {
						'Item': {
							'pk' : inferencedatetime.split()[0],
							'sk' : inferencedatetime.split()[1] + '-' + str(infcount) + '-inference-' + str(boardSerial),
							'system': 'inference',
							'pasta-type' : inference_result['object'],
							'confidence' : int(100*float(inference_result['score'].replace('[','').replace(']',''))),
							'inference-time' : inferenceCalcTime
						}
					}
				})
				infcount += 1
	except Exception as e:
		print("Unable to parse inference results list: " + repr(e))
		print("Dumping raw data:")
		pp.pprint(event["current"]["state"]["reported"]["inference"]["history"])
	else:
		print("Dumping inference results list:")
		print(str(infres))
		if infres['result-list']:
			res = dynamodb.batch_write_item(
				RequestItems={
					tableName : infres['result-list']
				}
			)
			logger.info("Response from DynaomDB inference request: ")
			logger.info(res)

	return
