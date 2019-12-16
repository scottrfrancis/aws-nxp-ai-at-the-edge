FROM torizon/arm64v8-debian-base

WORKDIR /home/torizon

RUN apt update
RUN apt install -y libgstreamer1.0-0 gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly \
    gstreamer1.0-libav gstreamer1.0-doc gstreamer1.0-tools gstreamer1.0-x \
    gstreamer1.0-alsa gstreamer1.0-gl gstreamer1.0-gtk3 gstreamer1.0-qt5 \
    gstreamer1.0-pulseaudio

RUN apt install -y python3 python3-pip python3-gst-1.0 python3-dev gcc pkg-config
RUN apt install -y libcairo2-dev libjpeg-dev libgif-dev
RUN apt install -y python3-gi gobject-introspection gir1.2-gtk-3.0 python3-gi-cairo

RUN pip3 install setuptools wheel pycairo
RUN pip3 install numpy Pillow
RUN pip3 install imageio requests flask flask_restful flask_cors

RUN apt install -y build-essential cmake git
RUN git clone --recursive https://github.com/neo-ai/neo-ai-dlr.git
#RUN cd neo-ai-dlr;git checkout v1.0;mkdir build;cd build;cmake ..;make -j`nproc`
RUN cd neo-ai-dlr;mkdir build;cd build;cmake ..;make -j`nproc`
RUN cd neo-ai-dlr/python;python3 setup.py install --user

COPY resources .

ENTRYPOINT python3 inference.py

#CMD gst-launch-1.0 v4l2src device=/dev/video4 ! videoconvert ! videoscale ! v4l2sink device=/dev/video14
#CMD gst-launch-1.0 v4l2src device=/dev/video4 ! videoconvert ! videoscale ! xvimagesink
#ENTRYPOINT cd v1;python3 inference.py
