#!/bin/sh
docker run --name deepdream-redis -v `pwd`/deepdream:/data -d redis redis-server --appendonly yes
docker run --name deepdream-compute -m 1740M -v `pwd`/deepdream:/opt/deepdream -v `pwd`/deepdream-manager/manager:/opt/manager --link deepdream-redis -d hamstah/deepdream-manager /bin/bash -c "cd /opt/manager/manager && rqworker -c rq_settings compute"
docker run --name deepdream-manager -v `pwd`/deepdream-manager/manager:/opt/manager --volumes-from deepdream-compute --link deepdream-redis -d hamstah/deepdream-manager gunicorn manager:app --bind 0.0.0.0:8000 --reload --chdir /opt/manager
docker run --name deepdream-nginx -v `pwd`/deepdream/nginx.conf:/etc/nginx/nginx.conf --volumes-from deepdream-compute -d -p 80:80 --link deepdream-manager nginx
