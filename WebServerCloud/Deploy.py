import fileinput
import Swarm_Management
import Config
import time

docker_compose_file = "docker-compose.yml"

def count_start_spaces(string):
    count = 0
    for i in string:
        if i == ' ':
            count += 1
        else:
            return count

def get_replicas_number():
    f = open(docker_compose_file, "r")
    for line in f.readlines():
        if "replicas:" in line:
            replicas_number = line.split("replicas:")[1].replace("\n","").strip()
            break
    f.close()
    return int(replicas_number)

def edit_deploy_settings_replicas(replicas_num):
    for line in fileinput.input(docker_compose_file, inplace=True):
        line = line.replace("\n","")
        if " replicas:" in line:
            print(line.split("replicas:")[0] + "replicas: " + str(replicas_num))
        else:
            print(line)
    fileinput.close()

def edit_deploy_settings_mode(mode):
    for line in fileinput.input(docker_compose_file, inplace=True):
        line = line.replace("\n","")
        if " mode:" in line:
            line.split("mode:")[0]
            print(line.split("mode:")[0] + "mode: " + mode)
        else:
            print(line)
    fileinput.close()

def edit_deploy_settings_node_labes(label_key, label_value):
    for line in fileinput.input(docker_compose_file, inplace=True):
        line = line.replace("\n","")
        if " constraints:" in line:
            print(line.split("[")[0] + "[node.labels." + label_key + "==" + label_value + "]")
        else:
            print(line)
    fileinput.close()

def new_node(hostname_request, mac_new_device, mode):
    hostname_to_drain = Config.DEVICE_HOSTNAME_MAP.get(mac_new_device, "")
    hostname_receiver = hostname_request
    Config.DEVICE_HOSTNAME_MAP[mac_new_device] = hostname_receiver

    label_key = hostname_receiver
    label_value = "true"
    Swarm_Management.add_label_to_node(hostname_receiver, label_key, label_value)
    print("Added Label " + label_key + ":" + label_value + " to hostname " + hostname_receiver)
    replicas_num = 1 #always 1
    edit_deploy_settings_replicas(replicas_num)
    edit_deploy_settings_node_labes(label_key, label_value)
    print("MOBILE PRESENCE mode - Docker compose settings file modified for the hostname " + hostname_receiver)

    if hostname_receiver is not "":
        Swarm_Management.set_availability_node(hostname_receiver, "active") #deploy on the new node -> call the new node to join the swarm
        print(Config.MODE[mode] + " mode - Changed the node " + hostname_receiver + " availability to Active")
        print(Config.MODE[mode] + " mode - Creating new services for the application " + Config.APP_NAME)
        startDeployContainers = time.time()
        Swarm_Management.create_services(Config.APP_NAME)
        timeDeployContainers = time.time() - startDeployContainers
        print("Containers deployed in " + str(timeDeployContainers) + " s")
    else:
        print(Config.MODE[mode] + " no available node can help: all node busy")
    drain_node(hostname_to_drain, mode)

def scale_node(hostname_requesting, mode):
    drain_list = Swarm_Management.get_swarm_node_list("Drain")
    hostname_receiver = ""
    for hostname in drain_list:
        if hostname != hostname_requesting:
            hostname_receiver = hostname
            break

    if hostname_receiver is not "":
        cluster_nodes = Swarm_Management.get_node_labels(hostname_requesting)
        label_key_receiver = hostname_receiver
        label_value_receiver = "true"
        Swarm_Management.add_label_to_node(hostname_receiver, label_key_receiver, label_value_receiver)
        print("Added receiver Label " + label_key_receiver + ":" + label_value_receiver + " to hostname " + hostname_receiver + " for future possible usage")
        for node in cluster_nodes:
            label_key_requesting = hostname_receiver
            label_value_requestig = "true"
            Swarm_Management.add_label_to_node(node, label_key_requesting, label_value_requestig)
            print("Added requesting Label " + label_key_requesting + ":" + label_value_requestig + " to hostname " + node + " to link the receiver node to the requesting hostname")
            label_key_receiver = node
            label_value_receiver = "true"
            Swarm_Management.add_label_to_node(hostname_receiver, label_key_receiver, label_value_receiver)
            print("Added receiver Label " + label_key_receiver + ":" + label_value_receiver + " to hostname " + hostname_receiver + " for future possible usage")

        replicas_num = len(cluster_nodes) + 1
        edit_deploy_settings_replicas(replicas_num)
        edit_deploy_settings_node_labes(hostname_requesting, "true") #hostname receiver or requesting is the same
        print("SCALE UP mode - Docker compose settings file modified for the hostname " + hostname_receiver)

        Swarm_Management.set_availability_node(hostname_receiver, "active") #deploy on the new node -> call the new node to join the swarm
        print(Config.MODE[mode] + " mode - Changed the node " + hostname_receiver + " availability to Active")
        print(Config.MODE[mode] + " mode - Creating new services for the application " + Config.APP_NAME)
        startDeployContainers = time.time()
        Swarm_Management.create_services(Config.APP_NAME)
        timeDeployContainers = time.time() - startDeployContainers
        print("Containers deployed in " + str(timeDeployContainers) + " s")
    else:
        print(Config.MODE[mode] + " no available node can help: all node busy")
    return hostname_receiver

def delete_node(hostname_requesting, mode):
    cluster_nodes = Swarm_Management.get_node_labels(hostname_requesting)
    cluster_nodes = [node for node in cluster_nodes if node != hostname_requesting]
    if len(cluster_nodes) <= 0:
        print("SCALE DOWN mode - The requesting node cannot be removed because alone and not linked to other nodes")
    else:
        print("SCALE DOWN mode - The requesting node can be removed because part of a cluster")
        Swarm_Management.delete_labels_from_node(hostname_requesting)
        print("Removed all the labels on the requesting hostname " + hostname_requesting)
        for node in cluster_nodes:
            Swarm_Management.remove_label_from_node(node, hostname_requesting)
        print("Removed Label about the requesting hostname " + hostname_requesting + " from all the node of the cluster")

        replicas_num = len(cluster_nodes)
        edit_deploy_settings_replicas(replicas_num)
        hostname_receiver = cluster_nodes[0] # node of the cluster to re-deploy the service
        edit_deploy_settings_node_labes(hostname_receiver, "true")
        print("SCALE DOWN mode - Docker compose settings file modified for the hostname " + hostname_receiver)

    if hostname_receiver is not "":
        Swarm_Management.set_availability_node(hostname_receiver, "active") #deploy on the new node -> call the new node to join the swarm
        print(Config.MODE[mode] + " mode - Changed the node " + hostname_receiver + " availability to Active")
        print(Config.MODE[mode] + " mode - Creating new services for the application " + Config.APP_NAME)
        Swarm_Management.create_services(Config.APP_NAME)
    else:
        print(Config.MODE[mode] + " no available node can help: all node busy")

    hostname_to_drain = hostname_requesting
    drain_node(hostname_to_drain, mode)

def drain_node(hostname_to_drain, mode):
    if hostname_to_drain is not "":
        node_id_to_drain = Swarm_Management.id_from_hostname(hostname_to_drain)
        Swarm_Management.set_availability_node(node_id_to_drain, "drain") #swarm will create a new id for the host -> the id found is no longer used
        Swarm_Management.delete_labels_from_node(hostname_to_drain)
        print(Config.MODE[mode] + " mode - Drain node with ip " + node_id_to_drain + " and cleared Labels")
