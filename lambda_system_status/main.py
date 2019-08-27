#
# Copyright 2019 Toradex AG. or its affiliates. All Rights Reserved.
#

# greengrass
import greengrasssdk
import platform

# rest consume
import requests

# mqtt thread
import threading
import time
import json

# Creating a greengrass core sdk client
client = greengrasssdk.client('iot-data')
# Retrieving platform information to send from Greengrass Core
my_platform = platform.platform()

# "THREAD" for MQTT connections
def greengrass_mqtt_run():
	while True:
		# cpu/data
		try:
			cpuData = requests.get("http://localhost:5001/cpu")
			client.publish(topic='cpu/data', payload=cpuData)
			print("Mqtt cpu/data published ...")
		except requests.exceptions.ConnectionError:
			print("Connection error, retry on next loop!")
		except Exception as e:
			print("Unknown exception: " + repr(e))
		# gpu/data
		try:
			gpuData = requests.get("http://localhost:5001/gpu")
			client.publish(topic='gpu/data', payload=gpuData)
			print("Mqtt gpu/data published ...")
		except requests.exceptions.ConnectionError:
			print("Connection error, retry on next loop!")
		except Exception as e:
			print("Unknown exception: " + repr(e))
		# ram/data
		try:
			ramData = requests.get("http://localhost:5001/ram")
			client.publish(topic='ram/data', payload=ramData)
			print("Mqtt ram/data published ...")
		except requests.exceptions.ConnectionError:
			print("Connection error, retry on next loop!")
		except Exception as e:
			print("Unknown exception: " + repr(e))

		# Send data periodically
		time.sleep(5)

t = threading.Thread(target=greengrass_mqtt_run)
t.start()

# This is a dummy handler and will not be invoked
# Instead the code above will be executed in an infinite loop for our example
def function_handler(event, context):
	return
