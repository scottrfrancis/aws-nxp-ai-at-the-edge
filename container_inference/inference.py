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

im_width_out = 640
im_height_out = 480
#im_width_out = 2592
#im_height_out = 1944

net_input_size= 240

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
    #******** INSERT YOUR INFERENCE HERE ********
    img2 = cv2.resize(img, (net_input_size,int(net_input_size/4*3)))#, interpolation = cv2.INTER_NEAREST)
    img2 = cv2.copyMakeBorder(img2,int(net_input_size/8),int(net_input_size/8),0,0,cv2.BORDER_CONSTANT,value=(0,0,0))

    buf=img2.astype('float64')

    # Mean and Std deviation of the RGB colors from dataset
    redmean=255*0.4401859057358472
    gremean=255*0.5057172186334968
    blumean=255*0.5893379173439015
    redstd=255*0.24873837809532068
    grestd=255*0.17898858615083552
    blustd=255*0.3176466480114065

    #prepare image to input
    net_input = buf.reshape((net_input_size*net_input_size ,3))
    net_input =np.transpose(buf)
    net_input[0,:] = net_input[0,:]-redmean
    net_input[0,:] = net_input[0,:]/redstd
    net_input[1,:] = net_input[1,:]-gremean
    net_input[1,:] = net_input[1,:]/grestd
    net_input[2,:] = net_input[2,:]-blumean
    net_input[2,:] = net_input[2:]/blustd

    #Run the model
    tbefore = time()
    outputs = model.run({'data': net_input})
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

        x1=int(bounding_boxes[i][1]*im_width_out/net_input_size)
        y1=int((bounding_boxes[i][0]-net_input_size/8)*im_height_out/(net_input_size*3/4))
        x2=int(bounding_boxes[i][3]*im_width_out/net_input_size)
        y2=int((bounding_boxes[i][2]-net_input_size/8)*im_height_out/(net_input_size*3/4))

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
    global tlast
    global tbefore
    global tafter

    t0=time()
    sample = sink.emit("pull-sample")
    global_buf = sample.get_buffer()
    caps = sample.get_caps()
    im_height_in = caps.get_structure(0).get_value('height')
    im_width_in = caps.get_structure(0).get_value('width')
    mem = global_buf.get_all_memory()
    t1=time()
    success, arr = mem.map(Gst.MapFlags.READ)
    t2=time()
    img = np.ndarray((im_height_in,im_width_in,3),buffer=arr.data,dtype=np.uint8)
    t3=time()
    pasta_detection(img)
    t4=time()
    appsource.emit("push-buffer", Gst.Buffer.new_wrapped(img.tobytes()))
    t5=time()
    mem.unmap(arr)

    try:
        print("FRAME:",time()-tlast,"FPS:",1/(time()-tlast))
    except:
        print("first frame")
    tlast=time()

    ttotal = tlast-t0
    print("t1=",(t1-t0)," - ",100*(t1-t0)/(ttotal),"%")
    print("t2=",(t2-t1)," - ",100*(t2-t1)/(ttotal),"%")
    print("t3=",(t3-t2)," - ",100*(t3-t2)/(ttotal),"%")
    print("t4a=",(tbefore-t3)," - ",100*(tbefore-t3)/(ttotal),"%")
    print("t4b=",(tafter-tbefore)," - ",100*(tafter-tbefore)/(ttotal),"%")
    print("t4c=",(t4-tafter)," - ",100*(t4-tafter)/(ttotal),"%")
    print("t5=",(t5-t4)," - ",100*(t5-t4)/(ttotal),"%")
    print("t6=",(tlast-t5)," - ",100*(tlast-t5)/(ttotal),"%")
    print("TOTAL=",ttotal)

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

    pipeline1_cmd="v4l2src device=/dev/video0 do-timestamp=True ! queue leaky=downstream ! videoscale n-threads=4 ! \
        video/x-raw,format=RGB,width="+str(im_width_out)+",height="+str(im_height_out)+" ! \
        queue leaky=downstream ! appsink name=sink max-buffers=5 \
        drop=True max-buffers=3 emit-signals=True"

    pipeline2_cmd = "appsrc name=appsource1 is-live=True block=True ! \
        video/x-raw,format=RGB,width="+str(im_width_out)+",height="+ \
        str(im_height_out)+",framerate=10/1,interlace-mode=(string)progressive ! \
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
