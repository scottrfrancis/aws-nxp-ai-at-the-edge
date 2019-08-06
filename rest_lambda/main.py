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
from deviceInfo import DeviceInfo

# Creating a greengrass core sdk client
client = greengrasssdk.client('iot-data')
# Retrieving platform information to send from Greengrass Core
my_platform = platform.platform()
# global sensor
deviceInfo = DeviceInfo()

# flask route
app = Flask(__name__)
api = Api(app)

# GET requests for CPU 
@app.route('/cpu')
def cpu_info():
	ret = {'cores' : deviceInfo.getCPUCoresCount(), 'temperatures' : []}
	ret['temperatures'] = { 'A53': deviceInfo.getTemperatureCPUA53(), 'A72': deviceInfo.getTemperatureCPUA72() }
	return jsonify(ret)

# GET requests for GPU
@app.route('/gpu')
def gpu_info():
	ret = {'cores' : 2, 'temperatures' : []}
	ret['temperatures'] = { 'GPU0': deviceInfo.getTemperatureGPU0(), 'GPU1': deviceInfo.getTemperatureGPU1() }
	return jsonify(ret)

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
