import tornado.ioloop
import tornado.web
import Monitoring
from Coordinator import Coordinator
import json
import Config

WEB_SERVER_PORT = 8889

MODE = {'init':'INITIALIZATION', 'scale_up':'SCALE UP', 'scale_down':'SCALE_DOWN' }

#curl -d hostname=alessandro-VirtualBox -d mode=mobile_presence -d mac= http://10.101.101.119:8888 #192.168.56.101

#NODES_WEIGTH_MAP = {'alessandro-VirtualBox2':1, 'alessandro-VirtualBox3':1}

nodes={}
coordinator=Coordinator(nodes={}, threshold=Config.THRESHOLD_DEFAULT)

def calcolo_pesi():
    print("calcolo pesi")

class MainHandler(tornado.web.RequestHandler):
    def post(self):
        arguments = self.request.arguments
        mode = arguments["mode"][0].decode("utf-8")
        hostname_request = arguments["hostname"][0].decode("utf-8")
        print(MODE[mode] + " from node " + hostname_request)
        if mode == "init":
            try:
                file = self.request.files['file'][0]['body'].decode("utf-8")
                coeff, estimation = Monitoring.initialization_monitoring(coordinator, hostname_request, nodes,file)
                response = {'e' : estimation.tolist(), 'threshold': Config.THRESHOLD_DEFAULT, 'coeff' : coeff.tolist()}
                print("Estimation vector: " + str(response['e']) + " - threshold: " + str(response['threshold']) + " - coeff: " + str(response['coeff']))
                self.write(json.dumps(response))
            except AttributeError:
                print(MODE[mode] + " Initialization request without dataset file") 
        elif mode == "scale_up":
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
