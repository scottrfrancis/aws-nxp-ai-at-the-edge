#
# Copyright 2019 Toradex AG. or its affiliates. All Rights Reserved.
#

# flask
from flask import Flask, request
from flask_restful import Resource, Api
from json import dumps
from flask import jsonify
from flask_cors import CORS, cross_origin
from deviceInfo import DeviceInfo

# global sensor
deviceInfo = DeviceInfo()

# flask route
app = Flask(__name__)
# add cors
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
api = Api(app)

# GET requests for CPU
@app.route('/cpu')
@cross_origin()
def cpu_info():
    ret = {'cores': deviceInfo.getCPUCoresCount(), 'temperatures': [],
           'usage': 0}
    ret['temperatures'] = {'A53': deviceInfo.getTemperatureCPUA53(
    ), 'A72': deviceInfo.getTemperatureCPUA72()}
    ret['usage'] = deviceInfo.getCPUUsage()
    return jsonify(ret)

# GET requests for GPU
@app.route('/gpu')
@cross_origin()
def gpu_info():
    ret = {'cores': 2, 'temperatures': [],
           'memoryUsage': deviceInfo.getGPUMemoryUsage()}
    ret['temperatures'] = {'GPU0': deviceInfo.getTemperatureGPU0(
    ), 'GPU1': deviceInfo.getTemperatureGPU1()}
    return jsonify(ret)

# GET requests for GPU
@app.route('/ram')
@cross_origin()
def ram_info():
    ret = {'total': deviceInfo.getRAMTotal(), 'usage': deviceInfo.getRAMUsage(),
           'free': deviceInfo.getRAMFree()}
    return jsonify(ret)

# GET requests for GPU
@app.route('/info')
@cross_origin()
def info():
    retRam = {'total': deviceInfo.getRAMTotal(), 'usage': deviceInfo.getRAMUsage(),
           'free': deviceInfo.getRAMFree()}
    
    retGpu = {'cores': 2, 'temperatures': [],
           'memoryUsage': deviceInfo.getGPUMemoryUsage()}
    retGpu['temperatures'] = {'GPU0': deviceInfo.getTemperatureGPU0(
    ), 'GPU1': deviceInfo.getTemperatureGPU1()}
    #retGpu = {}

    retCpu = {'cores': deviceInfo.getCPUCoresCount(), 'temperatures': [],
           'usage': 0}
    retCpu['temperatures'] = {'A53': deviceInfo.getTemperatureCPUA53(
    ), 'A72': deviceInfo.getTemperatureCPUA72()}
    retCpu['usage'] = deviceInfo.getCPUUsage()
    
    ret = {'ram': retRam, 'gpu': retGpu, 'cpu': retCpu}
    return jsonify(ret)

if __name__ == '__main__':
    print("Flask working well")
    app.run(host='0.0.0.0', port='5001')
else:
    print(__name__)
    print("Flask not working")

# This is a dummy handler and will not be invoked
# Instead the code above will be executed in an infinite loop for our example


def function_handler(event, context):
    return
