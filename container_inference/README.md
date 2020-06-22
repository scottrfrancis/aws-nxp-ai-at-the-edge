# Container Image #

This Docker image provides the inference service for the AI at the Edge, Pasta Detection Demo with AWS.

The model folder contains a pre-trained model with pasta dataset.

For information about the training process for the new model, see [Train a Neural Network for Object Detection algorithm (SSD) for iMX8 boards using SageMaker Neo](https://developer.toradex.com/knowledge-base/train-ssd-for-imx8-boards)


## Running ##

A container based on this image starts automatically with the demo. See repository with the [local-ui systemd service file](https://github.com/toradex/meta-pasta-demo/blob/master/recipes-containers/local-ui/files/local-ui.service).

To stop the running local-ui service, in your board's teminal:
`systemctl stop local-ui`

To start again the local-ui service:
`systemctl start local-ui`

### Running manually (without systemd service) ###

To run the inference container manually, in your board's teminal :

`docker run -e ACCEPT_FSL_EULA=1 --rm -d -p 5003:5003 --name=inference -v /dev/galcore:/dev/galcore -v /run/udev/:/run/udev/ -v /sys:/sys -v /dev:/dev -v /tmp:/tmp --network host --privileged torizonextras/pasta-demo-inference`

Then run the local-ui container:

`docker run --rm -d --name local-ui -v /sys:/sys -v /dev:/dev -v /tmp:/tmp --network host --privileged torizonextras/pasta-demo-local-ui:latest-arm64v8`

## Stopping ##

To stop the inference container, in your board's terminal:

`docker stop inference`

To stop the local-ui container:

`docker stop local-ui`

## Building ##

**Attention: Don't forget to `docker login` in BOTH your board AND in your PC before starting to push and pull dockerhub images. Use your [Dockerhub](http://dockerhub.com) credentials**

To build this image, in your PC's terminal:

`docker build --cache-from torizonextras/pasta-demo-local-ui -t <your-dockerhub-username>/pasta-demo-inference .`

Use the `--cache-from torizonextras/pasta-demo-local-ui` flag to drastically improve the performance of the building. Remove this flag if you want to build with no cache (It can take several hours).

To push to your dockerhub account, in your PC's terminal:

`docker push <your-dockerhub-username>/pasta-demo-inference`

To pull your image, in **your board's terminal**:

`docker pull <your-dockerhub-username>/pasta-demo-inference`

To test your new image, don't forget to change the local-ui.service.Replace **torizonextras** by your dockerhub username in the `local-ui.service` file:

```
# sudo mount -o remount,rw /usr /usr
# sudo chmod 666 /usr/lib/systemd/system/local-ui.service
# vi /usr/lib/systemd/system/local-ui.service
```
