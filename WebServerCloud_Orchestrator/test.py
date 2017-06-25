import tornado.ioloop
import tornado.web
import deploy
import swarm_management

WEB_SERVER_PORT_FOG_NODES = 8888
THIS_IP = "192.168.56.101" 
MASTER_PORT = 2377
WEB_SERVER_PORT = 8888

APP_NAME = "app"
MODE = {'mobile_presence':'MOBILE_PRESENCE', 'scale_up':'SCALE_UP', 'scale_down':'SCALE_DOWN' }
DEVICE_HOSTNAME_MAP = {}

#curl -d hostname=alessandro-VirtualBox -d mode=mobile_presence -d mac= http://10.101.101.119:8888 #192.168.56.101

def application_management(mode, hostname_requesting, mac_new_device):
    if mode =="mobile_presence":
        hostname_receiver = hostname_requesting
        hostname_to_drain = DEVICE_HOSTNAME_MAP.get(mac_new_device, "")
        DEVICE_HOSTNAME_MAP[mac_new_device] = hostname_receiver

        label_key = hostname_receiver
        label_value = "true"
        swarm_management.add_label_to_node(hostname_receiver, label_key, label_value)
        print("Added Label " + label_key + ":" + label_value + " to hostname " + hostname_receiver)
        replicas_num = 1 #always 1
        deploy.edit_deploy_settings_replicas(replicas_num)
        deploy.edit_deploy_settings_node_labes(label_key, label_value)
        print(MODE[mode] + " mode - Docker compose settings file modified for the hostname " + hostname_receiver)
    elif mode == "scale_up":
        
        #
                
        hostname_list = swarm_management.get_swarm_node_list("Drain")
        hostname_receiver = ""
        for hostname in hostname_list:
            if hostname != hostname_requesting:
                hostname_receiver = hostname
                break
        
        #update the node into the cluster
        cluster_nodes = swarm_management.get_node_labels(hostname_requesting)
        label_key_receiver = hostname_receiver
        label_value_receiver = "true"
        swarm_management.add_label_to_node(hostname_receiver, label_key_receiver, label_value_receiver)
        print("Added receiver Label " + label_key_receiver + ":" + label_value_receiver + " to hostname " + hostname_receiver + " for future possible usage")
        for node in cluster_nodes:
            label_key_requesting = hostname_receiver
            label_value_requestig = "true"
            swarm_management.add_label_to_node(node, label_key_requesting, label_value_requestig)
            print("Added requesting Label " + label_key_requesting + ":" + label_value_requestig + " to hostname " + hostname_receiver + " to link the receiver node to the requesting hostname")
            label_key_receiver = node
            label_value_receiver = "true"
            swarm_management.add_label_to_node(hostname_receiver, label_key_receiver, label_value_receiver)
            print("Added receiver Label " + label_key_receiver + ":" + label_value_receiver + " to hostname " + hostname_receiver + " for future possible usage")
        
        replicas_num = deploy.get_replicas_number() + 1
        deploy.edit_deploy_settings_replicas(replicas_num)
        deploy.edit_deploy_settings_node_labes(hostname_requesting, "true") #hostname receiver or requesting is the same
        print(MODE[mode] + " mode - Docker compose settings file modified for the hostname " + hostname_receiver)
        hostname_to_drain = ""
    elif mode == "scale_down":
        
        #
        
        cluster_nodes = swarm_management.get_node_labels(hostname_requesting)
        cluster_nodes = [node for node in cluster_nodes if node != hostname_requesting]
        if len(cluster_nodes) <= 0:
            print(MODE[mode] + " mode - The requesting node cannot be removed because alone and not linked to other nodes")
        else:
            print(MODE[mode] + " mode - The requesting node can be removed because part of a cluster")
            swarm_management.delete_labels_from_node(hostname_requesting)
            print("Removed all the labels on the requesting hostname " + hostname_requesting)
            for node in cluster_nodes:
                swarm_management.remove_label_from_node(node, hostname_requesting)
            print("Removed Label about the requesting hostname " + hostname_requesting + " from all the node of the cluster")
            
            replicas_num = deploy.get_replicas_number() - 1
            deploy.edit_deploy_settings_replicas(replicas_num)
            hostname_receiver = cluster_nodes[0] # node of the cluster to re-deploy the service
            deploy.edit_deploy_settings_node_labes(hostname_receiver, "true")
            print(MODE[mode] + " mode - Docker compose settings file modified for the hostname " + hostname_receiver)
            hostname_to_drain = hostname_requesting

    """ Code for everyone"""
    if hostname_receiver is not "":
        swarm_management.set_availability_node(hostname_receiver, "active") #deploy on the new node -> call the new node to join the swarm
        print(MODE[mode] + " mode - Changed the node " + hostname_receiver + " availability to Active")
        print(MODE[mode] + " mode - Creating new services for the application " + APP_NAME)
        swarm_management.create_services(APP_NAME)
    else:
        print(MODE[mode] + " no available node can help: all node busy")
        
    if hostname_to_drain is not "":
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
