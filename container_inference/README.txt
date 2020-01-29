* To build:

docker build -t denisyuji/demo-inference . && docker push denisyuji/demo-inference

* To run:

sshpass -p 1 ssh -t torizon@apalis-imx8-06438725.local "docker stop weston;docker stop inference;docker pull denisyuji/pasta-demo-inference && docker run -e ACCEPT_FSL_EULA=1 -d --rm --name=weston --net=host --cap-add CAP_SYS_TTY_CONFIG -v /dev:/dev -v /tmp:/tmp -v /run/udev/:/run/udev/ --device-cgroup-rule='c 4:* rmw'  --device-cgroup-rule='c 13:* rmw' --device-cgroup-rule='c 199:* rmw' --device-cgroup-rule='c 226:* rmw' torizon/arm64v8-debian-weston-vivante --developer weston-launch --tty=/dev/tty7 --user=torizon && docker run -e ACCEPT_FSL_EULA=1 --rm -it -p 5003:5003 --name=inference -v /dev/galcore:/dev/galcore -v /run/udev/:/run/udev/ -v /sys:/sys -v /dev:/dev -v /tmp:/tmp --network host --privileged denisyuji/demo-inference"
