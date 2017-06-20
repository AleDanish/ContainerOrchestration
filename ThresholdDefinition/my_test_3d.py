import numpy as np
import scipy.optimize
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def our_function(coeff, data):
    A, B, C = coeff # parameters to optimize
    x, y, z = data.T # input data
    return A*x+B*y+C*z #least squared function (funzione dei minimi quadrati)

# ===============================================
# FORMULATION #2: a special least squares problem

# Here all that is needeed is a function that computes the vector of residuals
# the optimization function takes care of the rest
def least_squares_residuals(coeff, data, target):
    """
    Function that returns the vector of residuals between the predicted values
    and the target value. Here we want each predicted value to be close to zero
    """
    A, B, C = coeff
    x, y, z = data.T
    prediction = our_function(coeff, data)
    vector_of_residuals = (prediction - target)
    return vector_of_residuals

data = np.loadtxt('dataset.txt')
target = 0
num_coeff = 3
coeff_0 = np.ones(num_coeff)

# Here the bounds are specified in the optimization call
bound_gt = np.full(shape=num_coeff, fill_value=0, dtype=np.float)
bound_lt = np.full(shape=num_coeff, fill_value=np.inf, dtype=np.float)
bounds = (bound_gt, bound_lt)

lst_sqrs_result = scipy.optimize.least_squares(least_squares_residuals, coeff_0,
                                               args=(data, target), bounds=bounds)
# Test what the squared error of the returned result is
coeff = lst_sqrs_result.x
lst_sqrs_output = our_function(coeff, data)
print('====================')
print('lst_sqrs_result =\n%s' % (lst_sqrs_result,))
print('---------------------')
print('lst_sqrs_output = %r' % (lst_sqrs_output,))
print('====================')

# plot raw data
plt.figure()
ax = plt.subplot(111, projection='3d')
ax.scatter(data[:,(0)], data[:,(1)], data[:,(2)], color='b')


# plot plane
xlim = ax.get_xlim()
ylim = ax.get_ylim()
X,Y = np.meshgrid(np.arange(xlim[0], xlim[1]),
                  np.arange(ylim[0], ylim[1]))
Z = np.zeros(X.shape)
for r in range(X.shape[0]):
    for c in range(X.shape[1]):
        A = lst_sqrs_result.x[0]
        B = lst_sqrs_result.x[1]
        C = lst_sqrs_result.x[2]
        D = lst_sqrs_result.fun[r]
        Z = (A * X[r,c] + B * Y[r,c] -D) / (C)
ax.plot_wireframe(X,Y,Z, color='k')

ax.set_xlabel('x')
ax.set_ylabel('y')
ax.set_zlabel('z')
plt.show()