#     Author: Alessandro Zanni
#     <alessandro.zanni3@unibo.it>

import Hostapd
import Monitoring
import Config
import time
import Messages

#curl -d hostname=alessandro-VirtualBox2 -d mode=mobile_presence -d mac=arduino_mac1 http://192.168.56.101:8888
#curl -d hostname=alessandro-VirtualBox2 -d mode=scale_up http://192.168.56.101:8888
#curl -d hostname=alessandro-VirtualBox2 -d mode=scale_down http://192.168.56.101:8888

def create_file():
    open(Config.MONITORING_FILE, "w")
    
def write_file(_cpu, _mem, _disk):
    with open(Config.MONITORING_FILE, "a+") as file:
        file.write(str(_cpu) + " " + str(_mem) + " " + str(_disk) + "\n")
        
def creationDataset():
    _cpu, _mem, _disk = Monitoring.monitoring_resource()
    for index in range(1, Config.NUM_TRAINING_DATA):
        time.sleep(Config.MONITORING_TIMEFRAME_INIT)
        _cpu, _mem, _disk = Monitoring.monitoring_resource()
        write_file(_cpu, _mem, _disk)
        print(str(index) + ": CPU:" + str(_cpu) + " MEM:" + str(_mem) + " DISK:" + str(_disk))

'''
    initialization
'''
create_file()
creationDataset()
response = Messages.send("init", filename=Config.MONITORING_FILE) #communication to cloud
threshold = response["threshold"]
coeff = response["coeff"]
e = response["e"]
vLast = response["e"]
print("First estimation from coordinator - e:" + str(response["e"]))

# Create threads
print("Started threasds to monitor the node and to detect new Arduino connections")
thread1 = Monitoring.myThread_Monitoring(1, "Thread-Monitoring", threshold, coeff, e, vLast)
thread2 = Hostapd.myThread_Hostapd(2, "Thread-Hostapd")
#thread1.start()
thread2.start()
