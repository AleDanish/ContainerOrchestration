import time
import subprocess
from MQTTClient import MQTTClient

def run_container():
    cmd = "docker run -p 1883:1883 -p 9001:9001 alez/mosquitto-raspi"
    subprocess.Popen(cmd, shell=True)

ip = "172.17.0.1"
client = MQTTClient(ip, "client1")
startDeploy = time.time()
run_container()

while True:
    try:
        client.connect()
        break
    except:
        pass
timeStartup = time.time() - startDeploy

client.disconnect()
print("Total time to create and startup the container is " + str(timeStartup) + " s \n")
