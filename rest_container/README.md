# System Information #

This Docker image provides system information through a REST API:

- CPU load percentage
- GPU memory usage percentage
- RAM usage percentage

To build and run, docker-compose files and helper scripts are provided.

## Run ##

To run detached (as in -d):

`./run.sh -d`

To run attached (as in -it):

`./run.sh`

## Build ##

To build and push for all arch (x86, armv7 and armv8):

`./build.sh`