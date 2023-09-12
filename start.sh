#!/bin/bash

CONTAINER_NAME="tiktok-live-recorder"

# Check if the container already exists
if [[ $(docker ps -aq -f name=$CONTAINER_NAME) ]]; then
  # Stop the existing container
  docker stop $CONTAINER_NAME

  # Remove the existing container
  docker rm $CONTAINER_NAME
fi

docker build -t $CONTAINER_NAME .

mkdir -p ./mp4s
docker run -v ./mp4s:/home/myuser/mp4s -d --name $CONTAINER_NAME $CONTAINER_NAME
