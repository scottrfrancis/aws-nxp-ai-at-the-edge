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

system_data_port = "5001"
system_control_port = "5002"
inference_info_port = "5003"
rest = {
	"cpu/": "http://localhost:" + system_data_port + "/cpu",
	"gpu/": "http://localhost:" + system_data_port + "/gpu",
	"ram/": "http://localhost:" + system_data_port + "/ram",
	#"cam/": "http://localhost:" + system_data_port + "/cam",
	"info/": "http://localhost:" + system_data_port + "/info",
	"cb/": "http://localhost:" + system_control_port + "/cb",
	"led/": "http://localhost:" + system_control_port + "/led",
	"inference/": "http://localhost:" + inference_info_port + "/inference"
}

# Creating a greengrass core sdk client
client = greengrasssdk.client('iot-data')

# "THREAD" for MQTT connections
def greengrass_mqtt_run():
	boardSerial = 0
	while True:
		if not boardSerial:
			try:
				boardSerial = requests.get(rest["info/"]).json()["board-serial"]
			except Exception as e:
				print("Cannot get board serial: " + repr(e))
		for topicMQTT,url in rest.items():
			# Basically bridge REST to MQTT
			try:
				getData = requests.get(url)
				client.publish(topic=topicMQTT + str(boardSerial) + "/data", payload=getData)
				print("MQTT data published on " + topicMQTT)
			except requests.exceptions.ConnectionError:
				print("Connection error on topic " + topicMQTT + ", retry on next loop!")
			except Exception as e:
				print("Unknown exception on topic " + topicMQTT + ": " + repr(e))

		# Send data periodically
		time.sleep(5)

t = threading.Thread(target=greengrass_mqtt_run)
t.start()

# This is a dummy handler and will not be invoked
# Instead the code above will be executed in an infinite loop for our example
def function_handler(event, context):
	return
