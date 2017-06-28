import tornado.web
import Monitoring
import json
import Config
import Swarm_Management
import Deploy
import subprocess
import ast
import numpy as np

#curl -d hostname=alessandro-VirtualBox -d mode=mobile_presence -d mac= http://10.101.101.119:8888 #192.168.56.101

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

def update_balancingSet(hostname_receiver, nodes, balancingSet):
    weigth = 1
    nodes[hostname_receiver]=weigth
    ip_hostname = Config.MAP_HOSTNAME_IP[hostname_receiver]
    response = send_message("info", ip_hostname)
    V = response["v"]
    U = response["u"]
    balancingSet.append([hostname_receiver, V, U])
    return balancingSet

class MainHandler(tornado.web.RequestHandler):
    def post(self):
        arguments = self.request.arguments
        mode = arguments["mode"][0].decode("utf-8")
        hostname_request = arguments["hostname"][0].decode("utf-8")
        print("Arrived request from the hostname " + hostname_request + " with the mode " + mode)
        if mode =="init":
            try:
                file_monitoring_setup= self.request.files['file'][0]['body'].decode("utf-8")
                coeff, estimation = Monitoring.initialization_monitoring(file_monitoring_setup)
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
            V_node=[v0,v1,v2]
            U_node=[u0,u1,u2]
            coeff=[coeff0, coeff1, coeff2]

            deploy = False
            nodes={}
            balancingSet = []
            labels = Swarm_Management.get_node_labels(hostname_request)
            for label in labels:
                if label == hostname_request:
                    weigth = 1
                    nodes[label]=weigth
                    balancingSet.append([hostname_request, V_node, U_node])
                else:
                    balancingSet = update_balancingSet(label, nodes, balancingSet)
            if len(labels) == 1:
                print(str(len(nodes)) + " node -> global violation.")
                hostaname_receiver = Deploy.scale_node(hostname_request, mode)
                if hostaname_receiver == "":
                    deploy = False
                    print("No suitable node to extend the cluster")
                else:
                    print("Deployed containers on " + hostaname_receiver)
                    update_balancingSet(hostaname_receiver, nodes, balancingSet)
                    for i,V,U in balancingSet:  # @UnusedVariable
                        w=nodes[i]
                        sumW = w
                        e = Monitoring.estimation(V, w, sumW)
                        if i == hostname_request:
                            value = {'e' : e.tolist()}
                            self.write(json.dumps(value))
                        else:
                            ip_receiver = Config.MAP_HOSTNAME_IP[i]
                            send_message_noresp("violation", ip_receiver, e[0], e[1], e[2])
            elif len(labels) > 1:
                b = Monitoring.calculate_balance(balancingSet, nodes)
                valueMonitoring = Config.MONITORING_FUNCTION(coeff, b)
                print("Coord: balance vector is: " + "".join(str(x)+" " for x in b) + ", f(b)= %f, threshold is %f"%(valueMonitoring, Config.THRESHOLD_DEFAULT))
                if valueMonitoring < Config.THRESHOLD_DEFAULT:
                    print("Balancing successful")
                    message = "balanced"
                    value = Monitoring.calculate_delta(balancingSet, nodes, b)
                else:
                    print("Balancing failed")
                    hostaname_receiver = Deploy.scale_node(hostname_request, mode)
                    if hostaname_receiver == "":
                        deploy = False
                        print("No suitable node to extend the cluster")
                    else:
                        print("Deployed containers on " + hostaname_receiver)
                        update_balancingSet(hostaname_receiver, nodes, balancingSet)
                        message = "violation"
                        value = Monitoring.calculate_e(balancingSet, nodes, coeff)
                if deploy == True:
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
            V_node=[v0,v1,v2]
            U_node=[u0,u1,u2]

            nodes={}
            balancingSet = []
            labels = Swarm_Management.get_node_labels(hostname_request)
            if len(labels) <= 1:
                print("Cannot scale down. Only 1 node into the cluster")
            else:
                for label in labels:
                    if label != hostname_request:
                        balancingSet = update_balancingSet(label, nodes, balancingSet)

                Deploy.delete_node(hostname_request, mode)

                for element in balancingSet:
                    if element[0] == hostname_request:
                        V = V_node
                    else:
                        V = np.array(element[1])
                    w=nodes[element[0]]
                    sumW = w
                    estimation = Monitoring.estimation(V, w, sumW)
                    ip_receiver = Config.MAP_HOSTNAME_IP[element[0]]
                    send_message_noresp("violation", ip_receiver, estimation[0], estimation[1], estimation[2])

    def get(self):
        print("Arrived request without arguments")

def make_app():
    return tornado.web.Application([(r"/", MainHandler),])

if __name__ == "__main__":
    #yinitialization_nodes()
    app = make_app()
    app.listen(Config.WEB_SERVER_PORT)
    print("WebServer listening on port " + str(Config.WEB_SERVER_PORT))
    tornado.ioloop.IOLoop.current().start()
