#     Author: Alessandro Zanni
#     <alessandro.zanni3@unibo.it>

import subprocess
import threading
import time
import Config
import Messages

class myThread_Hostapd(threading.Thread):
    def __init__(self, threadID, name):
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
            #device_mac = self.get_devices()
            
            # se device nouvo...contatta il cloud
            Messages.send("mobile_presence", mac="mac_address2")
            
            time.sleep(Config.HOSTAPD_TIMEFRAME)