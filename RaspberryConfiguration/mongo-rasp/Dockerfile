#FROM resin/armv7hf-debian:jessie
FROM alez/raspberry3-qemu

MAINTAINER Alessandro Zanni

# Install MongoDB.
RUN apt-get update && \
    apt-get install -y mongodb-server

RUN mkdir -p /data/db

EXPOSE 27017

ENTRYPOINT usr/bin/mongod
