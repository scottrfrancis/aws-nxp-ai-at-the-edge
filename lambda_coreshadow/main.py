#
# Copyright 2019 Toradex AG. or its affiliates. All Rights Reserved.
#

# greengrass
import greengrasssdk
from coreShadow import CoreShadow

import json

shadowThing = "colibri_imx6_leo_Core"

# Creating a greengrass core sdk client
client = greengrasssdk.client('iot-data')

# Shadow payload generation class
shadow = CoreShadow()

# 0 | info | cpu | gpu | ram | inference | cb | led
bitwise = {
	"cpu" : int('0b11011111', 2),
	"gpu" : int('0b11101111', 2),
	"ram" : int('0b11110111', 2),
	"inference" : int('0b11111011', 2),
	"cb" : int('0b11111101', 2),
	"led" : int('0b11111110', 2),
	"info": int('0b10111111', 2),
}
ready = int('0b01111011', 2)
tryToSendCount = 0
shadowPayload = {"state" : {"reported": {}}}


def ready_is_ready(subsys):
	global ready
	global bitwise

	ready = ready & bitwise[subsys]
	#print("Ready on zero. Current value is: " + format(ready, '#010b'))

def ready_reset():
	global ready
	global tryToSendCount
	global shadowPayload

	ready = int('0b01111011', 2)
	tryToSendCount = 0
	shadowPayload["state"]["reported"].clear()

def ready_pass():
	global tryToSendCount

	tryToSendCount += 1


def function_handler(event, context):
	global shadowPayload
	global tryToSendCount

	serial = "000"
	subsys = context.client_context.custom['subject'].split("/")[0]
	try:
		serial = context.client_context.custom['subject'].split("/")[1]
	except:
		pass

	print("Incoming event: " + subsys + " from board ID: " + serial)

	if subsys == "$aws":
		# Print confirmation
		print("Device shadow updated: " + str(event))
	else:
		if subsys == "inference":
			for inference_timestamp in event["history"]:
				for inference_result in inference_timestamp['last']:
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
