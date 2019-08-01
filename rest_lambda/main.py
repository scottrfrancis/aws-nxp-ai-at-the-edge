#
# Copyright 2019 Toradex AG. or its affiliates. All Rights Reserved.
#

# greengrass
import greengrasssdk
import platform

# flask
from flask import Flask, request
from flask_restful import Resource, Api
from json import dumps
from flask import jsonify

# Creating a greengrass core sdk client
client = greengrasssdk.client('iot-data')
# Retrieving platform information to send from Greengrass Core
my_platform = platform.platform()
# global temp resource
temp = 0.0

# flask route
app = Flask(__name__)
api = Api(app)

# MQTT will get this every 5s so REST API will share this resource
def read_temperature():
	global temp
	f = open("/sys/class/thermal/thermal_zone0/temp", "r")
	temp = f.read()
	temp = float(temp) / 1000.0
	return

# GET for CPU temperatures
class Temperature(Resource):
	def get(self):
		read_temperature()
		ret = {'temperature': temp}
		return jsonify(ret)


api.add_resource(Temperature, '/temperature')  # Route_1

if __name__ == 'main':
	print("Flask working")
	app.run(host='0.0.0.0', port='5001')
else:
	print(__name__)
	print("Flask not working")

# This is a dummy handler and will not be invoked
# Instead the code above will be executed in an infinite loop for our example
def function_handler(event, context):
	return
