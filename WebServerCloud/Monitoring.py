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
    A, B, C = coeff
    x, y, z = data.T  # @UnusedVariable
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

def initialization_monitoring(file):
    coeff, data = calculateCoefficientFunction(file)
    x_mean = np.mean(data[:,(0)])
    y_mean = np.mean(data[:,(1)])
    z_mean = np.mean(data[:,(2)])
    V = np.array([x_mean, y_mean, z_mean])
    w = 1
    sumW = 1
    return coeff, estimation(V, w, sumW)

def estimation(V, w, sumW):
    V = np.array(V)
    e=(w*V)/sumW
    return e

def calculate_balance(balancingSet, nodes):
    sumU=[0,0,0]
    sumW=0
    for i,v,u in balancingSet:  # @UnusedVariable
        for index in range(0,3):
            sumU[index]+=u[index]*nodes[i]
        sumW+=nodes[i]
        disk = u[2]
    b = np.array(sumU)/sumW
    b[2] = disk
    print("balancing set is:" + str(balancingSet))
    return b

def calculate_delta(balancingSet, nodes, b):
    dDelta=[]
    for (i,v,u) in balancingSet:  # @UnusedVariable
        dDelta.append([i, nodes[i]*b-nodes[i]*u])
    print("Balance successful")
    print("dDelta:" + str(dDelta))
    return dDelta

def calculate_e(balancingSet, nodes, coeff):
    sumV=[0,0,0]
    sumU=[0,0,0]
    for i,V,U in balancingSet:
        for index in range(0,3):
            sumV[index]+=V[index]*nodes[i]
            sumU[index]+=U[index]*nodes[i]
    vGl = np.array(sumV)/sum(nodes[i] for i,v,u in balancingSet)  # @UnusedVariable
    uGl = np.array(sumU)/sum(nodes[i] for i,v,u in balancingSet)  # @UnusedVariable
    print("Coord: GLOBAL VIOLATION:v="  + str(vGl) + ",u=" + str(uGl) + " ,f(v)=%f"%(Config.MONITORING_FUNCTION(coeff, vGl)))

    e=vGl
    values=[]
    for (i,v,u) in balancingSet:  # @UnusedVariable
        values.append([i, e])

    return values, "violation"
