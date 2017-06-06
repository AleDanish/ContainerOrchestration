import tornado.ioloop
import tornado.web
import subprocess

WEB_SERVER_PORT = 8888

class MainHandler(tornado.web.RequestHandler):
    def post(self):
        arguments = self.request.arguments
        token = arguments["token"][0].decode("utf-8")
        ip_master = arguments["ip_master"][0].decode("utf-8")
        port_master = arguments["port_master"][0].decode("utf-8")
        print("Arrived request from the master with ip " + ip_master + ":" + port_master + " with token " + token)
        #remove node from swarm to update its status (after the rm --force from the master)
        cmd1 = "docker swarm leave"
        subprocess.Popen(cmd1, shell=True)
        #join the swarm
        cmd2 = "docker swarm join --token " + token + " " + ip_master + ":" + port_master
        subprocess.Popen(cmd2, shell=True)
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
