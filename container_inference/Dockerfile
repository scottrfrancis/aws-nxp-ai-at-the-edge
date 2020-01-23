FROM torizonextras/camera-inference-base
#FROM torizon/arm64v8-debian-weston-vivante

WORKDIR /home/torizon

RUN mkdir -p model
COPY model model

RUN pip3 install requests flask flask_restful flask_cors

RUN apt-get install -y sshpass openssh-client

RUN apt install -y libcairo2-dev
RUN git clone https://github.com/pygobject/pycairo.git
RUN cd pycairo && python3 setup.py build && python3 setup.py install
RUN apt install -y python3-gi python3-gi-cairo gobject-introspection

COPY inference.py .

ENTRYPOINT v4l2-ctl -c auto_white_balance=1; v4l2-ctl -c auto_gain=1; v4l2-ctl -c exposure_auto=1;v4l2-ctl -d /dev/video0 -p 15;rm -rf *.png;python3 inference.py
