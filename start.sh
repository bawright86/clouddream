#!/bin/sh
#
# Start the docker container which will keep looking for images inside
# the inputs/ directory and spew out results into outputs/

docker run --name deepdream-compute -v `pwd`/deepdream:/opt/deepdream -d visionai/clouddream /bin/bash -c "cd /opt/deepdream && ./process_images.sh 2>&1 > log.html"
docker run --name deepdream-manager -v `pwd`/deepdream-manager/manager:/opt/manager --volumes-from deepdream-compute -d flask gunicorn manager:app --bind 0.0.0.0:8000 --reload --chdir /opt/manager
docker run --name deepdream-files -v `pwd`/deepdream/nginx.conf:/etc/nginx/nginx.conf --volumes-from deepdream-compute -d -p 80:80 --link deepdream-manager nginx