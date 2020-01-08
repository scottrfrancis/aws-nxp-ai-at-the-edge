import faulthandler; faulthandler.enable()
import sys, os, time, re,signal
import gi
gi.require_version('Gst', '1.0')
gi.require_version('Gtk', '3.0')
gi.require_foreign('cairo')
from time import time
from time import sleep
from gi.repository import GLib, Gst
import cairo
from dlr import DLRModel
import numpy as np
import imageio
import gc
from draw_overlay import print_inference,draw_bb
#  -----------------   ----------   -----------   ------------   --------------
#  |source (camera)|---|app sink|---|inference|---|app source|---|sink (video)|
#  -----------------   ----------   -----------   ------------   --------------

# Inference
def inference(buffer):
    #***** Insert your inference Code here *****
    global model
    global outputs
    global net_input_size
    global last_inference_time

    #img = imageio.imread('./tmp_image.jpg')
    #img = img.astype('float64')

    img=buffer.astype('float64')

    net_input_size= 224

    # Mean and Std deviation of the RGB colors from dataset
    redmean=255*0.4401859057358472
    gremean=255*0.5057172186334968
    blumean=255*0.5893379173439015
    redstd=255*0.24873837809532068
    grestd=255*0.17898858615083552
    blustd=255*0.3176466480114065

    #crop input image from the center
    image_in = img[	int(img.shape[0]/2-net_input_size/2):int(img.shape[0]/2+net_input_size/2), \
    		int(img.shape[1]/2-net_input_size/2):int(img.shape[1]/2+net_input_size/2),:]

    #prepare image to input
    image_in = image_in.reshape((net_input_size*net_input_size ,3))
    image_in =np.transpose(image_in)
    image_in[0,:] = image_in[0,:]-redmean
    image_in[0,:] = image_in[0,:]/redstd
    image_in[1,:] = image_in[1,:]-gremean
    image_in[1,:] = image_in[1,:]/grestd
    image_in[2,:] = image_in[2,:]-blumean
    image_in[2,:] = image_in[2:]/blustd

    #Run the model
    t1 = time()
    outputs = model.run({'data': image_in})
    last_inference_time = time()-t1
    #***** Enf of your inference Code *****

# Pipeline 1 output
def get_frame(sink, data):
    global caps
    global data_frame
    global sample

    sample = sink.emit("pull-sample")
    global_buf = sample.get_buffer()
    caps = sample.get_caps()

    arr = np.ndarray(
        (caps.get_structure(0).get_value('height'),
         caps.get_structure(0).get_value('width'),
         3),
        buffer=global_buf.extract_dup(0, global_buf.get_size()),
        dtype=np.uint8)

    inference(arr)
    gc.collect()
    return Gst.FlowReturn.OK

# Init Pipeline 2

def on_draw(overlay, context, _timestamp, _duration):
    global outputs
    global net_input_size
    global last_inference_time

    try:
        print_inference(context,last_inference_time)

        objects=outputs[0][0]
        scores=outputs[1][0]
        bounding_boxes=outputs[2][0]

        i = 0
        while (scores[i]>=0.5) :
            if int(objects[i]) <= 4:
                xmin= int(bounding_boxes[i][0]+160-(net_input_size/2))
                xmax= int(bounding_boxes[i][2]+160-(net_input_size/2))
                ymin= int(bounding_boxes[i][1]+120-(net_input_size/2))
                ymax= int(bounding_boxes[i][3]+120-(net_input_size/2))
                draw_bb(context,xmin,xmax,ymin,ymax,int(objects[i]))
            i=i+1
    except:
        pass

def main():
    print("Pasta Demo inference started\n")
    # SagemakerNeo init
    global model

    model = DLRModel('./model', 'cpu')

    # Gstreamer Init
    Gst.init(None)

    #pipeline = Gst.parse_launch("multifilesrc location='tmp_image.jpg' loop=true ! jpegdec ! videoconvert ! videoscale ! videorate !\
    #pipeline = Gst.parse_launch("videotestsrc ! videoconvert ! \
    #pipeline = Gst.parse_launch("multifilesrc location='tmp_image.jpg' loop=true ! jpegdec ! videoconvert ! videoscale ! videorate !\
    # pipeline = Gst.parse_launch("v4l2src device=/dev/video0 ! videoconvert ! videorate ! videoscale !\
    #     video/x-raw,format=RGB,widht=320,height=240,framerate=8/1 !  \
    #     tee name=t ! queue ! videoconvert ! cairooverlay name=overlay ! \
    #     videoconvert ! video/x-raw,format=RGB,width=320,height=240 ! \
    #     videoconvert ! v4l2sink device=/dev/video14 t. ! \
    #     queue ! videoconvert ! videoscale ! \
    #     video/x-raw,format=RGB,width=320,height=240 ! appsink name=sink ")
    pipeline = Gst.parse_launch("v4l2src device=/dev/video0 ! videoconvert ! videorate ! videoscale !\
        video/x-raw, width=320, height=240 !  \
        tee name=t ! queue ! videoconvert ! cairooverlay name=overlay ! \
        videoconvert ! video/x-raw,format=RGB,width=320,height=240 ! \
        videoconvert ! v4l2sink device=/dev/video14 t. ! \
        queue ! videoconvert ! videoscale ! \
        video/x-raw,format=RGB,width=320,height=240 ! appsink name=sink ")
    #pipeline = Gst.parse_launch('v4l2src device=/dev/video0 ! videoconvert ! videoscale ! video/x-raw, width=320, height=240 ! v4l2sink device=/dev/video14 sync=false')

    appsink = pipeline.get_by_name('sink')
    appsink.set_property("emit-signals", True)
    appsink.connect("new-sample", get_frame, appsink)

    pipeline.set_state(Gst.State.PLAYING)
    cairo_overlay = pipeline.get_by_name('overlay')
    cairo_overlay.connect('draw', on_draw)

    bus = pipeline.get_bus()

    # Main Loop
    while True:
        message = bus.timed_pop_filtered(10000, Gst.MessageType.ANY)
        if message:
            if message.type == Gst.MessageType.EOS:
                print("bus: End-Of-Stream reached.")
                appsink.emit("eos")
                break

    # Free resources
    pipeline.set_state(Gst.State.NULL)

if __name__ == "__main__":
    main()
