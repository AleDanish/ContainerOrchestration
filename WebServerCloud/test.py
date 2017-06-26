import tornado.web
import Monitoring
from Coordinator import Coordinator
import json
import Config
import Swarm_Management
import Deploy
import subprocess
import ast
import numpy as np
import MQTTClient

#curl -d hostname=alessandro-VirtualBox -d mode=mobile_presence -d mac= http://10.101.101.119:8888 #192.168.56.101

#NODES_WEIGTH_MAP = {'alessandro-VirtualBox2':1, 'alessandro-VirtualBox3':1}
nodes={}
coordinator=Coordinator(threshold=Config.THRESHOLD_DEFAULT)

def send_message_write_file(ip_hostname_receiver):
    cmd="curl http://" + ip_hostname_receiver + ":" + str(Config.WEB_SERVER_FOG_PORT)
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    file = open(Config.MONITORING_FILE, "w")
    for line in iter(proc.stdout.readline,''):
        line = line.decode("utf-8")
        if line == '' :
            file.close()
            break
        else:
            file.write(line)

def send_message(mode, ip_hostname_receiver):
    cmd="curl http://" + ip_hostname_receiver + ":" + str(Config.WEB_SERVER_FOG_PORT) + " -F mode=" + mode
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    for line in iter(proc.stdout.readline,''):
        line = line.decode("utf-8")
        if line == '' :
            break
        else:
            return ast.literal_eval(line)

def send_message_noresp(mode, ip_hostname_receiver, value0, value1, value2):
    cmd="curl http://" + ip_hostname_receiver + ":" + str(Config.WEB_SERVER_FOG_PORT) + " -F mode=" + mode + " -F value0=" + str(value0) + " -F value1=" + str(value1) + " -F value2=" + str(value2)
    subprocess.Popen(cmd, shell=True)

def initialization_nodes():
    """ Setting all the worker nodes in the swarm as Drain """
    hostname_list = Swarm_Management.get_swarm_node_list("Ready")
    for hostname in hostname_list:
        node_id = Swarm_Management.id_from_hostname(hostname)
        Swarm_Management.set_availability_node(node_id, "drain")
        Swarm_Management.delete_labels_from_node(hostname)
        print("Hostname " + hostname + " set to Drain with empty Labels")

class MainHandler(tornado.web.RequestHandler):
    def post(self):
        arguments = self.request.arguments
        mode = arguments["mode"][0].decode("utf-8")
        hostname_request = arguments["hostname"][0].decode("utf-8")
        print("Arrived request from the hostname " + hostname_request + " with the mode " + mode)
        if mode =="init":
            try:
                file_monitoring_setup= self.request.files['file'][0]['body'].decode("utf-8")
                coeff, estimation = Monitoring.initialization_monitoring(coordinator, file_monitoring_setup)
                response = {'e' : estimation.tolist(), 'threshold': Config.THRESHOLD_DEFAULT, 'coeff' : coeff.tolist()}
                print("Estimation vector: " + str(response['e']) + " - threshold: " + str(response['threshold']) + " - coeff: " + str(response['coeff']))
                self.write(json.dumps(response))
            except AttributeError:
                print(Config.MODE[mode] + " Initialization request without dataset file")
        elif mode == "mobile_presence":
            mac_new_device = arguments["mac"][0].decode("utf-8") #Arduino MAC address
            Deploy.new_node(hostname_request, mac_new_device, mode)
            
        elif mode == "scale_up":
            v0 = float(arguments["v0"][0].decode("utf-8"))
            v1 = float(arguments["v1"][0].decode("utf-8"))
            v2 = float(arguments["v2"][0].decode("utf-8"))
            u0 = float(arguments["u0"][0].decode("utf-8"))
            u1 = float(arguments["u1"][0].decode("utf-8"))
            u2 = float(arguments["u2"][0].decode("utf-8"))
            coeff0 = float(arguments["coeff0"][0].decode("utf-8"))
            coeff1 = float(arguments["coeff1"][0].decode("utf-8"))
            coeff2 = float(arguments["coeff2"][0].decode("utf-8"))
            V=[v0,v1,v2]
            U=[u0,u1,u2]
            coeff=[coeff0, coeff1, coeff2]
            coordinator.coeff = coeff

            # create the balancing set and the nodes list 
            nodes={}
            coordinator.balancingSet = []
            message = "global_violation"
            new_node = True
            while message == "global_violation":
                drain_list = Swarm_Management.get_swarm_node_list("Drain")
                hostname_receiver = ""
                for hostname in drain_list:
                    if hostname != hostname_request:
                        hostname_receiver = hostname
                        break

                Deploy.scale_node(hostname_request, hostname_receiver, mode)

                #move arduino to another position
                try:
                    client = MQTTClient(Config.MQTT_IP, Config.MQTT_CLIENT_NAME)
                    client.connect()
                    client.publish(Config.MQTT_TOPIC, Config.MQTT_MESSAGE)
                    client.disconnect()
                except:
                    print("Error to connect to MQTT broker")

                new_node = False
                for label in Swarm_Management.get_node_labels(hostname_request):
                    if label == hostname_request:
                        weigth = 1
                        nodes[label]=weigth
                        coordinator.balancingSet.append([hostname_request, V, U])
                    else:
                        try:
                            nodes[label] #if new catch exception
                        except KeyError:
                            new_node = True
                            weigth = 1
                            nodes[label]=weigth
                            ip_hostname = Config.MAP_HOSTNAME_IP[label]
                            response = send_message("info", ip_hostname)
                            V_node = response["v"]
                            U_node = response["u"]
                            coordinator.balancingSet.append([label, V_node, U_node])
                
                if  new_node == False: # no node available for the balancing process
                    break

                value, message = Monitoring.application_monitoring(coordinator, hostname_request, nodes)
                
            for element in value:
                if element[0] == hostname_request:
                    if message == "violation":
                        value = {'e' : element[1].tolist()}
                    elif message == "balanced":
                        value = {'delta' : element[1].tolist()}
                    self.write(json.dumps(value))
                else:
                    ip_receiver = Config.MAP_HOSTNAME_IP[element[0]]
                    send_message_noresp(message, ip_receiver, element[1][0], element[1][1], element[1][2])

        elif mode == "scale_down":
            print("Scale down")
            v0 = float(arguments["v0"][0].decode("utf-8"))
            v1 = float(arguments["v1"][0].decode("utf-8"))
            v2 = float(arguments["v2"][0].decode("utf-8"))
            u0 = float(arguments["u0"][0].decode("utf-8"))
            u1 = float(arguments["u1"][0].decode("utf-8"))
            u2 = float(arguments["u2"][0].decode("utf-8"))
            V=[v0,v1,v2]
            U=[u0,u1,u2]
            
            nodes={}
            balancingSet = []
            new_node = False
            for label in Swarm_Management.get_node_labels(hostname_request):
                if label != hostname_request:
                    new_node = True
                    weigth = 1
                    nodes[label]=weigth
                    ip_hostname = Config.MAP_HOSTNAME_IP[label]
                    response = send_message("info", ip_hostname)
                    V_node = response["v"]
                    U_node = response["u"]
                    balancingSet.append([label, V_node, U_node])

            Deploy.delete_node(hostname_request, mode)

            for element in balancingSet:
                if element[0] == hostname_request:
                    V = V_node
                else:
                    V = np.array(element[1])
                w=nodes[element[0]]
                sumW = w
                estimation = (w*V)/sumW
                ip_receiver = Config.MAP_HOSTNAME_IP[element[0]]
                send_message_noresp("violation", ip_receiver, estimation[0], estimation[1], estimation[2])

    def get(self):
        print("Arrived request without arguments")
        
def make_app():
    return tornado.web.Application([(r"/", MainHandler),])

if __name__ == "__main__":
    #initialization_nodes()
    app = make_app()
    app.listen(Config.WEB_SERVER_PORT)
    print("WebServer listening on port " + str(Config.WEB_SERVER_PORT))
    tornado.ioloop.IOLoop.current().start()
