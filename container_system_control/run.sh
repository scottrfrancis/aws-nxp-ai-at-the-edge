#!/bin/bash

DOCKER_COMPOSE_DIR=./docker_compose
ARCH=$(uname --m)

cd $DOCKER_COMPOSE_DIR
[[ "$1" == "-d" ]] && \
    docker-compose -f "docker-compose-$ARCH.yml" up -d || \
    docker-compose -f "docker-compose-$ARCH.yml" up