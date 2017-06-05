import tornado.ioloop
import tornado.web
import subprocess

WEB_SERVER_PORT = 8888

class MainHandler(tornado.web.RequestHandler):
    def post(self):
        arguments = self.request.arguments
        token = arguments["token"][0].decode("utf-8")
        ip_master = arguments["ip_master"][0].decode("utf-8")
        ip_port = arguments["port_master"][0].decode("utf-8")
        print("Arrived request from the master with ip " + ip_master + ":" + ip_port + " with token " + token)
        subprocess.Popen("docker swarm join --token " + token + " " + ip_master + ":" + ip_master)
        print("Node added to the cluster")
        
    def get(self):
        print("Arrived request without arguments")

def make_app():
    return tornado.web.Application([(r"/", MainHandler),])

if __name__ == "__main__":
    app = make_app()
    app.listen(WEB_SERVER_PORT)
    print("WebServer listening on port " + str(WEB_SERVER_PORT))
    tornado.ioloop.IOLoop.current().start()