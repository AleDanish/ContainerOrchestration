import subprocess
#import Config
#import pylab as pl
#import Utils
from Utils import dec,deDec

coordinator = None

def get_swarm_node_list(status):
    node_list=[]
    cmd="docker node ls | grep " + status + " | awk '{print $2}'"
    #cmd="docker node ls | awk '{print $2}'"
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    for line in iter(proc.stdout.readline,''):
        line = line.decode("utf-8")
        if line == '' :
            break
        elif (line != '*\n'): #not consider this node (cloud-leader-manager) and the columns title
            node_list.append(line.rstrip())
    return node_list

""" Get list of labels given node hostaname/id"""
def get_node_labels(node):
    cmd = "docker node inspect --format '{{ .Spec.Labels }}' " + node
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    labels = {}
    for line in iter(proc.stdout.readline,''):
        line = line.decode("utf-8").replace("map[","").replace("]\n","")
        if line != "":
            for label in line.split(" "):
                element = label.split(":")
                labels[element[0]] = element[1]
        break
    return labels

def initialization_monitoring(coordinator, hostname_request, nodes):
    nodes[hostname_request]=1
    coordinator.setNodes(nodes)
    dat = [0,1] #v=0, w=1
    e = coordinator.init(dat,hostname_request)
    estimation = {'e' : float(e)}
    return estimation

def application_monitoring(coordinator, hostname_request, arguments, nodes):
    for node in get_node_labels(hostname_request):
        weigth = 1 #TODO
        nodes[node]=weigth
    coordinator.setNodes(nodes)
    v = dec(arguments["v"][0].decode("utf-8"))
    u = dec(arguments["u"][0].decode("utf-8"))
    dat = (v,u)
    e, s = coordinator.balance(dat, hostname_request)
    print("String: " + str(s) + " new e=" + str(e))
    estimation = {'e' : float(e)}
    return estimation