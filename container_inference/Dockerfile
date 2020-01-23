FROM torizonextras/camera-inference-base
#FROM torizon/arm64v8-debian-weston-vivante

WORKDIR /home/torizon

RUN pip3 install requests flask flask_restful flask_cors

RUN mkdir -p model
COPY model model
COPY inference.py .

ENTRYPOINT v4l2-ctl -c auto_white_balance=1; v4l2-ctl -c auto_gain=1; v4l2-ctl -c exposure_auto=1;v4l2-ctl -d /dev/video0 -p 15;rm -rf *.png;python3 inference.py
