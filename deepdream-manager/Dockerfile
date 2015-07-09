FROM ubuntu

RUN echo "deb http://archive.ubuntu.com/ubuntu/ $(lsb_release -sc) main universe" >> /etc/apt/sources.list

RUN apt-get update
RUN apt-get install -y python python-dev python-distribute python-pip 

ADD /manager/requirements.txt /manager/requirements.txt

#WORKDIR /manager
RUN pip install -r /manager/requirements.txt

# CMD gunicorn manager:app --bind 0.0.0.0:8000 --reload