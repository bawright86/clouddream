# Dockerized Deepdream

All in one deepdream sandbox. This project aims to make it easy to experiment with deepdream
- Easy installation using docker containers, takes the pain away from setting up all the requirements. Currently only supports the CPU version.
- Easy to use web UI to add new pictures and queue processing with different parameters.

## Disclaimer

This project is not intended to be deployed in the wild as is, it is work in progress and I haven't spent much time on making it stable or secure.
Deploy at your own risk, preferably on a box with nothing valuable on.

By default nginx is configured with basic auth setup to control access to the server, you can turn it off by editing the nginx config file.

## Setup

### With Docker Compose

Make sure Docker compose is installed, see the [official installation instructions](https://docs.docker.com/compose/install/).

Use ```docker compose up``` to start all the containers.

Use ```docker compose scale compute=N``` to have N compute workers working in parallel.

### Without Docker compose

Just use the start.sh script, it will automatically pull the images needed and start the containers. Use stop.sh to stop the containers.

Make sure a docker is installed.
You need apache2-utils to generate the htpasswd file as well.

If you want to generate the images yourself

```
git clone git@github.com:hamstah/clouddream.git
cd clouddream/deepdream-compute
docker build -t hamstah/deepdream-compute .
cd ../deepdream-manager
docker build -t hamstah/deepdream-manager .
cd ../deepdream
htpasswd -c .htpasswd exampleuser
cd ..
./start.sh
```

## How does it work

### Containers

- redis has a redis server to manage the queue of processing jobs
- nginx serves the static files for the UI, proxies to gunicorn and serves the images
- compute contains a worker (rq) to process images from the redis queue
- manager is the python/Flask based manager displaying images, dealing with uploads and queuing jobs

### Docker images

- redis and nginx use the official Dockerfile
- compute is based on ubuntu and sets up all the environment needed for deepdream to work in
- manager is based on deepdream-compute with the added dependencies for flask, rq etc. The compute and manager containers are actually based on the manager image to make requirements management easier.


### Job parameters

When starting a job, you can pass a json configuration for the different parameters used by deepdream
- maxwidth is used to resize the image before processing, the smaller the quicker
- iter_n (default 10) - Number of iterations, the more you add the longer it takes and the weirder the output. default is 10
- octave_n (default 4) - Number of octaves
- octave_scale (default 1.4)
- end (default inception_4c/output) - see below
- clip (default True)

Possible values for `end` are as follows. They come from the
tmp.prototxt file which lists the layers of the GoogLeNet network used
in this demo. Note that the ReLU and Dropout layers are not valid for deepdreaming.

```
"conv1/7x7_s2"
"pool1/3x3_s2"
"pool1/norm1"
"conv2/3x3_reduce"
"conv2/3x3"
"conv2/norm2"
"pool2/3x3_s2"
"pool2/3x3_s2_pool2/3x3_s2_0_split_0"
"pool2/3x3_s2_pool2/3x3_s2_0_split_1"
"pool2/3x3_s2_pool2/3x3_s2_0_split_2"
"pool2/3x3_s2_pool2/3x3_s2_0_split_3"
"inception_3a/1x1"
"inception_3a/3x3_reduce"
"inception_3a/3x3"
"inception_3a/5x5_reduce"
"inception_3a/5x5"
"inception_3a/pool"
"inception_3a/pool_proj"
"inception_3a/output"
"inception_3a/output_inception_3a/output_0_split_0"
"inception_3a/output_inception_3a/output_0_split_1"
"inception_3a/output_inception_3a/output_0_split_2"
"inception_3a/output_inception_3a/output_0_split_3"
"inception_3b/1x1"
"inception_3b/3x3_reduce"
"inception_3b/3x3"
"inception_3b/5x5_reduce"
"inception_3b/5x5"
"inception_3b/pool"
"inception_3b/pool_proj"
"inception_3b/output"
"pool3/3x3_s2"
"pool3/3x3_s2_pool3/3x3_s2_0_split_0"
"pool3/3x3_s2_pool3/3x3_s2_0_split_1"
"pool3/3x3_s2_pool3/3x3_s2_0_split_2"
"pool3/3x3_s2_pool3/3x3_s2_0_split_3"
"inception_4a/1x1"
"inception_4a/3x3_reduce"
"inception_4a/3x3"
"inception_4a/5x5_reduce"
"inception_4a/5x5"
"inception_4a/pool"
"inception_4a/pool_proj"
"inception_4a/output"
"inception_4a/output_inception_4a/output_0_split_0"
"inception_4a/output_inception_4a/output_0_split_1"
"inception_4a/output_inception_4a/output_0_split_2"
"inception_4a/output_inception_4a/output_0_split_3"
"inception_4b/1x1"
"inception_4b/3x3_reduce"
"inception_4b/3x3"
"inception_4b/5x5_reduce"
"inception_4b/5x5"
"inception_4b/pool"
"inception_4b/pool_proj"
"inception_4b/output"
"inception_4b/output_inception_4b/output_0_split_0"
"inception_4b/output_inception_4b/output_0_split_1"
"inception_4b/output_inception_4b/output_0_split_2"
"inception_4b/output_inception_4b/output_0_split_3"
"inception_4c/1x1"
"inception_4c/3x3_reduce"
"inception_4c/3x3"
"inception_4c/5x5_reduce"
"inception_4c/5x5"
"inception_4c/pool"
"inception_4c/pool_proj"
"inception_4c/output"
"inception_4c/output_inception_4c/output_0_split_0"
"inception_4c/output_inception_4c/output_0_split_1"
"inception_4c/output_inception_4c/output_0_split_2"
"inception_4c/output_inception_4c/output_0_split_3"
"inception_4d/1x1"
"inception_4d/3x3_reduce"
"inception_4d/3x3"
"inception_4d/5x5_reduce"
"inception_4d/5x5"
"inception_4d/pool"
"inception_4d/pool_proj"
"inception_4d/output"
"inception_4d/output_inception_4d/output_0_split_0"
"inception_4d/output_inception_4d/output_0_split_1"
"inception_4d/output_inception_4d/output_0_split_2"
"inception_4d/output_inception_4d/output_0_split_3"
"inception_4e/1x1"
"inception_4e/3x3_reduce"
"inception_4e/3x3"
"inception_4e/5x5_reduce"
"inception_4e/5x5"
"inception_4e/pool"
"inception_4e/pool_proj"
"inception_4e/output"
"pool4/3x3_s2"
"pool4/3x3_s2_pool4/3x3_s2_0_split_0"
"pool4/3x3_s2_pool4/3x3_s2_0_split_1"
"pool4/3x3_s2_pool4/3x3_s2_0_split_2"
"pool4/3x3_s2_pool4/3x3_s2_0_split_3"
"inception_5a/1x1"
"inception_5a/3x3_reduce"
"inception_5a/3x3"
"inception_5a/5x5_reduce"
"inception_5a/5x5"
"inception_5a/pool"
"inception_5a/pool_proj"
"inception_5a/output"
"inception_5a/output_inception_5a/output_0_split_0"
"inception_5a/output_inception_5a/output_0_split_1"
"inception_5a/output_inception_5a/output_0_split_2"
"inception_5a/output_inception_5a/output_0_split_3"
"inception_5b/1x1"
"inception_5b/3x3_reduce"
"inception_5b/3x3"
"inception_5b/5x5_reduce"
"inception_5b/5x5"
"inception_5b/pool"
"inception_5b/pool_proj"
"inception_5b/output"
```

### Credits

Initially forked from [Vision.ai clouddream](https://github.com/VISIONAI/clouddream), almost entirelly rewritten since.

The included deepdream-compute/Dockerfile is an extended version of
https://github.com/taras-sereda/docker_ubuntu_caffe

Which is a modification from the original Caffe CPU master Dockerfile tleyden:
https://github.com/tleyden/docker/tree/master/caffe/cpu/master

The deepdream-manager uses a modified version of deepdream.py originally from Google
https://github.com/google/deepdream

### License

MIT License
