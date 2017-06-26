
sudo apt-get update

#install Docker
curl -sSL https://get.docker.com | sh
#sudo service docker stop
#sudo dockerd --storage-driver=overlay &

# set docker to run with sudo-priviledges
sudo groupadd dockerd
sudo gpasswd -a $USER docker
newgrp docker

sudo apt-get install python3
sudo apt-get install python3-pip
sudo pip3 install --user numpy scipy matplotlib ipython jupyter pandas sympy nose
sudo pip3 install tornado paho-mqtt