import time
import subprocess
from MQTTClient import MQTTClient

def run_container():
    cmd = "docker run -p 1883:1883 -p 9001:9001 toke/mosquitto"
    subprocess.Popen(cmd, shell=True)

startDeploy = time.time()
run_container()
endDeploy = time.time() 
timeDeploy = endDeploy - startDeploy
print("Total time to deploy the container is " + str(timeDeploy) + " s \n")

ip = "172.17.0.1"
client = MQTTClient(ip, "client1")
startup = False
while True:
    try:
        client.connect()
        break
    except:
        pass
timeStartup = time.time() - endDeploy

client.disconnect()
print("Total time to startup the container is " + str(timeStartup) + " s \n")
