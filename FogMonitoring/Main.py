#     Author: Alessandro Zanni
#     <alessandro.zanni3@unibo.it>

import Hostapd
import Monitoring

#curl -d hostname=alessandro-VirtualBox2 -d mode=mobile_presence -d mac=arduino_mac1 http://192.168.56.101:8888
#curl -d hostname=alessandro-VirtualBox2 -d mode=scale_up http://192.168.56.101:8888
#curl -d hostname=alessandro-VirtualBox2 -d mode=scale_down http://192.168.56.101:8888

# Create threads
thread1 = Monitoring.myThread_Monitoring(1, "Thread-Monitoring", 1)
thread2 = Hostapd.myThread_Hostapd(2, "Thread-Hostapd", 2)
thread1.start()
#thread2.start()
