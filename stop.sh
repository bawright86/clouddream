#!/bin/sh
docker stop deepdream-nginx deepdream-compute deepdream-manager deepdream-redis
docker rm deepdream-nginx deepdream-compute deepdream-manager deepdream-redis
