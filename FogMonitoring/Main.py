#     Author: Alessandro Zanni
#     <alessandro.zanni3@unibo.it>

import Hostapd
import Monitoring
import Config
import Messages
import tornado.web
import json

#curl -d hostname=alessandro-VirtualBox2 -d mode=mobile_presence -d mac=arduino_mac1 http://192.168.56.101:8888
#curl -d hostname=alessandro-VirtualBox2 -d mode=scale_up http://192.168.56.101:8888
#curl -d hostname=alessandro-VirtualBox2 -d mode=scale_down http://192.168.56.101:8888

def initialization():
    Monitoring.create_file()
    Monitoring.creationDataset()
    response = Messages.send("init", filename=Config.MONITORING_FILE) #communication to cloud
    threshold = response["threshold"]
    coeff = response["coeff"]
    e = response["e"]
    vLast = response["e"]
    print("First estimation from coordinator - e:" + str(response["e"]))
    
    # Create threads
    print("Started threads to monitor the node and to detect new Arduino connections")
    thread1 = Monitoring.myThread_Monitoring(1, "Thread-Monitoring", threshold, coeff, e, vLast)
    thread2 = Hostapd.myThread_Hostapd(2, "Thread-Hostapd")
    thread1.start()
    #thread2.start()

class MainHandler(tornado.web.RequestHandler):
    def post(self):
        arguments = self.request.arguments
        mode = arguments["mode"][0].decode("utf-8")
        if mode == "info":
            #file = open(Config.MONITORING_FILE, 'r').read()
            #self.write(file)
            values = {'u':Config.U_SHARED, 'v':Config.V_SHARED}
            self.write(json.dumps(values))
        elif mode == "balanced":
            delta0 = arguments["value0"][0].decode("utf-8")
            delta1 = arguments["value1"][0].decode("utf-8")
            delta2 = arguments["value2"][0].decode("utf-8")
            Config.DELTA_SHARED = [float(delta0), float(delta1), float(delta2)]
        elif mode == "violation":
            e0 = arguments["value0"][0].decode("utf-8")
            e1 = arguments["value1"][0].decode("utf-8")
            e2 = arguments["value2"][0].decode("utf-8")
            Config.E_SHARED = [float(e0), float(e1), float(e2)]
    
def make_app():
    return tornado.web.Application([(r"/", MainHandler),])

if __name__ == "__main__":
    initialization()
    app = make_app()
    app.listen(Config.WEB_SERVER_PORT)
    print("WebServer listening on port " + str(Config.WEB_SERVER_PORT))
    tornado.ioloop.IOLoop.current().start()
