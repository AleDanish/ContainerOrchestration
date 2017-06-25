#     Author: Alessandro Zanni
#     <alessandro.zanni3@unibo.it>

import threading
import psutil
import time
from Node import Node
import uuid
import Messages
import Config

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

def monitoring_resource():
    _cpu=psutil.cpu_percent() # Return physical cpu usage
    _mem= psutil.virtual_memory().percent # Return physical memory usage
    #_disk=psutil.disk_usage("/").percent # Return physical disk usage
    _disk=45
    return _cpu, _mem, _disk

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
            _cpu = 80.0
            _mem = 75.1
            #_disk = 66.3
            if Config.DELTA_SHARED != 0:
                self.node.delta = Config.DELTA_SHARED
                Config.DELTA_SHARED = 0
            self.node.run([_cpu, _mem, _disk])
            Config.U_SHARED = self.node.u
            Config.V_SHARED = self.node.v
            print("Node " + str(self.node.id) + " reporting u: " + str(self.node.u))
            functionValue = self.node.monitoringFunction(self.node.coeff, self.node.u)
            if functionValue > 0: #self.node.threshold:
                print("Found a local violation on the monitored resources - SCALE UP")
                Messages.send_noresp("scale_up", self.node.v, self.node.u) #communication to cloud
                while (Config.DELTA_SHARED == 0) or (Config.E_SHARED == 0):
                    pass
                if Config.DELTA_SHARED != 0:
                    self.node.delta = Config.DELTA_SHARED
                    Config.DELTA_SHARED = 0
                elif Config.E_SHARED != 0:
                    self.node.e = Config.E_SHARED
                    Config.E_SHARED = 0
                self.node.vLast = self.node.v
                print("New estimation from coordinator - e:" + str(self.node.e))
            elif functionValue < (-self.node.threshold):
                print("Found a local violation on the monitored resources - SCALE DOWN")
                #response = Messages.send(hostname, "scale_down", self.node.v, self.node.u) #communication to cloud
                #self.node.e = response["e"]
                #self.node.vLast = self.node.v #inutile?
                #print("New estimation from coordinator - e:" + str(self.node.e))
            time.sleep(Config.MONITORING_TIMEFRAME)
