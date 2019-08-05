#
# Copyright 2019 Toradex AG. or its affiliates. All Rights Reserved.
#

# greengrass
#import greengrasssdk
import platform

# flask
from flask import Flask, request
from flask_restful import Resource, Api
from json import dumps
from flask import jsonify
from sensors import Sensors

# Creating a greengrass core sdk client
#client = greengrasssdk.client('iot-data')
# Retrieving platform information to send from Greengrass Core
my_platform = platform.platform()
# global sensor
deviceInfo = Sensors()

# flask route
app = Flask(__name__)
api = Api(app)

# GET for CPU temperatures
class Temperature(Resource):
	def get(self):
		global deviceInfo
		temp = deviceInfo.getTemperature()
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
