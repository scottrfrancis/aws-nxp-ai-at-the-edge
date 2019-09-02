#
# Copyright 2019 Toradex AG. or its affiliates. All Rights Reserved.
#

# flask
from flask import Flask, request
from flask_restful import Resource, Api
from json import dumps
from flask import jsonify
from flask_cors import CORS, cross_origin
from deviceCtrl import DeviceCtrl

# Control LED and CB
deviceCtrl = DeviceCtrl()

# flask route
app = Flask(__name__)
# add cors
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
api = Api(app)

# GET requests for Conveyor Belt
@app.route('/cb/speed/<int:cb_percentage>')
@cross_origin()
def cb_pwm(cb_percentage):
    cb_ret = deviceCtrl.set_cb_speed(cb_percentage)
    return jsonify({"retval" : cb_ret})

@app.route('/cb')
@cross_origin()
def cb_pwm_get():
    return jsonify({
        "speed": deviceCtrl.get_cb_speed()
    })

# GET requests for LED
@app.route('/led/brightness/<int:led_percentage>')
@cross_origin()
def led_pwm(led_percentage):
    led_ret = deviceCtrl.set_led_brightness(led_percentage)
    return jsonify({"retval" : led_ret})

@app.route('/led')
@cross_origin()
def led_pwm_get():
    return jsonify({
        "brightness": deviceCtrl.get_led_brightness()
    })

if __name__ == '__main__':
    print("Flask working well")
    app.run(host='0.0.0.0', port='5002')
else:
    print(__name__)
    print("Flask not working")