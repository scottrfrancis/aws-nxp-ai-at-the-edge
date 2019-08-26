#!/bin/bash

DOCKER_COMPOSE_DIR=./docker_compose
cd $DOCKER_COMPOSE_DIR

for fname in $(ls docker-compose*.build.yml)
do
    # Build for all arch
    docker-compose -f $fname build
    # Push for all arch
    docker-compose -f $fname push
done