#     Author: Alessandro Zanni
#     <alessandro.zanni3@unibo.it>

import monitoring
import time
import threading
import subprocess

#curl -d hostname=alessandro-VirtualBox2 -d mode=mobile_presence -d mac=arduino_mac1 http://192.168.56.101:8888
#curl -d hostname=alessandro-VirtualBox2 -d mode=scale_up http://192.168.56.101:8888
#curl -d hostname=alessandro-VirtualBox2 -d mode=scale_down http://192.168.56.101:8888

MONITORING_TIMEFRAME = 10
HOSTAPD_TIMEFRAME = 10

class myThread_Monitoring(threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
    def run(self):
        while True:
            _cpu, _mem, _disk = monitoring.monitoring_resource()
            print('CPU (' + str(_cpu) + '%) - MEM (' + str(_mem.percent) + '%) - DISK (' + str(_disk.percent) + '%)')
            time.sleep(MONITORING_TIMEFRAME)

class myThread_Hostapd(threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
    def run(self):
        while True:
            cmd = "hostapd_cli all_sta"
            proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
            for line in iter(proc.stdout.readline,''):
                line = line.decode("utf-8").replace("\n","")
                break
            time.sleep(HOSTAPD_TIMEFRAME)


# Create threads
thread1 = myThread_Monitoring(1, "Thread-Monitoring")
thread2 = myThread_Hostapd(2, "Thread-Hostapd")
thread1.start()
#thread2.start()