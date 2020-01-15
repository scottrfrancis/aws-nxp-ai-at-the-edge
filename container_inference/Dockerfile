FROM torizon/arm64v8-debian-wayland-base-vivante AS base

WORKDIR /home/torizon

RUN apt-get -y update && apt-get install -y \
    libopencl-vivante1 \
    libopencl-vivante1-dev \
    libclc-vivante1 \
    libllvm-vivante1 \
    libgal-vivante1 \
    libvsc-vivante1 \
    && apt-get clean && apt-get autoremove

RUN apt-get -y update && apt-get install -y \
    python3 python3-pip python3-dev libatlas-base-dev \
    cmake build-essential gcc g++ git \
    && apt-get clean && apt-get autoremove

RUN pip3 install setuptools wheel

RUN pip3 install numpy Pillow

RUN apt-get -y update && apt-get install -y \
    libgstreamer1.0-0 gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly \
    gstreamer1.0-libav gstreamer1.0-doc gstreamer1.0-tools gstreamer1.0-x \
    gstreamer1.0-alsa gstreamer1.0-gl gstreamer1.0-gtk3 gstreamer1.0-qt5 \
    gstreamer1.0-pulseaudio v4l-utils \
    && apt-get clean && apt-get autoremove

RUN apt-get -y update && apt-get install -y \
    libcairo2-dev libjpeg-dev libgif-dev \
    python3-gi gobject-introspection gir1.2-gtk-3.0 python3-gi-cairo \
    && apt-get clean && apt-get autoremove

#install cv2
RUN apt-get -y update && apt-get install -y \
    libgtk2.0-dev pkg-config libavcodec-dev libavformat-dev libswscale-dev \
    libtbb2 libtbb-dev libjpeg-dev libpng-dev libtiff-dev libdc1394-22-dev \
    && apt-get clean && apt-get autoremove

RUN git clone https://github.com/opencv/opencv.git
RUN cd opencv && mkdir -p build && cd build && cmake ../;make && make install

RUN apt-get -y update && apt-get install -y \
    python3-gst-1.0 \
    && apt-get clean && apt-get autoremove

RUN apt install -y build-essential cmake git
RUN git clone --recursive https://github.com/neo-ai/neo-ai-dlr.git
RUN cd neo-ai-dlr;mkdir build;cd build;cmake ..;make -j`nproc`
RUN cd neo-ai-dlr/python;python3 setup.py install --user

RUN pip3 install requests flask flask_restful flask_cors

RUN mkdir model
COPY model model

COPY inference.py .
ENTRYPOINT v4l2-ctl -c auto_white_balance=1;v4l2-ctl -c auto_gain=1;v4l2-ctl -c exposure_auto=1;python3 inference.py
#;dmesg -e | tail -n 150
