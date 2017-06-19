#     Author: Alessandro Zanni
#     <alessandro.zanni3@unibo.it>

import threading
import hostapd
import psutil
import time
#from EnvironmentMonitoring import EnvironmentMonitoring
#from MonitoringNode import MonitoringNode
from Node import Node
import uuid
import socket
import Messages

#curl -d hostname=alessandro-VirtualBox2 -d mode=mobile_presence -d mac=arduino_mac1 http://192.168.56.101:8888
#curl -d hostname=alessandro-VirtualBox2 -d mode=scale_up http://192.168.56.101:8888
#curl -d hostname=alessandro-VirtualBox2 -d mode=scale_down http://192.168.56.101:8888

MONITORING_FILE = "dataset.txt"
MONITORING_TIMEFRAME = 2
THRESHOLD = 0.1

hostname = socket.gethostname()

class myThread_Monitoring(threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
    def monitoring_resource(self):
        """ Return physical cpu usage """
        _cpu=psutil.cpu_percent()
        """ Return physical memory usage """
        _mem= psutil.virtual_memory().percent
        """ Return physical disk usage """
        _disk=psutil.disk_usage("/").percent
        print('CPU (' + str(_cpu) + '%) - MEM (' + str(_mem) + '%) - DISK (' + str(_disk) + '%)')
        return _cpu, _mem, _disk
    def write_file(self, _cpu, _mem, _disk):
        with open(MONITORING_FILE, "a+") as file:
            file.write("CPU:" + str(_cpu) + " MEM:" + str(_mem) + " DISK:" + str(_disk) + "\n")
    def run(self):
        node = Node(nid=uuid.uuid4(),threshold=THRESHOLD, balancing="Classic")
        response = Messages.send(hostname, "init") #communication to cloud
        node.e = response["e"]
        print("Estimation from coordinator - e:" + str(node.e))
        while True:
            _cpu, _mem, _disk = self.monitoring_resource()
            node.run(_cpu/100)
            print('--Node %s reporting u: %f'%(node.id,node.u))
            if node.monitoringFunction(node.u)>=node.threshold:
                response = Messages.send(hostname, "violation", node.v, node.u) #communication to cloud
                node.e = response["e"]
                print("New estimation from coordinator - e:" + str(node.e))
            time.sleep(MONITORING_TIMEFRAME)
        
        while True:
            _cpu, _mem, _disk = self.monitoring_resource()
            self.write_file(_cpu, _mem, _disk)
            time.sleep(MONITORING_TIMEFRAME)
            
# Create threads
thread1 = myThread_Monitoring(1, "Thread-Monitoring", 1)
thread2 = hostapd.myThread_Hostapd(2, "Thread-Hostapd", 2)
thread1.start()
#thread2.start()
