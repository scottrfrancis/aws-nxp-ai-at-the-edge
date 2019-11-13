import common_util.overlays as overlays
import common_util.gstreamer_video_pipeline as gst_pipeline
import common_util.colors as colors
import argparse
import gc
import sys

# images
from PIL import Image
from io import BytesIO
import io
import base64
import pickle
from pprint import pprint
import imageio

import os
import warnings
import pickle
import time
import array as arr
from queue import Queue
import requests
import cairo
import numpy as np
import threading

from gi.repository import Gst
import gi
gi.require_version('Gst', '1.0')

# inference framework
from dlr import DLRModel

if (sys.version_info[0] < 3):
    sys.exit("This sample requires Python 3. Please install Python 3!")

# ------------------------------------------------------------------ INFERENCE
class_names =['shell','elbow','penne','tortellini', 'farfalle']

# RGB means
redmean=255*0.4401859057358472
gremean=255*0.5057172186334968
blumean=255*0.5893379173439015
redstd=255*0.24873837809532068
grestd=255*0.17898858615083552
blustd=255*0.3176466480114065

# load the model
model = DLRModel('./model/', 'cpu')

try:
    # size used for inference
    net_input_size=224
    number_of_pixels = net_input_size*net_input_size
    image_in=[0]*(net_input_size*net_input_size*3)
    input_data = {'data': image_in}
    outputs = model.run(input_data) #need to be a list of input arrays matching input names
    print('input size of the model: 224')
except:
    # size used for inference
    net_input_size=240
    number_of_pixels = net_input_size*net_input_size
    print('input size of the model: 240')

#*************************START FLASK**********************
history = Queue(1000)
from flask import Flask
from flask_restful import Resource, Api
from flask_cors import CORS, cross_origin
app = Flask(__name__)
# add cors
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
api = Api(app)

@app.route('/inference/')
@cross_origin()
def inference_web():
    global last_inference
    str_history = '{"history": ['
    while history.qsize()>0 :
        history_item = history.get(block=True, timeout=None)
        str_history = str_history + history_item.json()
        if history.qsize()>0 :
            str_history = str_history + ','
    str_history = str_history + ']}'
    return str_history

@app.route('/inference/last')
@cross_origin()
def last_inference_web():
    global last_inference
    return last_inference.json()

#************************* END FLASK **********************

class result:
    def __init__(self, score, object,xmin,ymin,xmax,ymax,time):
        self.score = score
        self.object = object
        self.xmin = xmin
        self.ymin = ymin
        self.xmax = xmax
        self.ymax = ymax
        self.time = time
    def json(self):
       return ('{"score": "%s","object": "%s","xmin": "%s","ymin": "%s","xmax": "%s","ymax": "%s"}'
                   %(self.score,self.object,self.xmin,self.ymin,self.xmax,self.ymax))

class inference:
    def __init__(self, timestamp, inference_time,results):
        self.timestamp = timestamp
        self.inference_time = inference_time
        self.results = results
    def json(self):
        results = ('{"timestamp": "%s","inference_time": "%s",'
                    %(self.timestamp,self.inference_time))
        results = results + '"last":['
        for i in range(len(self.results)):
            results = results + self.results[i].json()
            if(i<len(self.results)-1):
                results = results + ','
        results = results +']}'
        return results

last_inference = inference(0,0,[])

def pasta_detection(image_in, width = 320, height = 240):
    global last_inference

    t1 = time.time()

    f1 = open('/dev/shm/tmp_image.jpg', 'wb')
    f1.write(image_in)
    f1.close()
    try: img
    except NameError: pass
    else: del(img)

    img = imageio.imread('/dev/shm/tmp_image.jpg')
    img = img.astype('float64')

    image_in = img[	int(img.shape[0]/2-net_input_size/2):int(img.shape[0]/2+net_input_size/2), \
    		int(img.shape[1]/2-net_input_size/2):int(img.shape[1]/2+net_input_size/2),:]
    image_in = image_in.reshape((number_of_pixels ,3))
    image_in =np.transpose(image_in)
    image_in[0,:] = image_in[0,:]-redmean
    image_in[0,:] = image_in[0,:]/redstd
    image_in[1,:] = image_in[1,:]-gremean
    image_in[1,:] = image_in[1,:]/grestd
    image_in[2,:] = image_in[2,:]-blumean
    image_in[2,:] = image_in[2:]/blustd

    input_data = {'data': image_in}
    t2 = time.time()
    outputs = model.run(input_data) #need to be a list of input arrays matching input names
    t3 = time.time()

    objects=outputs[0][0]
    scores=outputs[1][0]
    bounding_boxes=outputs[2][0]

    i=0
    result_set=[]
    while (scores[i]>=0.4) :

        if int(objects[i]) <= 4:
            this_object=class_names[int(objects[i])]
            this_result = result(
                        score= scores[i],
                        object= this_object,
                        xmin= bounding_boxes[i][0]+160-(net_input_size/2),
                        xmax= bounding_boxes[i][2]+160-(net_input_size/2),
                        ymin= bounding_boxes[i][1]+120-(net_input_size/2),
                        ymax= bounding_boxes[i][3]+120-(net_input_size/2),
                        time=t3)

            if((bounding_boxes[i][2]-bounding_boxes[i][0]<=net_input_size/2)
                and(bounding_boxes[i][3]-bounding_boxes[i][1]<=net_input_size/2)):
               result_set.append(this_result)
            #result_set.append(this_result)

        i=i+1

    last_inference = inference(t2,t3-t2,result_set)
    if(history.full()==False): #FLASK
       history.put(last_inference, block=True, timeout=None)
    t4 = time.time()
    return result_set

# ------------------------------------------------------------------ END INFERENCE

def save_pickle(frame):
    f=open('arquivo.pickle', 'wb')
    pickle.dump(frame, f)

def color_by_id(id):
    """Returns a somewhat-unique color for the given class ID"""
    return [c / 255 for c in colors.COLORS[id % len(colors.COLORS)]]

def draw_bb(pipeline, frame, width = 320, height = 240):
    im = Image.open('/dev/shm/tmp_image.jpg')
    im.putalpha(256) # create alpha channel
    arr = np.array(im)
    _height, _width, channels = arr.shape
    surface = cairo.ImageSurface.create_for_data(arr, cairo.FORMAT_RGB24, width, height)
    pipeline._buffer = surface
    pipeline._render(frame)

def main():
    global last_inference
    print("Calling video and inference")
    infCount = 0
    lastTime = 0.0

    with gst_pipeline.VideoOverlayPipeline(
            "Pasta demo",
            "/dev/video4") as pipeline:

        while pipeline.running:
            # Get a frame of video from the pipeline.
            frame = pipeline.get_frame()
            if frame is None:
                print("Frame is none ...")
                break

            # call the inference
            ret = pasta_detection(frame.data)
            infCount = infCount + 1

            # put the overlays on the queue
            pipeline.clear_overlay()

            if ret != None:
                for item in ret:
                    bbox = overlays.BoundingBox(
                        (item.xmin)/320,
                        (item.ymin)/240,
                        (item.xmax - item.xmin)/320,
                        (item.ymax - item.ymin)/240,
                        item.object,
                        bg_color=color_by_id(5))
                    pipeline.add_overlay(bbox)

            #pipeline.add_overlay(
            #    overlays.Text("FPS " + str(1/(time.time()-lastTime)),
            #                                x=0,
            #                                y=0,
            #                                bg_color=color_by_id(-1)))

            pipeline.add_overlay(
                overlays.Text("Inference Time " + "{:.2f}".format(last_inference.inference_time),
                                            x=0,
                                            y=0,
                                            bg_color=color_by_id(-1)))

            # draw bound boxes
            draw_bb(pipeline, frame.data, 320, 240)
            # get the aux time to get fps
            lastTime=time.time()

            gc.collect()

if (__name__ == "__main__"):
    thread1 = threading.Thread(target = main)
    thread1.start()

if __name__ == '__main__':
    print("Flask working well")
    app.run(host='0.0.0.0', port='5003')
else:
    print(__name__)
    print("Flask not working")
