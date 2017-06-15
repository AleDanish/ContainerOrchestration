#     Author: Alessandro Zanni
#     <alessandro.zanni3@unibo.it>

import psutil
import time

while True:
    """ Return physical cpu usage """
    _cpu=psutil.cpu_percent()
    
    """ Return physical memory usage """
    _mem= psutil.virtual_memory()
    
    """ Return physical disk usage """
    _disk=psutil.disk_usage("/")
    print('CPU (' + str(_cpu) + '%) - MEM (' + str(_mem.percent) + '%) - DISK (' + str(_disk.percent) + '%)')
    time.sleep(10)