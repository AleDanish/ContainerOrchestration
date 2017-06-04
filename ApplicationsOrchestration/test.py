import tornado.ioloop
import tornado.web
import deploy

WEB_SERVER_PORT = 8888
#hostname_list = ["raspberry1", "raspberry2"]
#hostname_list = ["alessandro-VirtualBox2", "alessandro-VirtualBox3"]

#curl -d hostname=alessandro-VirtualBox http://10.101.101.119:8888

class MainHandler(tornado.web.RequestHandler):
    def post(self):
        arguments = self.request.arguments
        hostname_request = arguments["hostname"]
        hostname_list = deploy.get_swarm_node_list()
        for hostname in hostname_list:
            if hostname != hostname_request:
                hostname_receiver = hostname
                break
        deploy.edit_deploy_settings(hostname_receiver)

def make_app():
    return tornado.web.Application([(r"/", MainHandler),])

if __name__ == "__main__":
    app = make_app()
    app.listen(WEB_SERVER_PORT)
    print("WebServer listening on port " + str(WEB_SERVER_PORT))
    tornado.ioloop.IOLoop.current().start()