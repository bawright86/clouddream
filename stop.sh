#!/bin/sh
#
# Start the docker container which will keep looking for images inside
# the inputs/ directory and spew out results into outputs/

docker stop deepdream-nginx deepdream-compute deepdream-manager deepdream-redis
docker rm deepdream-nginx deepdream-compute deepdream-manager deepdream-redis
