#!/bin/sh
mkdir -p ~/.idea-docker
cd "$(dirname "$0")"
xhost +
docker-compose -f idea/docker-compose.yml up -d
