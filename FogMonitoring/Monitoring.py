#     Author: Alessandro Zanni
#     <alessandro.zanni3@unibo.it>

import threading
import psutil
import time
import Messages
import Config
import MQTTClient

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
    def __init__(self, threadID, name, threshold, coeff, e, vLast):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.threshold = threshold
        self.coeff = coeff
        self.e = e
        self.vLast = vLast
        self.delta = [0,0,0]
        self.v = 0
        self.u = 0
        self.weight = 1
    def calculate_u(self, vector):
        self.v=vector
        self.u=[(e_i+v_i-vLast_i)+(d_i/self.weight) for e_i,v_i,vLast_i,d_i in zip(self.e,self.v,self.vLast,self.delta)]
        self.vLast=self.v
    def run(self):
        while True:
            _cpu, _mem, _disk = monitoring_resource()
            #_cpu = 70.0
            #_mem = 85.1
            #_disk = 66.3
            if Config.DELTA_SHARED != 0:
                self.delta = Config.DELTA_SHARED
                Config.DELTA_SHARED = 0
            elif Config.E_SHARED != 0:
                self.e = Config.E_SHARED
                Config.E_SHARED = 0
                self.delta = [0,0,0]
            self.calculate_u([_cpu, _mem, _disk])
            Config.U_SHARED = self.u
            Config.V_SHARED = self.v
            print("Node with reporting u: " + str(self.u))
            functionValue = Config.monitoringFunction(self.coeff, self.u)
            if functionValue > self.threshold:
                print("Found a local violation on the monitored resources - SCALE UP")
                try:
                    #move arduino to another position
                    client = MQTTClient(Config.MQTT_IP, Config.MQTT_CLIENT_NAME)
                    client.connect()
                    client.publish(Config.MQTT_TOPIC, Config.MQTT_MESSAGE)
                    client.disconnect()
                except:
                    print("Error to connect to MQTT broker")
                response = Messages.send("scale_up", v=self.v, u=self.u, coeff=self.coeff) #communication to cloud
                try:
                    self.e = response["e"]
                    self.delta = [0,0,0]
                    print("New estimation from coordinator - e:" + str(self.e))
                except KeyError:
                    self.delta = response['delta']
                    print("New estimation from coordinator - delta:" + str(self.delta))
                self.vLast = self.v
            elif functionValue < (-self.threshold):
                print("Found a local violation on the monitored resources - SCALE DOWN")
                print("Found a local violation on the monitored resources - SCALE UP")
                Messages.send_noresp("scale_down", v=self.v, u=self.u) #communication to cloud
                self.vLast = self.v
            time.sleep(Config.MONITORING_TIMEFRAME)
