import tornado.ioloop
import tornado.web
import deploy
import swarm_management

WEB_SERVER_PORT = 8888
APP_NAME = "app"
DEPLOYMENT_TYPE = "SCALABILITY"
#DEPLOYMENT_TYPE = "MOBILE_PRESENCE"

WEB_SERVER_PORT_FOG_NODES = "8888"
THIS_IP = "192.168.56.101" 
MASTER_PORT = "2377"

#curl -d hostname=alessandro-VirtualBox http://10.101.101.119:8888

# get an hostname (!= from the node is requesting) from the available node into the swarm and deploy the same service on it
def application_management(hostname_requesting):
    hostname_list = swarm_management.get_swarm_node_list("Drain")
    hostname_receiver = ""
    for hostname in hostname_list:
        if hostname != hostname_requesting:
            hostname_receiver = hostname
            break
    if hostname_receiver is not "":
        print(DEPLOYMENT_TYPE + " mode - Calling the node " + hostname_receiver + " to join the swarm ...")
        swarm_management.set_availability_node(hostname_receiver, "active") #deploy on the new node -> call the new node to join the swarm
        if DEPLOYMENT_TYPE == "SCALABILITY":
            print(DEPLOYMENT_TYPE + " mode - Creating new services for the application " + APP_NAME + " on the hostname " +  hostname_receiver + "...")
            swarm_management.create_services(APP_NAME)
        elif DEPLOYMENT_TYPE == "MOBILE_PRESENCE":
            print(DEPLOYMENT_TYPE + " mode - Modifying the docker compose settings file for deployment on " + hostname_receiver + "...")
            deploy.edit_deploy_settings_hostname(hostname_receiver)
            print(DEPLOYMENT_TYPE + " mode - Docker compose settings file modified for the hostname " + hostname_receiver)
            print(DEPLOYMENT_TYPE + " mode - Creating new services for the application " + APP_NAME + " on the hostname " +  hostname_receiver + "...")
            swarm_management.create_services(APP_NAME)
            node_id_requesting = swarm_management.id_from_hostname(hostname_requesting)
            swarm_management.set_availability_node(node_id_requesting, "drain") #swarm will create a new id for the host -> the id found is no longer used
            print(DEPLOYMENT_TYPE + " mode - Drain node with ip " + node_id_requesting)
        
def initial_deploy():
    hostname_list = swarm_management.get_swarm_node_list("Ready")
    hostname_receiver = hostname_list[0]
    deployment_mode = ""
    if DEPLOYMENT_TYPE == "SCALABILITY":
        deployment_mode = "global"
    elif DEPLOYMENT_TYPE == "MOBILE_PRESENCE":
        deployment_mode = "replicated"

    print(DEPLOYMENT_TYPE + " mode - Modifying the docker compose settings file for deployment on " + hostname_receiver + "...")
    deploy.edit_deploy_settings_mode(deployment_mode)
    print(DEPLOYMENT_TYPE + " mode - Docker compose settings file modified for the hostname " + hostname_receiver)
    print(DEPLOYMENT_TYPE + " mode - Creating new services for the application " + APP_NAME + " on the hostname " +  hostname_receiver + "...")
    swarm_management.create_services(APP_NAME)

class MainHandler(tornado.web.RequestHandler):
    def post(self):
        arguments = self.request.arguments
        hostname_request = arguments["hostname"][0]
        hostname_request = hostname_request.decode("utf-8")
        print("Arrived request from the hostname " + hostname_request)
        application_management(hostname_request)

    def get(self):
        print("Arrived request without arguments")
        application_management("")
        
def make_app():
    return tornado.web.Application([(r"/", MainHandler),])

if __name__ == "__main__":
    initial_deploy()
    app = make_app()
    app.listen(WEB_SERVER_PORT)
    print("WebServer listening on port " + str(WEB_SERVER_PORT))
    tornado.ioloop.IOLoop.current().start()
