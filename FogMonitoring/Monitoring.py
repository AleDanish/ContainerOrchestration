#     Author: Alessandro Zanni
#     <alessandro.zanni3@unibo.it>

import threading
import psutil
import time
from Node import Node
import uuid
import socket
import Messages
import Config
import numpy as np

hostname = socket.gethostname()

#def formatResult(out):
#    if out=='0':
#        return int(out)
#    else:
#        value=int(out[:-1])
#        unit=out[-1:]
#        if unit=='B':
#            value=value/1000
#        elif unit=='M':
#            value=value*1000
#    return value

class myThread_Monitoring(threading.Thread):
    node = Node(nid=uuid.uuid4(), balancing="Classic")
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
    def monitoring_resource(self):
        _cpu=psutil.cpu_percent() # Return physical cpu usage
        _mem= psutil.virtual_memory().percent # Return physical memory usage
        _disk=psutil.disk_usage("/").percent # Return physical disk usage
        return _cpu, _mem, _disk
    def create_file(self):
        open(Config.MONITORING_FILE, "w")
    def write_file(self, _cpu, _mem, _disk):
        with open(Config.MONITORING_FILE, "a+") as file:
            file.write(str(_cpu) + " " + str(_mem) + " " + str(_disk) + "\n")
    def creationDataset(self):
        _cpu, _mem, _disk = self.monitoring_resource()
        for index in range(1, Config.NUM_TRAINING_DATA):
            time.sleep(Config.MONITORING_TIMEFRAME_INIT)
            _cpu, _mem, _disk = self.monitoring_resource()
            self.write_file(_cpu, _mem, _disk)
            print(str(index) + ": CPU:" + str(_cpu) + " MEM:" + str(_mem) + " DISK:" + str(_disk))
    def initialization(self):
        #self.create_file()
        #self.creationDataset()
        response = Messages.send(hostname, "init", filename=Config.MONITORING_FILE) #communication to cloud
        self.node.threshold = response["threshold"]
        self.node.coeff = response["coeff"]
        self.node.e = response["e"]
        self.node.vLast = np.array(self.node.e)
        print("First estimation from coordinator - e:" + str(self.node.e))
    def run(self):
        self.initialization()
        while True:
            _cpu, _mem, _disk = self.monitoring_resource()
            _cpu = 80.0
            _mem = 65.1
            _disk = 66.0
            self.node.run(np.array([_cpu, _mem, _disk]))
            print("Node " + str(self.node.id) + " reporting u: " + str(self.node.u))
            functionValue = self.node.monitoringFunction(self.node.coeff, self.node.u)
            if functionValue > self.node.threshold:
                print("Found a local violation on the monitored resources - SCALE UP")
                response = Messages.send(hostname, "scale_up", self.node.v, self.node.u) #communication to cloud
                self.node.e = response["e"]
                self.node.vLast = self.node.v
                self.node.delta=0
                print("New estimation from coordinator - e:" + str(self.node.e))
            elif functionValue < -self.node.threshold:
                print("Found a local violation on the monitored resources - SCALE DOWN")
                #response = Messages.send(hostname, "scale_down", self.node.v, self.node.u) #communication to cloud
                #self.node.e = response["e"]
                #self.node.vLast = self.node.v #inutile?
                #print("New estimation from coordinator - e:" + str(self.node.e))
            time.sleep(Config.MONITORING_TIMEFRAME)
