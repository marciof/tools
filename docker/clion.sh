#!/bin/sh
mkdir -p ~/.clion-docker
cd "$(dirname "$0")"
xhost +
docker-compose -f clion/docker-compose.yml up -d
