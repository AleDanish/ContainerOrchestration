# Script to configure a RaspberryPi from scratch
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

sudo apt-get install python3
sudo apt-get install -y python3-pip
sudo pip3 install psutil tornado paho-mqtt

#configure hotspot
sudo apt-get -y install hostapd dnsmasq

sudo apt-get update

#change with unique hostname
sudo nano /etc/hosts
sudo nano /etc/hostname
sudo /etc/init.d/hostname.sh
sudo reboot

