import tornado.ioloop
import tornado.web
import Monitoring
import pylab as pl
import Utils
from Utils import dec,deDec
from Coordinator import Coordinator

WEB_SERVER_PORT = 8889

MODE = {'init':'INITIALIZATION', 'violation':'VIOLATION' }

#curl -d hostname=alessandro-VirtualBox -d mode=mobile_presence -d mac= http://10.101.101.119:8888 #192.168.56.101

#NODES_WEIGTH_MAP = {'alessandro-VirtualBox2':1, 'alessandro-VirtualBox3':1}
THRESHOLD=0.1
defMonFunc= lambda x: x**2

nodes={}
coordinator=Coordinator(nodes={}, threshold=THRESHOLD, monitoringFunction=defMonFunc)

def calcolo_pesi():
    print("calcolo pesi")
    
class MainHandler(tornado.web.RequestHandler):
    def post(self):
        arguments = self.request.arguments
        mode = arguments["mode"][0].decode("utf-8")
        hostname_request = arguments["hostname"][0].decode("utf-8")
        print(MODE[mode] + " from node " + hostname_request)
        
        if mode == "init":
            #file = self.request.file?
            estimation = Monitoring.initialization_monitoring(coordinator, hostname_request, nodes)
        elif mode == "violation":
            estimation = Monitoring.application_monitoring(coordinator, hostname_request, arguments, nodes)
        self.write(estimation)

    def get(self):
        print("Arrived request without arguments")
        
def make_app():
    return tornado.web.Application([(r"/", MainHandler),])

if __name__ == "__main__":
    app = make_app()
    app.listen(WEB_SERVER_PORT)
    print("WebServer listening on port " + str(WEB_SERVER_PORT))
    tornado.ioloop.IOLoop.current().start()
