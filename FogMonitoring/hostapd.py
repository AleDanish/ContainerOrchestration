#     Author: Alessandro Zanni
#     <alessandro.zanni3@unibo.it>

import subprocess
import threading
import time

HOSTAPD_TIMEFRAME = 10

class myThread_Hostapd(threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
    def get_devices(self):
        devices = []
        cmd = "hostapd_cli all_sta"
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        for line in iter(proc.stdout.readline,''):
            line = line.decode("utf-8").replace("\n","")
            if line != "":
                devices.append(line)
            else:
                return devices
    def run(self):
        while True:
            devices = self.get_devices()
            
            # se device nouvo...contatta il cloud
            
            time.sleep(HOSTAPD_TIMEFRAME)