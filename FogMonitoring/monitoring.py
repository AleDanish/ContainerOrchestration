#     Author: Alessandro Zanni
#     <alessandro.zanni3@unibo.it>

import psutil

def monitoring_resource():
    while True:
        """ Return physical cpu usage """
        _cpu=psutil.cpu_percent()
        """ Return physical memory usage """
        _mem= psutil.virtual_memory()
        """ Return physical disk usage """
        _disk=psutil.disk_usage("/")
        return _cpu, _mem, _disk 