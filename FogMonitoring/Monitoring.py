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

MONITORING_FILE = "dataset.txt"
MONITORING_TIMEFRAME = 2
MONITORING_TIMEFRAME_INIT = 1

hostname = socket.gethostname()

def formatResult(out):
    if out=='0':
        return int(out)
    else:
        value=int(out[:-1])
        unit=out[-1:]
        if unit=='B':
            value=value/1000
        elif unit=='M':
            value=value*1000
    return value

class myThread_Monitoring(threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
    def monitoring_resource(self):
        _cpu=psutil.cpu_percent() # Return physical cpu usage
        _mem= psutil.virtual_memory().percent # Return physical memory usage
        _disk=psutil.disk_usage("/").percent # Return physical disk usage
        return _cpu, _mem, _disk
    def write_file(self, _cpu, _mem, _disk):
        with open(MONITORING_FILE, "a+") as file:
            file.write(str(_cpu) + " " + str(_mem) + " " + str(_disk) + "\n")
    def initialization(self):
        for element in range(1,20):
            _cpu, _mem, _disk, _io = self.monitoring_resource()
            self.write_file(_cpu, _mem, _disk)
            print("CPU:" + str(_cpu) + " MEM:" + str(_mem) + " DISK:" + str(_disk) + " I/O:" + _io + "\n")
            time.sleep(MONITORING_TIMEFRAME_INIT)
    def run(self):
        self.initialization()
        
        node = Node(nid=uuid.uuid4(),threshold=Config.THRESHOLD, balancing="Classic")
        _cpu, _mem, _disk = self.monitoring_resource()
        node.run(_cpu/100)
        response = Messages.send(hostname, "init", node.v, node.u) #communication to cloud
        node.e = response["e"]
        node.vLast = node.v
        print("First estimation from coordinator - e:" + str(node.e))
        while True:
            _cpu, _mem, _disk = self.monitoring_resource()
            node.run(_cpu/100)
            print('--Node %s reporting u: %f'%(node.id,node.u))
            if node.monitoringFunction(node.u)>=node.threshold:
                response = Messages.send(hostname, "violation", node.v, node.u) #communication to cloud
                node.e = response["e"]
                node.vLast = node.v
                print("New estimation from coordinator - e:" + str(node.e))
            time.sleep(MONITORING_TIMEFRAME)
        
        while True:
            _cpu, _mem, _disk = self.monitoring_resource()
            self.write_file(_cpu, _mem, _disk)
            time.sleep(MONITORING_TIMEFRAME)
