# System Control #

This Docker image provides system control through a REST API:

- CB speed
- LED brightness

To build and run, docker-compose files and helper scripts are provided.

## Run ##

To run detached (as in -d):

`./run.sh -d`

To run attached (as in -it):

`./run.sh`

## Build ##

To build and push for all arch (x86, armv7 and armv8):

`./build.sh`