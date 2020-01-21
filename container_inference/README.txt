** To build **

docker build -t <your-dockerhub-username>/pasta-demo-inference .

** To run **

docker run -e ACCEPT_FSL_EULA=1 --rm -d --name=inference -v /dev/galcore:/dev/galcore -v /dev:/dev -v /tmp:/tmp -v /run/udev/:/run/udev/ --network host --privileged <your-dockerhub-username>/pasta-demo-inference
