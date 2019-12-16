*To build the image:
docker build -t torizonextras/pasta-demo-inference .

*To run:
docker run --rm -d --name=inference -v /sys:/sys -v /dev:/dev -v /tmp:/tmp --network host --privileged torizonextras/pasta-demo-inference
