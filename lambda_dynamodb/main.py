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
import json
from decimal import Decimal

shadowTopic = "$aws/things/colibri_imx6_leo_Core/shadow/update"

dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
tableName = "PastaDemo"

# Create the dynamo db table if needed
try:
    table = dynamodb.create_table(
        TableName=tableName,
        KeySchema=[
            {
                'AttributeName': 'timestamp', 
                'KeyType': 'HASH'  #Partition key
            },
			{
                'AttributeName': 'subsystem', 
                'KeyType': 'RANGE'  #Sort key
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'timestamp',
                'AttributeType': 'N'
            },
			{
                'AttributeName': 'subsystem',
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

# This is a long lived lambda so we can keep state as below
totalTraffic = 0
totalGreenlights = 0
minCars = -1
maxCars = -1

# This handler is called when an event is sent via MQTT
# Event targets are set in subscriptions settings
# This should be set up to listen to shadow document updates
# This function gets traffic light updates from the shadow MQTT event
def function_handler(event, context):
	global totalTraffic
	global totalGreenlights
	global minCars
	global maxCars

	# grab the light status from the event
    # Shadow JSON schema:
    # { "state": { "desired": { "property":<R,G,Y> } } }
	logger.info(event)

	# Record full system snapshot to DynamoDB
	global tableName
	table = dynamodb.Table(tableName)

	# A53 CPU temeperature
	table.put_item(
		Item={
			'system': 'cpu',
			'subsystem': 'cpu-temperature-a53',
			'value' : Decimal(str(event["current"]["state"]["reported"]["cpu"]["temperatures"]["A53"])),
			'timestamp': event["current"]["metadata"]["reported"]["cpu"]["temperatures"]["A53"]["timestamp"]
		}
	)

	# A72 CPU temeperature
	table.put_item(
		Item={
			'system': 'cpu',
			'subsystem': 'cpu-temperature-a72',
			'value' : Decimal(str(event["current"]["state"]["reported"]["cpu"]["temperatures"]["A72"])),
			'timestamp': event["current"]["metadata"]["reported"]["cpu"]["temperatures"]["A72"]["timestamp"]
		}
	)

	# CPU load
	table.put_item(
		Item={
			'system': 'cpu',
			'subsystem': 'cpu-processing-load',
			'value' : Decimal(str(event["current"]["state"]["reported"]["cpu"]["usage"])),
			'timestamp': event["current"]["metadata"]["reported"]["cpu"]["usage"]["timestamp"]
		}
	)

	# GPU0 temeperature
	table.put_item(
		Item={
			'system': 'gpu',
			'subsystem': 'gpu-temperature-GPU0',
			'value' : Decimal(str(event["current"]["state"]["reported"]["gpu"]["temperatures"]["GPU0"])),
			'timestamp': event["current"]["metadata"]["reported"]["gpu"]["temperatures"]["GPU0"]["timestamp"]
		}
	)

	# GPU1 temperature
	table.put_item(
	Item={
			'system': 'gpu',
			'subsystem': 'gpu-temperature-GPU1',
			'value' : Decimal(str(event["current"]["state"]["reported"]["gpu"]["temperatures"]["GPU1"])),
			'timestamp': event["current"]["metadata"]["reported"]["gpu"]["temperatures"]["GPU1"]["timestamp"]
		}
	)

	# GPU memory usage
	table.put_item(
	Item={
			'system': 'gpu',
			'subsystem': 'gpu-memory-load',
			'value' : Decimal(str(event["current"]["state"]["reported"]["gpu"]["memoryUsage"])),
			'timestamp': event["current"]["metadata"]["reported"]["gpu"]["memoryUsage"]["timestamp"]
		}
	)

	# RAM free
	table.put_item(
	Item={
			'system': 'ram',
			'subsystem': 'ram-memory-free',
			'value' : Decimal(str(event["current"]["state"]["reported"]["ram"]["free"])),
			'timestamp': event["current"]["metadata"]["reported"]["ram"]["free"]["timestamp"]
		}
	)

	# RAM usage
	table.put_item(
	Item={
			'system': 'ram',
			'subsystem': 'ram-memory-load',
			'value' : Decimal(str(event["current"]["state"]["reported"]["ram"]["usage"])),
			'timestamp': event["current"]["metadata"]["reported"]["ram"]["usage"]["timestamp"]
		}
	)

	return