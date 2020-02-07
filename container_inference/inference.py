import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstApp', '1.0')
from gi.repository import GLib, Gst, GstApp
from time import time
from dlr import DLRModel
import numpy as np
import gc
import cv2
from queue import Queue
import threading
import datetime

width_out = 640
height_out = 480
nn_input_size= 128
class_names =['shell','elbow','penne','tortellini','farfalle']
colors=[(0xFF,0x83,0x00),(0xFF,0x66,0x00),(0xFF,0x00,0x00),(0x99,0xFF,0x00),(0x00,0x00,0xFF),(0x00,0xFF,0x00)]

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
#************************* END FLASK **********************

# Inference
def pasta_detection(img):
    global last_inference
    global tbefore
    global tafter
    global t_between_frames
    #******** INSERT YOUR INFERENCE HERE ********

    nn_input=cv2.resize(img, (nn_input_size,int(nn_input_size/4*3)))#, interpolation = cv2.INTER_NEAREST)
    nn_input=cv2.copyMakeBorder(nn_input,int(nn_input_size/8),int(nn_input_size/8),0,0,cv2.BORDER_CONSTANT,value=(0,0,0))

    # Mean and Std deviation of the RGB colors from dataset
    mean=[112.247175,128.957835,150.280935]
    std=[63.42819,45.64194,80.99973]

    #prepare image to input
    nn_input=nn_input.astype('float64')
    nn_input=nn_input.reshape((nn_input_size*nn_input_size ,3))
    nn_input=np.transpose(nn_input)
    nn_input[0,:] = nn_input[0,:]-mean[0]
    nn_input[0,:] = nn_input[0,:]/std[0]
    nn_input[1,:] = nn_input[1,:]-mean[1]
    nn_input[1,:] = nn_input[1,:]/std[1]
    nn_input[2,:] = nn_input[2,:]-mean[2]
    nn_input[2,:] = nn_input[2,:]/std[2]

    #Run the model
    tbefore = time()
    outputs = model.run({'data': nn_input})
    tafter = time()
    last_inference_time = tafter-tbefore
    objects=outputs[0][0]
    scores=outputs[1][0]
    bounding_boxes=outputs[2][0]

    #***********FLASK*******
    result_set=[]
    #***********END OF FLASK*******
    i = 0
    while (scores[i]>0.4):
        y1=int((bounding_boxes[i][1]-nn_input_size/8)*width_out/nn_input_size)
        x1=int((bounding_boxes[i][0])*height_out/(nn_input_size*3/4))
        y2=int((bounding_boxes[i][3]-nn_input_size/8)*width_out/nn_input_size)
        x2=int((bounding_boxes[i][2])*height_out/(nn_input_size*3/4))

        #***********FLASK*******
        this_object=class_names[int(objects[i])]
        this_result = result(score= scores[i],object= this_object,
            xmin= x1,xmax= x2,ymin= y1,ymax= y2,time=tafter)
        result_set.append(this_result)
        #***********END OF FLASK*******# def signal_handler(signal, frame):
        object_id=int(objects[i])
        cv2.rectangle(img,(x2,y2),(x1,y1),colors[object_id%len(colors)],2)
        cv2.rectangle(img,(x1+50,y2+15),(x1,y2),colors[object_id%len(colors)],cv2.FILLED)
        cv2.putText(img,class_names[object_id],(x1,y2+10), cv2.FONT_HERSHEY_SIMPLEX, 0.4,(255,255,255),1,cv2.LINE_AA)
        i=i+1

    cv2.rectangle(img,(115,17),(0,0),(0,0,0),cv2.FILLED)
    #cv2.putText(img,"inf. time: %.3fs"%last_inference_time+" fps: %.2f"%(1/t_between_frames),(3,12), cv2.FONT_HERSHEY_SIMPLEX, 0.4,(255,255,255),1,cv2.LINE_AA)
    cv2.putText(img,"inf. time: %.3fs"%last_inference_time,(3,12), cv2.FONT_HERSHEY_SIMPLEX, 0.4,(255,255,255),1,cv2.LINE_AA)

    #***********FLASK*******
    last_inference = inference(tbefore,last_inference_time,result_set)
    if(history.full()==False): #FLASK
       history.put(last_inference, block=True, timeout=None)
    #***********END OF FLASK*******

    #******** END OF YOUR INFERENCE CODE ********

# Pipeline 1 output
def get_frame(sink, data):
    global appsource

    sample = sink.emit("pull-sample")
    global_buf = sample.get_buffer()
    caps = sample.get_caps()
    im_height_in = caps.get_structure(0).get_value('height')
    im_width_in = caps.get_structure(0).get_value('width')
    mem = global_buf.get_all_memory()
    success, arr = mem.map(Gst.MapFlags.READ)
    img = np.ndarray((im_height_in,im_width_in,3),buffer=arr.data,dtype=np.uint8)
    pasta_detection(img)
    appsource.emit("push-buffer", Gst.Buffer.new_wrapped(img.tobytes()))
    mem.unmap(arr)

    return Gst.FlowReturn.OK

def main():
    print("Pasta Demo inference started\n")
    # SagemakerNeo init
    global model
    global appsource
    global pipeline1
    global pipeline2

    model = DLRModel('./model', 'cpu')

    # Gstreamer Init
    Gst.init(None)

    pipeline1_cmd="v4l2src device=/dev/video0 do-timestamp=True ! \
        videoscale n-threads=4 method=nearest-neighbour ! \
        video/x-raw,format=RGB,width="+str(width_out)+",height="+str(height_out)+" ! \
        queue leaky=downstream max-size-buffers=1 ! appsink name=sink \
        drop=True max-buffers=1 emit-signals=True"

    pipeline2_cmd = "appsrc name=appsource1 is-live=True block=True ! \
        video/x-raw,format=RGB,width="+str(width_out)+",height="+ \
        str(height_out)+",framerate=20/1,interlace-mode=(string)progressive ! \
        videoconvert ! v4l2sink max-lateness=8000000000 device=/dev/video14"

    pipeline1 = Gst.parse_launch(pipeline1_cmd)
    appsink = pipeline1.get_by_name('sink')
    appsink.connect("new-sample", get_frame, appsink)

    pipeline2 = Gst.parse_launch(pipeline2_cmd)
    appsource = pipeline2.get_by_name('appsource1')

    pipeline1.set_state(Gst.State.PLAYING)
    bus1 = pipeline1.get_bus()
    pipeline2.set_state(Gst.State.PLAYING)
    bus2 = pipeline2.get_bus()

    # Main Loop
    while True:
        message = bus1.timed_pop_filtered(10000, Gst.MessageType.ANY)
        if message:
            if message.type == Gst.MessageType.ERROR:
                err,debug = message.parse_error()
                print("ERROR bus 1: ",err,debug)
                pipeline1.set_state(Gst.State.NULL)
                pipeline2.set_state(Gst.State.NULL)
                break

            if message.type == Gst.MessageType.WARNING:
                err,debug = message.parse_warning()
                print("bus 1: ",err,debug)

            if message.type == Gst.MessageType.STATE_CHANGED:
                old_state, new_state, pending_state = message.parse_state_changed()
                print("STATE Bus 1 - Changed from ",old_state," To: ",new_state)


        message = bus2.timed_pop_filtered(10000, Gst.MessageType.ANY)
        if message:
            if message.type == Gst.MessageType.ERROR:
                err,debug = message.parse_error()
                print("ERROR bus 2: ",err,debug)
                pipeline1.set_state(Gst.State.NULL)
                pipeline2.set_state(Gst.State.NULL)
                break

            if message.type == Gst.MessageType.WARNING:
                err,debug = message.parse_warning()
                print("bus 2: ",err,debug)

            if message.type == Gst.MessageType.STATE_CHANGED:
                old_state, new_state, pending_state = message.parse_state_changed()
                print("STATE Bus 2 - Changed from ",old_state," To: ",new_state)

    # Free resources
    pipeline1.set_state(Gst.State.NULL)
    pipeline2.set_state(Gst.State.NULL)

if (__name__ == "__main__"):
    thread1 = threading.Thread(target = main)
    thread1.start()

if __name__ == '__main__':
    print("Flask working well")
    app.run(host='0.0.0.0', port='5003')
else:
    print(__name__)
    print("Flask not working")
