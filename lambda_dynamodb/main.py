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
	table = dynamodb.Table(tableName)

	# CPU

	cpudatetime = datetime.utcfromtimestamp(int(event["current"]["metadata"]["reported"]["cpu"]["temperatures"]["A53"]["timestamp"])).strftime('%Y-%m-%d %H:%M:%S')
	res = table.put_item(
		Item={
			'pk' : cpudatetime.split()[0],
			'sk' : cpudatetime.split()[1] + '-cpu',
			#'data' : {
			#	'cpu' : {
			#		'a53-temperature': Decimal(str(event["current"]["state"]["reported"]["cpu"]["temperatures"]["A53"])),
			#		'a72-temperature': Decimal(str(event["current"]["state"]["reported"]["cpu"]["temperatures"]["A72"])),
			#		'processing-load': Decimal(str(event["current"]["state"]["reported"]["cpu"]["usage"]))
			#	}
			#},
			'system': 'cpu',
			'a53-temperature': Decimal(str(event["current"]["state"]["reported"]["cpu"]["temperatures"]["A53"])),
			'a72-temperature': Decimal(str(event["current"]["state"]["reported"]["cpu"]["temperatures"]["A72"])),
			'processing-load': Decimal(str(event["current"]["state"]["reported"]["cpu"]["usage"]))
		}
	)
	print("Added CPU item: " + str(res))

	# GPU

	gpudatetime = datetime.utcfromtimestamp(int(event["current"]["metadata"]["reported"]["gpu"]["temperatures"]["GPU0"]["timestamp"])).strftime('%Y-%m-%d %H:%M:%S')
	res = table.put_item(
		Item={
			'pk' : gpudatetime.split()[0],
			'sk' : gpudatetime.split()[1] + '-gpu',
			#'data' : {
			#	'gpu' : {
			#		'gpu0-temperature' : Decimal(str(event["current"]["state"]["reported"]["gpu"]["temperatures"]["GPU0"])),
			#		'gpu1-temperature' : Decimal(str(event["current"]["state"]["reported"]["gpu"]["temperatures"]["GPU1"])),
			#		'memory-load' : Decimal(str(event["current"]["state"]["reported"]["gpu"]["memoryUsage"]))
			#	}
			#},
			'system': 'gpu',
			'gpu0-temperature' : Decimal(str(event["current"]["state"]["reported"]["gpu"]["temperatures"]["GPU0"])),
			'gpu1-temperature' : Decimal(str(event["current"]["state"]["reported"]["gpu"]["temperatures"]["GPU1"])),
			'memory-load' : Decimal(str(event["current"]["state"]["reported"]["gpu"]["memoryUsage"]))
		}
	)
	print("Added GPU item: " + str(res))

	# RAM

	ramdatetime = datetime.utcfromtimestamp(int(event["current"]["metadata"]["reported"]["ram"]["free"]["timestamp"])).strftime('%Y-%m-%d %H:%M:%S')
	res = table.put_item(
	Item={
			'pk' : ramdatetime.split()[0],
			'sk' : ramdatetime.split()[1] + '-ram',
			#'data' : {
			#	'ram' : {
			#		'memory-free' : Decimal(str(event["current"]["state"]["reported"]["ram"]["free"])),
			#		'memory-load' : Decimal(str(event["current"]["state"]["reported"]["ram"]["usage"]))
			#	}
			#},
			'system': 'ram',
			'memory-free' : Decimal(str(event["current"]["state"]["reported"]["ram"]["free"])),
			'memory-load' : Decimal(str(event["current"]["state"]["reported"]["ram"]["usage"]))
		}
	)
	print("Added RAM item: " + str(res))

	# Inference

	inferencedatetime = datetime.utcfromtimestamp(int(event["current"]["metadata"]["reported"]["ram"]["free"]["timestamp"])).strftime('%Y-%m-%d %H:%M:%S')
	res = table.put_item(
	Item={
			'pk' : inferencedatetime.split()[0],
			'sk' : inferencedatetime.split()[1] + '-inference',
			#'data' : {
			#	'inference' : {
			#		'pasta-type' : Decimal(str(event["current"]["state"]["reported"]["inference"]["pasta-type"])),
			#		'confidence' : Decimal(str(event["current"]["state"]["reported"]["inference"]["confidence"])),
			#		'inference-time' : Decimal(str(event["current"]["state"]["reported"]["inference"]["inference-time"]))
			#	}
			#},
			'system': 'inference',
			'pasta-type' : Decimal(randrange(0, 4)),
			'confidence' : Decimal(str(uniform(0.0, 100.0))),
			'inference-time' : Decimal(randrange(75, 483))
			#'pasta-type' : Decimal(str(event["current"]["state"]["reported"]["inference"]["pasta-type"])),
			#'confidence' : Decimal(str(event["current"]["state"]["reported"]["inference"]["confidence"])),
			#'inference-time' : Decimal(str(event["current"]["state"]["reported"]["inference"]["inference-time"]))
		}
	)
	print("Added inference item: " + str(res))

	# Conveyor Belt

	cbdatetime = datetime.utcfromtimestamp(int(event["current"]["metadata"]["reported"]["ram"]["free"]["timestamp"])).strftime('%Y-%m-%d %H:%M:%S')
	res = table.put_item(
	Item={
			'pk' : cbdatetime.split()[0],
			'sk' : cbdatetime.split()[1] + '-cb',
			#'data' : {
			#	'cb' : {
			#		'speed' : Decimal(str(event["current"]["state"]["reported"]["cb"]["speed"]))
			#	}
			#},
			'system': 'cb',
			'speed' : Decimal(randrange(46, 63, 3))
			#'speed' : Decimal(str(event["current"]["state"]["reported"]["cb"]["speed"]))
		}
	)
	print("Added conveyor belt item: " + str(res))

	# LED

	leddatetime = datetime.utcfromtimestamp(int(event["current"]["metadata"]["reported"]["ram"]["free"]["timestamp"])).strftime('%Y-%m-%d %H:%M:%S')
	res = table.put_item(
	Item={
			'pk' : leddatetime.split()[0],
			'sk' : leddatetime.split()[1] + '-led',
			#'data' : {
			#	'led' : {
			#		'brightness' : Decimal(str(event["current"]["state"]["reported"]["led"]["brightness"]))
			#	}
			#},
			'system': 'led',
			'brightness' : Decimal(randrange(87, 93, 1))
			#'brightness' : Decimal(str(event["current"]["state"]["reported"]["led"]["brightness"]))
		}
	)
	print("Added LED item: " + str(res))

	return
