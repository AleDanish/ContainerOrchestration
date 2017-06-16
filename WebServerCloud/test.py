import tornado.ioloop
import tornado.web
import deploy
import swarm_management

WEB_SERVER_PORT_FOG_NODES = "8888"
THIS_IP = "192.168.56.101" 
MASTER_PORT = "2377"
WEB_SERVER_PORT = 8888

APP_NAME = "app"
MODE = {'mobile_presence':'MOBILE_PRESENCE', 'scale_up':'SCALE_UP', 'scale_down':'SCALE_DOWN' }
DEVICE_HOSTNAME_MAP = {}

#curl -d hostname=alessandro-VirtualBox -d mode=mobile_presence -d mac= http://10.101.101.119:8888 #192.168.56.101

# get an hostname (!= from the node is requesting) from the available node into the swarm and deploy the same service on it
def application_management(mode, hostname_requesting, mac_new_device):
    if mode =="mobile_presence":
        hostname_receiver = hostname_requesting
        hostname_to_drain = DEVICE_HOSTNAME_MAP.get(mac_new_device, "")
        DEVICE_HOSTNAME_MAP[mac_new_device] = hostname_receiver

        replicas_num = 1 #always 1
        deploy.edit_deploy_settings_replicas(replicas_num)
        label_key = hostname_receiver
        label_value = "true"
        swarm_management.add_label_to_node(hostname_receiver, label_key, label_value)
        print("Added Label " + label_key + ":" + label_value + " to hostname " + hostname_receiver)
        deploy.edit_deploy_settings_node_labes(label_key, label_value)
        print(MODE[mode] + " mode - Docker compose settings file modified for the hostname " + hostname_receiver)
    elif mode == "scale_up":
        hostname_list = swarm_management.get_swarm_node_list("Drain")
        hostname_receiver = ""
        for hostname in hostname_list:
            if hostname != hostname_requesting:
                hostname_receiver = hostname
                break
        replicas_num = deploy.get_replicas_number()
        deploy.edit_deploy_settings_replicas(replicas_num + 1)
        
        label_key_requesting = hostname_requesting
        label_value_requestig = "true"
        swarm_management.add_label_to_node(hostname_receiver, label_key_requesting, label_value_requestig)
        print("Added requesting Label " + label_key_requesting + ":" + label_value_requestig + " to hostname " + hostname_receiver + " to link the receiver node to the requesting")
        
        label_key_receiver = hostname_receiver
        label_value_receiver = "true"
        swarm_management.add_label_to_node(hostname_receiver, label_key_receiver, label_value_receiver)
        print("Added receiver Label " + label_key_receiver + ":" + label_value_receiver + " to hostname " + hostname_receiver + " for future possible usage")
        deploy.edit_deploy_settings_node_labes(hostname_requesting, "true")
        print(MODE[mode] + " mode - Docker compose settings file modified for the hostname " + hostname_receiver)

    if hostname_receiver is not "":
        swarm_management.set_availability_node(hostname_receiver, "active") #deploy on the new node -> call the new node to join the swarm
        print(MODE[mode] + " mode - Changed the node " + hostname_receiver + " availability to Active")
        print(MODE[mode] + " mode - Creating new services for the application " + APP_NAME + " on the hostname " +  hostname_receiver + "...")
        swarm_management.create_services(APP_NAME)
    else:
        print(MODE[mode] + " no available node can help: all node busy")
        
    if (mode == "mobile_presence") and (hostname_to_drain is not ""):
        node_id_to_drain = swarm_management.id_from_hostname(hostname_to_drain)
        swarm_management.set_availability_node(node_id_to_drain, "drain") #swarm will create a new id for the host -> the id found is no longer used
        swarm_management.delete_labels_from_node(hostname_to_drain)
        print(MODE[mode] + " mode - Drain node with ip " + node_id_to_drain + " and cleared Labels")

def initialization_nodes():
    """ Setting all the worker nodes in the swarm as Drain """
    hostname_list = swarm_management.get_swarm_node_list("Ready")
    for hostname in hostname_list:
        node_id = swarm_management.id_from_hostname(hostname)
        swarm_management.set_availability_node(node_id, "drain")
        swarm_management.delete_labels_from_node(hostname)
        print("Hostname " + hostname + " set to Drain with empty Labels")
    
class MainHandler(tornado.web.RequestHandler):
    def post(self):
        arguments = self.request.arguments
        mode = arguments["mode"][0].decode("utf-8")
        hostname_request = arguments["hostname"][0].decode("utf-8")
        print("Arrived request from the hostname " + hostname_request + " with the mode " + mode)
        if mode == "mobile_presence":
            mac_new_device = arguments["mac"][0].decode("utf-8") #Arduino MAC address
        else:
            mac_new_device = None
        application_management(mode, hostname_request, mac_new_device)

    def get(self):
        print("Arrived request without arguments")
        
def make_app():
    return tornado.web.Application([(r"/", MainHandler),])

if __name__ == "__main__":
    initialization_nodes()
    app = make_app()
    app.listen(WEB_SERVER_PORT)
    print("WebServer listening on port " + str(WEB_SERVER_PORT))
    tornado.ioloop.IOLoop.current().start()
