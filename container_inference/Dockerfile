FROM torizonextras/camera-inference-base
#FROM torizon/arm64v8-debian-weston-vivante

WORKDIR /home/torizon

RUN mkdir -p model
COPY model model

RUN pip3 install requests flask flask_restful flask_cors

COPY inference.py .

ENTRYPOINT v4l2-ctl -c auto_white_balance=2;v4l2-ctl -c auto_gain=2;v4l2-ctl -c exposure_auto=1;python3 inference.py
