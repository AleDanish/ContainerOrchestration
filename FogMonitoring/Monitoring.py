#     Author: Alessandro Zanni
#     <alessandro.zanni3@unibo.it>

import threading
import psutil
import time
from Node import Node
import uuid
import Messages
import Config

_disk=psutil.disk_usage("/").percent

def monitoring_resource():
    _cpu=psutil.cpu_percent() # Return physical cpu usage
    _mem= psutil.virtual_memory().percent # Return physical memory usage
    #_disk=psutil.disk_usage("/").percent # Return physical disk usage
    return _cpu, _mem, _disk

def create_file():
    open(Config.MONITORING_FILE, "w")
    
def write_file(_cpu, _mem, _disk):
    with open(Config.MONITORING_FILE, "a+") as file:
        file.write(str(_cpu) + " " + str(_mem) + " " + str(_disk) + "\n")
        
def creationDataset2():
    _cpu, _mem, _disk = monitoring_resource()
    for index in range(1, Config.NUM_TRAINING_DATA):
        time.sleep(Config.MONITORING_TIMEFRAME_INIT)
        _cpu, _mem, _disk = monitoring_resource()
        write_file(_cpu, _mem, _disk)
        print(str(index) + ": CPU:" + str(_cpu) + " MEM:" + str(_mem) + " DISK:" + str(_disk))

def creationDataset():
    _cpu, _mem, _disk = monitoring_resource()
    for index in range(1, Config.NUM_TRAINING_DATA):
        time.sleep(Config.MONITORING_TIMEFRAME_INIT)
        _cpu_new, _mem_new, _disk_new = monitoring_resource()
        write_file(_cpu_new, _mem, _disk)
        print(str(index) + ": CPU:" + str(_cpu_new) + " MEM:" + str(_mem) + " DISK:" + str(_disk_new))

class myThread_Monitoring(threading.Thread):
    node = Node(nid=uuid.uuid4())
    def __init__(self, threadID, name, threshold, coeff, e, vLast):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.node.threshold = threshold
        self.node.coeff = coeff
        self.node.e = e
        self.node.vLast = vLast
    def run(self):
        while True:
            _cpu, _mem, _disk = monitoring_resource()
            #_cpu = 70.0
            #_mem = 85.1
            #_disk = 66.3
            if Config.DELTA_SHARED != 0:
                self.node.delta = Config.DELTA_SHARED
                Config.DELTA_SHARED = 0
            elif Config.E_SHARED != 0:
                self.node.e = Config.E_SHARED
                Config.E_SHARED = 0
                self.node.delta = [0,0,0]
            self.node.run([_cpu, _mem, _disk])
            Config.U_SHARED = self.node.u
            Config.V_SHARED = self.node.v
            print("Node " + str(self.node.id) + " reporting u: " + str(self.node.u))
            functionValue = self.node.monitoringFunction(self.node.coeff, self.node.u)
            if functionValue > self.node.threshold:
                print("Found a local violation on the monitored resources - SCALE UP")
                response = Messages.send("scale_up", v=self.node.v, u=self.node.u, coeff=self.node.coeff) #communication to cloud
                try:    
                    self.node.e = response["e"]
                    self.node.delta = [0,0,0]
                    print("New estimation from coordinator - e:" + str(self.node.e))
                except KeyError:
                    self.node.delta = response['delta']
                    print("New estimation from coordinator - delta:" + str(self.node.delta))
                self.node.vLast = self.node.v
            elif functionValue < (-self.node.threshold):
                print("Found a local violation on the monitored resources - SCALE DOWN")
                print("Found a local violation on the monitored resources - SCALE UP")
                response = Messages.send("scale_down", v=self.node.v, u=self.node.u) #communication to cloud
                try:
                    self.node.e = response["e"]
                    self.node.delta = [0,0,0]
                    print("New estimation from coordinator - e:" + str(self.node.e))
                except KeyError:
                    self.node.delta = response['delta']
                    print("New estimation from coordinator - delta:" + str(self.node.delta))
                self.node.vLast = self.node.v
            time.sleep(Config.MONITORING_TIMEFRAME)
