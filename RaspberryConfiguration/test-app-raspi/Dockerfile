#FROM resin/raspberrypi3-python
FROM alez/raspberry3-qemu

MAINTAINER Alessandro Zanni <alessandro.zanni3@unibo.it>

RUN [ "cross-build-start" ]

ADD . /TestPy

RUN apt-get update && apt-get install -y \
  python3.4 \
  python3-pip
RUN pip3 install pymongo
RUN pip3 install paho-mqtt

RUN [ "cross-build-end" ]

CMD [ "python3", "TestPy/test.py" ]
