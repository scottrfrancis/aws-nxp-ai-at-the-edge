#
# Copyright 2019 Toradex AG. or its affiliates. All Rights Reserved.
#

# greengrass
import greengrasssdk
import boto3
from botocore.exceptions import ClientError
import logging

# helper
from random import *
import time
from datetime import datetime
import json
from decimal import Decimal

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
							'pk' : inferencedatetime.split()[0],
							'sk' : inferencedatetime.split()[1] + '-inference-' + str(boardSerial),
							'system': 'inference',
							'pasta-type' : Decimal(randrange(0, 4)),
							'confidence' : Decimal(str(uniform(0.0, 100.0))),
							'inference-time' : Decimal(randrange(75, 483))
							#'pasta-type' : Decimal(str(event["current"]["state"]["reported"]["inference"]["pasta-type"])),
							#'confidence' : Decimal(str(event["current"]["state"]["reported"]["inference"]["confidence"])),
							#'inference-time' : Decimal(str(event["current"]["state"]["reported"]["inference"]["inference-time"]))
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
				#{
				#	'PutRequest' :{
				#		'Item': {
				#			'pk' : leddatetime.split()[0],
				#			'sk' : leddatetime.split()[1] + '-info-' + str(boardSerial),
				#			'system': 'info',
				#			'board-revision' : event["current"]["state"]["reported"]["info"]["board-revision"],
				#			'board-serial': event["current"]["state"]["reported"]["info"]["board-serial"],
				#			'board-type': event["current"]["state"]["reported"]["info"]["board-type"]
				#		}
				#	}
				#}
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

	logger.info("Response from DynaomDB request: ")
	logger.info(res)

	return
