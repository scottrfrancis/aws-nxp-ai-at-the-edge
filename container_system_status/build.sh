#!/bin/bash

DOCKER_COMPOSE_DIR=./docker_compose
cd $DOCKER_COMPOSE_DIR

BUILD_TYPE=("prod" "dev/next")

PS3="Select a build type: "
select opt in "${BUILD_TYPE[@]}"
do
    if [[ " ${BUILD_TYPE[@]} " =~ " ${opt} " ]]; then
        if [[ "${opt}" == "prod" ]]; then
            for fname in $(ls docker-compose*.build.yml)
            do
                # Build for all arch
                docker-compose -f $fname build
                # Push for all arch
                docker-compose -f $fname push
            done
        elif [[ "${opt}" == "dev/next" ]]; then
            for fname in $(ls docker-compose*.build-next.yml)
            do
                # Build for all arch
                docker-compose -f $fname build
                # Push for all arch
                docker-compose -f $fname push
            done
        fi
        break
    else
        echo "Build type not supported"
    fi
done
