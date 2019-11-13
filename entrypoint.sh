#!/bin/bash

mkdir ~/.aws
cd ~/.aws

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

echo '{
  "name": "PastaDemoCFN",
  "awsAdminProfile": "default",
  "awsRegion": "us-west-2"
}' > appConfig.json

yarn installAll
yarn deploy
yarn update

# run the script
export PATH=$PATH:/root/.local/bin
cd /aws-nxp-ai-at-the-edge

# update the core shadow script
echo '#
# Copyright 2019 Toradex AG. or its affiliates. All Rights Reserved.
#

# greengrass
import greengrasssdk
from coreShadow import CoreShadow

import json

shadowThing = "'$2'_Core"

# Creating a greengrass core sdk client
client = greengrasssdk.client("iot-data")

# Shadow payload generation class
shadow = CoreShadow()

# 0 | info | cpu | gpu | ram | inference | cb | led
bitwise = {
	"cpu" : int("0b11011111", 2),
	"gpu" : int("0b11101111", 2),
	"ram" : int("0b11110111", 2),
	"inference" : int("0b11111011", 2),
	"cb" : int("0b11111101", 2),
	"led" : int("0b11111110", 2),
	"info": int("0b10111111", 2),
}
ready = int("0b01111011", 2)
tryToSendCount = 0
shadowPayload = {"state" : {"reported": {}}}


def ready_is_ready(subsys):
	global ready
	global bitwise

	ready = ready & bitwise[subsys]
	#print("Ready on zero. Current value is: " + format(ready, "#010b"))

def ready_reset():
	global ready
	global tryToSendCount
	global shadowPayload

	ready = int("0b01111011", 2)
	tryToSendCount = 0
	shadowPayload["state"]["reported"].clear()

def ready_pass():
	global tryToSendCount

	tryToSendCount += 1


def function_handler(event, context):
	global shadowPayload
	global tryToSendCount

	serial = "000"
	subsys = context.client_context.custom["subject"].split("/")[0]
	try:
		serial = context.client_context.custom["subject"].split("/")[1]
	except:
		pass

	print("Incoming event: " + subsys + " from board ID: " + serial)

	if subsys == "$aws":
		# Print confirmation
		print("Device shadow updated: " + str(event))
	else:
		if subsys == "inference":
			for inference_timestamp in event["history"]:
				for inference_result in inference_timestamp["last"]:
					del inference_result["xmin"]
					del inference_result["ymin"]
					del inference_result["xmax"]
					del inference_result["ymax"]
		# Generate payload
		#partialPayload = shadow.gen_payload(event, subsys)
		#print(str(partialPayload))
		shadowPayload["state"]["reported"].update({subsys: event})
		ready_is_ready(subsys)
		# send only after getting all data from system or not getting all data
		# for too long
		if ready == 0 or tryToSendCount >= 15:
			#print("Data buffer filled, sending updated device shadow!")
			#print(str(shadowPayload))
			res = client.update_thing_shadow(
				thingName = shadowThing,
				payload = json.dumps(shadowPayload)
			) # res is not being checked for success
			ready_reset()
		else:
			ready_pass()

	return
' > lambda_coreshadow/main.py

# update the dynamo table name
tableName=$(aws dynamodb list-tables --output=text | grep -o 'PastaDemoCFN.*')

echo '#
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

shadowTopic = {
	"6438725" : "apalis-imx8-cb-brazil_Core",
	"6494620": "colibri_imx6_leo_Core"
}

#shadowTopic = "$aws/things/colibri_imx6_leo_Core/shadow/update"

dynamodb = boto3.resource("dynamodb", region_name="us-west-2")
#tableName = "PastaDemo"
tableName = "'$tableName'"

# Create the dynamo db table if needed
try:
    table = dynamodb.create_table(
        TableName=tableName,
        KeySchema=[
            {
                "AttributeName": "pk",
                "KeyType": "HASH"  #Partition key
            },
			{
                "AttributeName": "sk",
                "KeyType": "RANGE"  #Sort key
            }
        ],
        AttributeDefinitions=[
            {
                "AttributeName": "pk",
                "AttributeType": "S"
            },
			{
                "AttributeName": "sk",
                "AttributeType": "S"
            }
        ],
        ProvisionedThroughput={
            "ReadCapacityUnits": 5,
            "WriteCapacityUnits": 5
        }
    )

    # Wait until the table exists.
    table.meta.client.get_waiter("table_exists").wait(TableName=tableName)
except ClientError as e:
    if e.response["Error"]["Code"] == "ResourceInUseException":
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

datetimes = {
	"start": {
		"cpu": None,
		"gpu": None,
		"ram": None,
		"cb": None,
		"led": None,
		"info": None,
		"inference": None
	},
	"now": {
		"cpu": 0,
		"gpu": 0,
		"ram": 0,
		"cb": 0,
		"led": 0,
		"info": 0,
		"inference": 0
	}
}

staticValues = {
	"info": {
		"board-serial": 0,
		"board-revision" : "0",
		"board-type": "0",
		"log-count": 0
	}
}

historyValues = {
	"sum": {
		"cpu": {
			"log-count": 0,
			"a53-temperature": 0.0,
			"a72-temperature": 0.0,
			"processing-load": 0.0,
			"a53-0-load": 0.0,
			"a53-1-load": 0.0,
			"a53-2-load": 0.0,
			"a53-3-load": 0.0,
			"a72-0-load": 0.0,
			"a72-1-load": 0.0
		},
		"gpu": {
			"log-count": 0,
			"gpu0-temperature" : 0.0,
			"gpu1-temperature" : 0.0,
			"memory-load" : 0.0
		},
		"ram": {
			"log-count": 0,
			"memory-free" : 0,
			"memory-load" : 0.0
		},
		"cb": {
			"log-count": 0,
			"speed": 0
		},
		"led": {
			"log-count": 0,
			"brightness": 0
		},
		"inference": {
			"log-count": 0,
			"inference-time": 0,
			"inference-time-count": 0,
			"penne": {
				"log-count": 0,
				"confidence": 0,
				"pasta-count": 0
			},
			"farfalle": {
				"log-count": 0,
				"confidence": 0,
				"pasta-count": 0
			},
			"elbow": {
				"log-count": 0,
				"confidence": 0,
				"pasta-count": 0
			},
			"shell": {
				"log-count": 0,
				"confidence": 0,
				"pasta-count": 0
			}
		}
	},
	"last": {
		"cpu": {
			"a53-temperature": 0.0,
			"a72-temperature": 0.0,
			"processing-load": 0.0,
			"a53-0-load": 0.0,
			"a53-1-load": 0.0,
			"a53-2-load": 0.0,
			"a53-3-load": 0.0,
			"a72-0-load": 0.0,
			"a72-1-load": 0.0
		},
		"gpu": {
			"gpu0-temperature" : 0.0,
			"gpu1-temperature" : 0.0,
			"memory-load" : 0.0
		},
		"ram": {
			"memory-free" : 0,
			"memory-load" : 0.0
		},
		"cb": {
			"speed": 0
		},
		"led": {
			"brightness": 0
		},
		"inference": {
			"inference-time": 0,
			"penne": {
				"confidence": 0,
				"pasta-count": 0
			},
			"farfalle": {
				"confidence": 0,
				"pasta-count": 0
			},
			"elbow": {
				"confidence": 0,
				"pasta-count": 0
			},
			"shell": {
				"confidence": 0,
				"pasta-count": 0
			}
		}
	}
}

def function_handler(event, context):


	# Record full system snapshot to DynamoDB
	global tableName
	global datetimes
	global historyValues

	# Get board info if doesn"t have yet
	try:
		if not staticValues["info"]["board-serial"]:
			staticValues["info"]["board-serial"] = str(event["current"]["state"]["reported"]["info"]["board-serial"])
		if not staticValues["info"]["board-revision"]:
			staticValues["info"]["board-revision"] = event["current"]["state"]["reported"]["info"]["board-revision"]
		if not staticValues["info"]["board-serial"]:
			staticValues["info"]["board-serial"] = event["current"]["state"]["reported"]["info"]["board-type"]
	except Exception as e:
		print("Unable to get board info: " + repr(e))

	# Calculate timestamps for each piece of data
	try:
		datetimes["now"]["cpu"] = datetime.utcfromtimestamp(int(event["current"]["metadata"]["reported"]["cpu"]["temperatures"]["A53"]["timestamp"])).strftime("%Y-%m-%d %H:%M:%S")
		if not datetimes["start"]["cpu"]:
			datetimes["start"]["cpu"] = datetimes["now"]["cpu"]

		datetimes["now"]["gpu"] = datetime.utcfromtimestamp(int(event["current"]["metadata"]["reported"]["gpu"]["temperatures"]["GPU0"]["timestamp"])).strftime("%Y-%m-%d %H:%M:%S")
		if not datetimes["start"]["gpu"]:
			datetimes["start"]["gpu"] = datetimes["now"]["gpu"]

		datetimes["now"]["ram"] = datetime.utcfromtimestamp(int(event["current"]["metadata"]["reported"]["ram"]["free"]["timestamp"])).strftime("%Y-%m-%d %H:%M:%S")
		if not datetimes["start"]["ram"]:
			datetimes["start"]["ram"] = datetimes["now"]["ram"]

		datetimes["now"]["cb"] = datetime.utcfromtimestamp(int(event["current"]["metadata"]["reported"]["cb"]["speed"]["timestamp"])).strftime("%Y-%m-%d %H:%M:%S")
		if not datetimes["start"]["cb"]:
			datetimes["start"]["cb"] = datetimes["now"]["cb"]

		datetimes["now"]["led"] = datetime.utcfromtimestamp(int(event["current"]["metadata"]["reported"]["led"]["brightness"]["timestamp"])).strftime("%Y-%m-%d %H:%M:%S")
		if not datetimes["start"]["led"]:
			datetimes["start"]["led"] = datetimes["now"]["led"]

		datetimes["now"]["info"] = datetime.utcfromtimestamp(int(event["current"]["metadata"]["reported"]["info"]["board-serial"]["timestamp"])).strftime("%Y-%m-%d %H:%M:%S")
		if not datetimes["start"]["info"]:
			datetimes["start"]["info"] = datetimes["now"]["info"]
	except Exception as e:
		import traceback
		print("Unable to get board info: " + repr(e))
		traceback.print_exc()
	else:
		# update data for board info
		staticValues["info"]["log-count"] += 1
		try: # update data for CPU
			# last
			historyValues["last"]["cpu"]["a53-temperature"] = event["current"]["state"]["reported"]["cpu"]["temperatures"]["A53"]
			historyValues["last"]["cpu"]["a72-temperature"] = event["current"]["state"]["reported"]["cpu"]["temperatures"]["A72"]
			historyValues["last"]["cpu"]["processing-load"] = event["current"]["state"]["reported"]["cpu"]["usage"]
			historyValues["last"]["cpu"]["a53-0-load"] = event["current"]["state"]["reported"]["cpu"]["usageDetailed"]["A53-0"]
			historyValues["last"]["cpu"]["a53-1-load"] = event["current"]["state"]["reported"]["cpu"]["usageDetailed"]["A53-1"]
			historyValues["last"]["cpu"]["a53-2-load"] = event["current"]["state"]["reported"]["cpu"]["usageDetailed"]["A53-2"]
			historyValues["last"]["cpu"]["a53-3-load"] = event["current"]["state"]["reported"]["cpu"]["usageDetailed"]["A53-3"]
			historyValues["last"]["cpu"]["a72-0-load"] = event["current"]["state"]["reported"]["cpu"]["usageDetailed"]["A72-0"]
			historyValues["last"]["cpu"]["a72-1-load"] = event["current"]["state"]["reported"]["cpu"]["usageDetailed"]["A72-1"]
			# sum
			historyValues["sum"]["cpu"]["a53-temperature"] += historyValues["last"]["cpu"]["a53-temperature"]
			historyValues["sum"]["cpu"]["a72-temperature"] += historyValues["last"]["cpu"]["a72-temperature"]
			historyValues["sum"]["cpu"]["processing-load"] += historyValues["last"]["cpu"]["processing-load"]
			historyValues["sum"]["cpu"]["a53-0-load"] += historyValues["last"]["cpu"]["a53-0-load"]
			historyValues["sum"]["cpu"]["a53-1-load"] += historyValues["last"]["cpu"]["a53-1-load"]
			historyValues["sum"]["cpu"]["a53-2-load"] += historyValues["last"]["cpu"]["a53-2-load"]
			historyValues["sum"]["cpu"]["a53-3-load"] += historyValues["last"]["cpu"]["a53-3-load"]
			historyValues["sum"]["cpu"]["a72-0-load"] += historyValues["last"]["cpu"]["a72-0-load"]
			historyValues["sum"]["cpu"]["a72-1-load"] += historyValues["last"]["cpu"]["a72-1-load"]
			historyValues["sum"]["cpu"]["log-count"] += 1
		except:
			pass
		try: # update data for GPU
			# last
			historyValues["last"]["gpu"]["gpu0-temperature"] = event["current"]["state"]["reported"]["gpu"]["temperatures"]["GPU0"]
			historyValues["last"]["gpu"]["gpu1-temperature"] = event["current"]["state"]["reported"]["gpu"]["temperatures"]["GPU1"]
			historyValues["last"]["gpu"]["memory-load"] = event["current"]["state"]["reported"]["gpu"]["memoryUsage"]
			# sum
			historyValues["sum"]["gpu"]["gpu0-temperature"] += historyValues["last"]["gpu"]["gpu0-temperature"]
			historyValues["sum"]["gpu"]["gpu1-temperature"] += historyValues["last"]["gpu"]["gpu1-temperature"]
			historyValues["sum"]["gpu"]["memory-load"] += historyValues["last"]["gpu"]["memory-load"]
			historyValues["sum"]["gpu"]["log-count"] += 1
		except:
			pass
		try: # update data for RAM
			# last
			historyValues["last"]["ram"]["memory-free"] = event["current"]["state"]["reported"]["ram"]["free"]
			historyValues["last"]["ram"]["memory-load"] = event["current"]["state"]["reported"]["ram"]["usage"]
			# sum
			historyValues["sum"]["ram"]["memory-free"] += historyValues["last"]["ram"]["memory-free"]
			historyValues["sum"]["ram"]["memory-load"] += historyValues["last"]["ram"]["memory-load"]
			historyValues["sum"]["ram"]["log-count"] += 1
		except:
			pass
		try: # update data for CB
			# last
			historyValues["last"]["cb"]["speed"] = event["current"]["state"]["reported"]["cb"]["speed"]
			# sum
			historyValues["sum"]["cb"]["speed"] += historyValues["last"]["cb"]["speed"]
			historyValues["sum"]["cb"]["log-count"] += 1
		except:
			pass
		try: # update data for LED
			# last
			historyValues["last"]["led"]["brightness"] = event["current"]["state"]["reported"]["led"]["brightness"]
			# sum
			historyValues["sum"]["led"]["brightness"] += historyValues["last"]["led"]["brightness"]
			historyValues["sum"]["led"]["log-count"] += 1
		except:
			pass
		try: # update data for Inference, including timestamps
			if not event["current"]["state"]["reported"]["inference"]["history"]: # all zero, no pasta detected
				historyValues["last"]["inference"]["penne"]["pasta-count"] = 0
				historyValues["last"]["inference"]["penne"]["confidence"] = 0
				historyValues["last"]["inference"]["farfalle"]["pasta-count"] = 0
				historyValues["last"]["inference"]["farfalle"]["confidence"] = 0
				historyValues["last"]["inference"]["elbow"]["pasta-count"] = 0
				historyValues["last"]["inference"]["elbow"]["confidence"] = 0
				historyValues["last"]["inference"]["shell"]["pasta-count"] = 0
				historyValues["last"]["inference"]["shell"]["confidence"] = 0
			else: # at least one pasta detected
				for inference_timestamp in event["current"]["state"]["reported"]["inference"]["history"]:
					datetimes["now"]["inference"] = datetime.utcfromtimestamp(int(float(inference_timestamp["timestamp"]))).strftime("%Y-%m-%d %H:%M:%S")
					if not datetimes["start"]["inference"]:
						datetimes["start"]["inference"] = datetimes["now"]["inference"]
					historyValues["last"]["inference"]["inference-time"] = int(1000*float(inference_timestamp["inference_time"]))
					historyValues["sum"]["inference"]["inference-time"] += historyValues["last"]["inference"]["inference-time"]
					historyValues["sum"]["inference"]["inference-time-count"] += 1
					# Reset this value before looping over pastas detected
					historyValues["last"]["inference"]["penne"]["pasta-count"] = 0
					historyValues["last"]["inference"]["penne"]["confidence"] = 0
					historyValues["last"]["inference"]["farfalle"]["pasta-count"] = 0
					historyValues["last"]["inference"]["farfalle"]["confidence"] = 0
					historyValues["last"]["inference"]["elbow"]["pasta-count"] = 0
					historyValues["last"]["inference"]["elbow"]["confidence"] = 0
					historyValues["last"]["inference"]["shell"]["pasta-count"] = 0
					historyValues["last"]["inference"]["shell"]["confidence"] = 0
					for inference_result in inference_timestamp["last"]:
						historyValues["last"]["inference"][inference_result["object"]]["pasta-count"] += 1
						historyValues["last"]["inference"][inference_result["object"]]["confidence"] += int(100*float(inference_result["score"].replace("[","").replace("]","")))
					historyValues["sum"]["inference"]["penne"]["pasta-count"] += historyValues["last"]["inference"]["penne"]["pasta-count"]
					historyValues["sum"]["inference"]["penne"]["confidence"] += historyValues["last"]["inference"]["penne"]["confidence"]
					historyValues["sum"]["inference"]["farfalle"]["pasta-count"] += historyValues["last"]["inference"]["farfalle"]["pasta-count"]
					historyValues["sum"]["inference"]["farfalle"]["confidence"] += historyValues["last"]["inference"]["farfalle"]["confidence"]
					historyValues["sum"]["inference"]["elbow"]["pasta-count"] += historyValues["last"]["inference"]["elbow"]["pasta-count"]
					historyValues["sum"]["inference"]["elbow"]["confidence"] += historyValues["last"]["inference"]["elbow"]["confidence"]
					historyValues["sum"]["inference"]["shell"]["pasta-count"] += historyValues["last"]["inference"]["shell"]["pasta-count"]
					historyValues["sum"]["inference"]["shell"]["confidence"] += historyValues["last"]["inference"]["shell"]["confidence"]
		except Exception as e:
			print("Unable to parse inference results list: " + repr(e))
			print("Dumping raw data:")
			pp.pprint(event["current"]["state"]["reported"]["inference"]["history"])
		else:
			pass # even if error, will send the last detected frame
		print("Dumping last inference results list:")
		print(str(historyValues["last"]["inference"]))
		print("Dumping sum inference results list:")
		print(str(historyValues["sum"]["inference"]))

	res = dynamodb.batch_write_item(
		RequestItems={
			tableName : [
				{
					"PutRequest" : { # CPU Sum
						"Item": {
							"pk" : "cpu",
							"sk" :  "average-" + staticValues["info"]["board-serial"],
							"start-average-time": datetimes["start"]["cpu"],
							"log-count": historyValues["sum"]["cpu"]["log-count"],
							"a53-temperature": Decimal(str(historyValues["sum"]["cpu"]["a53-temperature"])),
							"a72-temperature": Decimal(str(historyValues["sum"]["cpu"]["a72-temperature"])),
							"processing-load": Decimal(str(historyValues["sum"]["cpu"]["processing-load"])),
							"a53-0-load": Decimal(str(historyValues["sum"]["cpu"]["a53-0-load"])),
							"a53-1-load": Decimal(str(historyValues["sum"]["cpu"]["a53-1-load"])),
							"a53-2-load": Decimal(str(historyValues["sum"]["cpu"]["a53-2-load"])),
							"a53-3-load": Decimal(str(historyValues["sum"]["cpu"]["a53-3-load"])),
							"a72-0-load": Decimal(str(historyValues["sum"]["cpu"]["a72-0-load"])),
							"a72-1-load": Decimal(str(historyValues["sum"]["cpu"]["a72-1-load"]))
						}
					}
				},
				{
					"PutRequest" : { # CPU Last
						"Item": {
							"pk" : "cpu",
							"sk" :  "last-" + staticValues["info"]["board-serial"],
							"last-updated-time": datetimes["now"]["cpu"],
							"a53-temperature": Decimal(str(historyValues["last"]["cpu"]["a53-temperature"])),
							"a72-temperature": Decimal(str(historyValues["last"]["cpu"]["a72-temperature"])),
							"processing-load": Decimal(str(historyValues["last"]["cpu"]["processing-load"])),
							"a53-0-load": Decimal(str(historyValues["last"]["cpu"]["a53-0-load"])),
							"a53-1-load": Decimal(str(historyValues["last"]["cpu"]["a53-1-load"])),
							"a53-2-load": Decimal(str(historyValues["last"]["cpu"]["a53-2-load"])),
							"a53-3-load": Decimal(str(historyValues["last"]["cpu"]["a53-3-load"])),
							"a72-0-load": Decimal(str(historyValues["last"]["cpu"]["a72-0-load"])),
							"a72-1-load": Decimal(str(historyValues["last"]["cpu"]["a72-1-load"]))
						}
					}
				},
				{
					"PutRequest" :{ # GPU Sum
						"Item": {
							"pk" : "gpu",
							"sk" : "average-" + staticValues["info"]["board-serial"],
							"start-average-time": datetimes["start"]["gpu"],
							"log-count": historyValues["sum"]["gpu"]["log-count"],
							"gpu0-temperature" : Decimal(str(historyValues["sum"]["gpu"]["gpu0-temperature"])),
							"gpu1-temperature" : Decimal(str(historyValues["sum"]["gpu"]["gpu1-temperature"])),
							"memory-load" : Decimal(str(historyValues["sum"]["gpu"]["memory-load"]))
						}
					}
				},
				{
					"PutRequest" :{ # GPU Last
						"Item": {
							"pk" : "gpu",
							"sk" : "last-" + staticValues["info"]["board-serial"],
							"last-updated-time": datetimes["now"]["gpu"],
							"gpu0-temperature" : Decimal(str(historyValues["last"]["gpu"]["gpu0-temperature"])),
							"gpu1-temperature" : Decimal(str(historyValues["last"]["gpu"]["gpu1-temperature"])),
							"memory-load" : Decimal(str(historyValues["last"]["gpu"]["memory-load"]))
						}
					}
				},
				{
					"PutRequest" :{ # RAM Sum
						"Item": {
							"pk" : "ram",
							"sk" : "average-" + staticValues["info"]["board-serial"],
							"start-average-time": datetimes["start"]["ram"],
							"log-count": historyValues["sum"]["ram"]["log-count"],
							"memory-free" : Decimal(str(historyValues["sum"]["ram"]["memory-free"])),
							"memory-load" : Decimal(str(historyValues["sum"]["ram"]["memory-load"]))
						}
					}
				},
				{
					"PutRequest" :{ # RAM Last
						"Item": {
							"pk" : "ram",
							"sk" : "last-" + staticValues["info"]["board-serial"],
							"last-updated-time": datetimes["now"]["ram"],
							"memory-free" : Decimal(str(historyValues["last"]["ram"]["memory-free"])),
							"memory-load" : Decimal(str(historyValues["last"]["ram"]["memory-load"]))
						}
					}
				},
				{
					"PutRequest" :{ # CB Sum
						"Item": {
							"pk" : "cb",
							"sk" : "average-" + staticValues["info"]["board-serial"],
							"start-average-time": datetimes["start"]["cb"],
							"log-count": historyValues["sum"]["cb"]["log-count"],
							"speed" : Decimal(str(historyValues["sum"]["cb"]["speed"]))
						}
					}
				},
				{
					"PutRequest" :{ # CB Last
						"Item": {
							"pk" : "cb",
							"sk" : "last-" + staticValues["info"]["board-serial"],
							"last-updated-time": datetimes["now"]["cb"],
							"speed" : Decimal(str(historyValues["last"]["cb"]["speed"]))
						}
					}
				},
				{
					"PutRequest" :{ # LED Sum
						"Item": {
							"pk" : "led",
							"sk" : "average-" + staticValues["info"]["board-serial"],
							"start-average-time": datetimes["start"]["led"],
							"log-count": historyValues["sum"]["led"]["log-count"],
							"brightness" : Decimal(str(historyValues["sum"]["led"]["brightness"]))
						}
					}
				},
				{
					"PutRequest" :{ # LED Last
						"Item": {
							"pk" : "led",
							"sk" : "last-" + staticValues["info"]["board-serial"],
							"last-updated-time": datetimes["now"]["led"],
							"brightness" : Decimal(str(historyValues["last"]["led"]["brightness"]))
						}
					}
				},
				{
					"PutRequest" :{ # Inference Sum
						"Item": {
							"pk" : "inference",
							"sk" : "average-" + staticValues["info"]["board-serial"],
							"start-average-time": datetimes["start"]["inference"],
							"inference-time": historyValues["sum"]["inference"]["inference-time"],
							"inference-time-count" : historyValues["sum"]["inference"]["inference-time-count"]
						}
					}
				},
				{
					"PutRequest" :{ # Inference Last
						"Item": {
							"pk" : "inference",
							"sk" : "last-" + staticValues["info"]["board-serial"],
							"last-updated-time": datetimes["now"]["inference"],
							"inference-time": historyValues["last"]["inference"]["inference-time"],
						}
					}
				},
				{
					"PutRequest" :{ # Inference Sum - penne
						"Item": {
							"pk" : "inference-penne",
							"sk" : "average-" + staticValues["info"]["board-serial"],
							"start-average-time": datetimes["start"]["inference"],
							"pasta-count": historyValues["sum"]["inference"]["penne"]["pasta-count"],
							"confidence" : historyValues["sum"]["inference"]["penne"]["confidence"]
						}
					}
				},
				{
					"PutRequest" :{ # Inference Last - penne
						"Item": {
							"pk" : "inference-penne",
							"sk" : "last-" + staticValues["info"]["board-serial"],
							"last-updated-time": datetimes["now"]["inference"],
							"pasta-count": historyValues["last"]["inference"]["penne"]["pasta-count"],
							"confidence" : historyValues["last"]["inference"]["penne"]["confidence"]
						}
					}
				},
				{
					"PutRequest" :{ # Inference Sum - farfalle
						"Item": {
							"pk" : "inference-farfalle",
							"sk" : "average-" + staticValues["info"]["board-serial"],
							"start-average-time": datetimes["start"]["inference"],
							"pasta-count": historyValues["sum"]["inference"]["farfalle"]["pasta-count"],
							"confidence" : historyValues["sum"]["inference"]["farfalle"]["confidence"]
						}
					}
				},
				{
					"PutRequest" :{ # Inference Last - farfalle
						"Item": {
							"pk" : "inference-farfalle",
							"sk" : "last-" + staticValues["info"]["board-serial"],
							"last-updated-time": datetimes["now"]["inference"],
							"pasta-count": historyValues["last"]["inference"]["farfalle"]["pasta-count"],
							"confidence" : historyValues["last"]["inference"]["farfalle"]["confidence"]
						}
					}
				},
				{
					"PutRequest" :{ # Inference Sum - elbow
						"Item": {
							"pk" : "inference-elbow",
							"sk" : "average-" + staticValues["info"]["board-serial"],
							"start-average-time": datetimes["start"]["inference"],
							"pasta-count": historyValues["sum"]["inference"]["elbow"]["pasta-count"],
							"confidence" : historyValues["sum"]["inference"]["elbow"]["confidence"]
						}
					}
				},
				{
					"PutRequest" :{ # Inference Last - elbow
						"Item": {
							"pk" : "inference-elbow",
							"sk" : "last-" + staticValues["info"]["board-serial"],
							"last-updated-time": datetimes["now"]["inference"],
							"pasta-count": historyValues["last"]["inference"]["elbow"]["pasta-count"],
							"confidence" : historyValues["last"]["inference"]["elbow"]["confidence"]
						}
					}
				},
				{
					"PutRequest" :{ # Inference Sum - shell
						"Item": {
							"pk" : "inference-shell",
							"sk" : "average-" + staticValues["info"]["board-serial"],
							"start-average-time": datetimes["start"]["inference"],
							"pasta-count": historyValues["sum"]["inference"]["shell"]["pasta-count"],
							"confidence" : historyValues["sum"]["inference"]["shell"]["confidence"]
						}
					}
				},
				{
					"PutRequest" :{ # Inference Last - shell
						"Item": {
							"pk" : "inference-shell",
							"sk" : "last-" + staticValues["info"]["board-serial"],
							"last-updated-time": datetimes["now"]["inference"],
							"pasta-count": historyValues["last"]["inference"]["shell"]["pasta-count"],
							"confidence" : historyValues["last"]["inference"]["shell"]["confidence"]
						}
					}
				},
				{
					"PutRequest" :{ # Last online
						"Item": {
							"pk" : "board-detail",
							"sk" : staticValues["info"]["board-serial"],
							"board-revision" : staticValues["info"]["board-revision"],
							"board-type": staticValues["info"]["board-type"],
							"last-updated-time": datetimes["now"]["info"],
							"log-count": staticValues["info"]["log-count"]
						}
					}
				}
			]
		}
	)
	logger.info("Response from DynaomDB generic request: ")
	logger.info(res)

	return
' > lambda_dynamodb/main.py

# GG big bang
./bigbang.sh $1 $2
