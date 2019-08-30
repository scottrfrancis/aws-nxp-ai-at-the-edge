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

system_data_port = "5001"
conveyor_belt_port = "5002"
rest = {
	"cpu/data": "http://localhost:" + system_data_port + "/cpu",
	"gpu/data": "http://localhost:" + system_data_port + "/gpu",
	"ram/data": "http://localhost:" + system_data_port + "/ram",
	"cam/data": "http://localhost:" + system_data_port + "/cam",
	"cb/data": "http://localhost:" + conveyor_belt_port + "/cb",
	"led/data": "http://localhost:" + conveyor_belt_port + "/led"
}

# Creating a greengrass core sdk client
client = greengrasssdk.client('iot-data')
# Retrieving platform information to send from Greengrass Core
my_platform = platform.platform()

# "THREAD" for MQTT connections
def greengrass_mqtt_run():
	while True:
		# cpu/data
		try:
			cpuData = requests.get(rest["cpu/data"])
			client.publish(topic='cpu/data', payload=cpuData)
			print("Mqtt cpu/data published ...")
		except requests.exceptions.ConnectionError:
			print("Connection error: cpu/data, retry on next loop!")
		except Exception as e:
			print("Unknown exception: " + repr(e))
		# gpu/data
		try:
			gpuData = requests.get(rest["gpu/data"])
			client.publish(topic='gpu/data', payload=gpuData)
			print("Mqtt gpu/data published ...")
		except requests.exceptions.ConnectionError:
			print("Connection error: gpu/data, retry on next loop!")
		except Exception as e:
			print("Unknown exception: " + repr(e))
		# ram/data
		try:
			ramData = requests.get(rest["ram/data"])
			client.publish(topic='ram/data', payload=ramData)
			print("Mqtt ram/data published ...")
		except requests.exceptions.ConnectionError:
			print("Connection error: ram/data, retry on next loop!")
		except Exception as e:
			print("Unknown exception: " + repr(e))
		# cam/data
		try:
			ramData = requests.get(rest["cam/data"])
			client.publish(topic='cam/data', payload=ramData)
			print("Mqtt cam/data published ...")
		except requests.exceptions.ConnectionError:
			print("Connection error: cam/data, retry on next loop!")
		except Exception as e:
			print("Unknown exception: " + repr(e))
		# cb/data
		try:
			ramData = requests.get(rest["cb/data"])
			client.publish(topic='cb/data', payload=ramData)
			print("Mqtt cb/data published ...")
		except requests.exceptions.ConnectionError:
			print("Connection error: cb/data, retry on next loop!")
		except Exception as e:
			print("Unknown exception: " + repr(e))
		# led/data
		try:
			ramData = requests.get(rest["led/data"])
			client.publish(topic='led/data', payload=ramData)
			print("Mqtt led/data published ...")
		except requests.exceptions.ConnectionError:
			print("Connection error: led/data, retry on next loop!")
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
