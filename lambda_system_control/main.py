#
# Copyright 2019 Toradex AG. or its affiliates. All Rights Reserved.
#

# greengrass
import greengrasssdk

# rest consume
import requests

# mqtt thread
import threading
import time
import json

core_name = "colibri_imx6_leo_Core"
system_control_port = "5002"
rest = {
	"cam/resolution": {
		"url": "http://localhost:" + system_control_port + "/cam/resolution/",
		"value": 0
	},
	"cb/speed": {
		"url": "http://localhost:" + system_control_port + "/cb/speed/",
		"value": 0
	},
	"led/brightness": {
		"url": "http://localhost:" + system_control_port + "/led/brightness/",
		"value": 0
	}
}

# Creating a greengrass core sdk client
client = greengrasssdk.client('iot-data')

# Update values on device shadow changes!
def function_handler(event, context):
	print("Got topic " + context.client_context.custom['subject'] + ". Dumping event data:")
	try:
		boardSerial = str(requests.get("http://localhost:5001/info").json()["board-serial"])
	except Exception as e:
		print("Cannot get board serial, unable to handle your request: " + repr(e))
	else:
		if context.client_context.custom['subject'] == "$aws/things/" + core_name + "/shadow/update/delta":
			for key,item in rest.items():
				try:
					item["value"] = event["current"]["state"]["desired"][key.split("/")[0]][key.split("/")[1]]
					res = requests.get(item["url"] + item["value"])
				except requests.exceptions.ConnectionError:
					print("Connection error on REST endpoint " + item["url"] + ", retry on next loop!")
				except Exception as e:
					print("Unknown exception on REST endpoint " + item["url"] + ": " + repr(e))
					print("Response error: " + str(res))
		elif context.client_context.custom['subject'] == "cb/" + boardSerial + "/speed":
			print("Updating cb " + boardSerial + " speed to: " + str(event["speed"]))
			requests.get(rest["cb/speed"]["url"] + str(event["speed"]))
		elif context.client_context.custom['subject'] == "led/" + boardSerial + "/brightness":
			print("Updating led " + boardSerial + " brightness to: " + str(event["brightness"]))
			requests.get(rest["led/brightness"]["url"] + str(event["brightness"]))
		else:
			print("No action on topic " + context.client_context.custom['subject'] + ". Dumping event data:")
			print(str(event))
	return
