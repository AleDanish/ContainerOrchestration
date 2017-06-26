FROM python:3

MAINTAINER Alessandro Zanni

ADD . /TestPy

RUN pip3 install pymongo
RUN pip3 install paho-mqtt

CMD [ "python3", "TestPy/test.py" ]
