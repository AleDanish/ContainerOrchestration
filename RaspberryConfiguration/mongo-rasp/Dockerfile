FROM resin/armv7hf-debian:jessie

MAINTAINER Alessandro Zanni

# Install MongoDB.
RUN apt-get update && \
    apt-get install -y mongodb
  
# Define mountable directories.
VOLUME ["/data/db"]

# Define working directory.
WORKDIR /data

# Expose ports.
#   - 27017: process
#   - 28017: http
EXPOSE 27017
EXPOSE 28017

# Define default command.
CMD ["mongod"]
