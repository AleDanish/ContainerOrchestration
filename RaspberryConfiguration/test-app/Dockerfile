FROM resin/raspberrypi3-python

MAINTAINER Alessandro Zanni

ADD . /TestPy

RUN pip install pymongo
RUN pip install paho-mqtt

CMD [ "python", "TestPy/test.py" ]
