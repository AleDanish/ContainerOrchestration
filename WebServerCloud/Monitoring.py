import subprocess
import numpy as np
import scipy.optimize
from io import StringIO   # StringIO behaves like a file object
import Config

def hostname_from_id(id_node):
    cmd = "docker node ls | grep " + id_node + "| awk '{print $2}'"
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    for line in iter(proc.stdout.readline,''):
        return line.decode("utf-8").replace("\n","").strip()

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
    input_data = np.array([data[:,(0)], data[:,(1)],np.ones([Config.NUM_SAMPLE])]).T
    target = data[:,(2)]
    num_coeff = 3
    coeff_0 = np.ones(num_coeff)
    
    lst_sqrs_result = scipy.optimize.least_squares(least_squares_residuals, coeff_0, args=(input_data, target))
    coeff = lst_sqrs_result.x
    lst_sqrs_output = our_function(coeff, data)
    print("Calculated Coefficients: A="+str(coeff[0])+" B="+str(coeff[1])+" C="+str(coeff[2]))
    print('Function output: lst_sqrs_output = %r' % (lst_sqrs_output,))
    return coeff, data

def initialization_monitoring(coordinator, hostname_request, file):
    coeff, data = calculateCoefficientFunction(file)
    coordinator.setMonitoringFunction(Config.MONITORING_FUNCTION)
    coordinator.coeff=coeff
    #nodes[hostname_request]=1
    coordinator.e = 0
    #coordinator.setNodes(nodes)
    x_mean = np.mean(data[:,(0)])
    y_mean = np.mean(data[:,(1)])
    z_mean = np.mean(data[:,(2)])
    V = np.array([x_mean, y_mean, z_mean])
    w = 1
    dat = [V,w] #v=0, w=1
    sumW = 1
    estimation = coordinator.init_estimation(dat,hostname_request, sumW)
    return coeff, estimation

def application_monitoring(coordinator, hostname_request, nodes):
    coordinator.nodes = nodes
    #dat = (V_new_node, U_new_node)
    #e, s = coordinator.estimation(dat, hostname_request)
    value, s = coordinator.balance()
    print("String: " + str(s) + " value for the nodes=" + str(value))
    return value, s
