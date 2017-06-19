#     Author: Alessandro Zanni
#     <alessandro.zanni3@unibo.it>

import psutil
import threading
import time

MONITORING_FILE = "dataset.txt"
MONITORING_TIMEFRAME = 10

class myThread_Monitoring(threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
    def monitoring_resource(self):
        while True:
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
        while True:
            _cpu, _mem, _disk = self.monitoring_resource()
            self.write_file(_cpu, _mem, _disk)
            time.sleep(MONITORING_TIMEFRAME)