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
rest = {
	"cpu/data": "http://localhost:" + system_data_port + "/cpu",
	"gpu/data": "http://localhost:" + system_data_port + "/gpu",
	"ram/data": "http://localhost:" + system_data_port + "/ram",
	"cam/data": "http://localhost:" + system_data_port + "/cam",
	"cb/data": "http://localhost:" + system_control_port + "/cb",
	"led/data": "http://localhost:" + system_control_port + "/led"
}

# Creating a greengrass core sdk client
client = greengrasssdk.client('iot-data')

# "THREAD" for MQTT connections
def greengrass_mqtt_run():
	while True:
		for topicMQTT,url in rest.items():
			# Basically bridge REST to MQTT
			try:
				getData = requests.get(url)
				client.publish(topic=topicMQTT, payload=getData)
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
