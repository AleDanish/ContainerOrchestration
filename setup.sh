# Script to configure a RaspberryPi from scratch
sudo apt-get update

#install java
sudo apt-get install python python3
sudo apt-get install python-pip
sudo pip install pymongo
sudo pip install paho-mqtt
sudo pip install tornado
sudo pip install docker

sudo apt-get update

#install Docker
curl -sSL https://get.docker.com | sh
#sudo service docker stop
#sudo dockerd --storage-driver=overlay &

# set docker to run with sudo-priviledges
sudo groupadd dockerd
sudo gpasswd -a $USER docker
newgrp docker

sudo apt-get update

#configure hotspot
sudo apt-get -y install hostapd dnsmasq

sudo apt-get update


