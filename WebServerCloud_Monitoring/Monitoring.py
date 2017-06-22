import subprocess
from Utils import dec,deDec
import numpy as np
import scipy.optimize
from io import StringIO   # StringIO behaves like a file object

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

def our_function(coeff, data):
    A, B, C = coeff # parameters to optimize
    x, y, z = data.T # input data
    return A*x+B*y+C #least squared function

# FORMULATION: least squares problem
def least_squares_residuals(coeff, data, target):
    """ Function that returns the vector of residuals between the predicted values
        and the target value. Each predicted value should be close to zero """
    prediction = our_function(coeff, data)
    vector_of_residuals = (prediction - target)
    return vector_of_residuals

def calculateCoefficientFunction(file):
    data = np.loadtxt(StringIO(file))
    input_data = np.array([data[:,(0)], data[:,(1)],np.ones([20])]).T
    target = data[:,(2)]
    num_coeff = 3
    coeff_0 = np.ones(num_coeff)
    
    lst_sqrs_result = scipy.optimize.least_squares(least_squares_residuals, coeff_0, args=(input_data, target))
    # Test what the squared error of the returned result is
    coeff = lst_sqrs_result.x
    lst_sqrs_output = our_function(coeff, data)
    print("Calculated Coefficients: A="+str(coeff[0])+" B="+str(coeff[1])+" C="+str(coeff[2]))
    print('Function output: lst_sqrs_output = %r' % (lst_sqrs_output,))
    return coeff, data

def initialization_monitoring(coordinator, hostname_request, nodes,file):
    coeff, data = calculateCoefficientFunction(file)
    monitoringFunction=lambda coeff, data: coeff[0]*data[0]+coeff[1]*data[1]+coeff[2]*data[2]
    coordinator.setMonitoringFunction(monitoringFunction)
    nodes[hostname_request]=1
    coordinator.e = 0
    coordinator.setNodes(nodes)    
    x_mean = np.mean(data[:,(0)])
    y_mean = np.mean(data[:,(1)])
    z_mean = np.mean(data[:,(2)])
    V = np.array([x_mean, y_mean, z_mean])
    w = 1
    dat = [V,w] #v=0, w=1
    estimation = coordinator.init(dat,hostname_request)
    return coeff, estimation

def application_monitoring(coordinator, hostname_request, arguments, nodes):
    for node in get_node_labels(hostname_request):
        weigth = 1 #TODO
        nodes[node]=weigth
    coordinator.setNodes(nodes)
    V = dec(arguments["v"][0].decode("utf-8"))#array
    U = dec(arguments["u"][0].decode("utf-8"))#array
    dat = (V,U)
    e, s = coordinator.balance(dat, hostname_request)
    print("String: " + str(s) + " new e=" + str(e))
    estimation = {'e' : float(e)}
    return estimation