import numpy as np
import scipy.optimize
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def our_function(coeff, data):
    A, B, C = coeff # parameters to optimize
    x, y, z = data.T # input data
    return A*x+B*y+C*z #least squared function (funzione dei minimi quadrati)

def general_objective(coeff, data, target):
    """
    General function that simply returns a value to be minimized.
    The coeff will be modified to minimize whatever the output of this function
    may be.
    """
    if np.any(coeff < 0):
        return np.inf
    prediction = our_function(coeff, data)
    losses = (prediction - target) ** 2
    loss = losses.sum()
    return loss

data = np.loadtxt('dataset.txt')
target = 0
num_coeff = 3
coeff_0 = np.ones(num_coeff)
general_result = scipy.optimize.minimize(general_objective, coeff_0,
                                         method='Nelder-Mead',
                                         args=(data, target))

coeff = general_result.x
general_output = our_function(coeff, data)
print('====================')
print('general_result =\n%s' % (general_result,))
print('---------------------')
print('general_output = %r' % (general_output,))
print('====================')
print("coeff: " + str(coeff[0])+ " " + str(coeff[1])+" " + str(coeff[2]))
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
        A_norm = general_result.final_simplex[1][0]
        B_norm = general_result.final_simplex[1][1]
        C_norm = general_result.final_simplex[1][2]
        D_norm = general_result.final_simplex[1][3]
        Z[r,c] = (A_norm * X[r,c] + B_norm * Y[r,c] - general_output[0])/ (-C_norm)
        #Z[r,c] = (coeff[0] * X[r,c] + coeff[1] * Y[r,c])
ax.plot_wireframe(X,Y,Z, color='k')

ax.set_xlabel('x')
ax.set_ylabel('y')
ax.set_zlabel('z')
plt.show()
