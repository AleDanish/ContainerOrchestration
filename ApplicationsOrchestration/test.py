import fileinput
import tornado.ioloop
import tornado.web

WEB_SERVER_PORT = 8888
#hostname_list = ["raspberry1", "raspberry2"]
hostname_list = ["alessandro-VirtualBox2", "alessandro-VirtualBox3"]
docker_compose_file = "docker-compose.yml"

#curl -d hostname=alessandro-VirtualBox http://10.101.101.119:8888

def edit_deploy_settings(hostname):
    for line in fileinput.input(docker_compose_file, inplace=True):
        line = line.replace("\n","")
        if "node.hostname" in line:
            print(line.split("==")[0] + "==" + hostname)
        else:
            print(line)

class MainHandler(tornado.web.RequestHandler):
    def post(self):
        arguments = self.request.arguments
        
        hostname_request = arguments["hostname"]
        
        for hostname in hostname_list:
            if hostname != hostname_request:
                hostname_receiver = hostname
                break
        edit_deploy_settings(hostname_receiver)
        
    def get(self):
        hostname_request = self.request
        for hostname in hostname_list:
            if hostname != hostname_request:
                hostname_receiver = hostname
                break
        edit_deploy_settings(hostname_receiver) 


def make_app():
    return tornado.web.Application([(r"/", MainHandler),])

if __name__ == "__main__":
    app = make_app()
    app.listen(WEB_SERVER_PORT)
    print("WebServer listening on port " + str(WEB_SERVER_PORT))
    tornado.ioloop.IOLoop.current().start()