THRESHOLD_DEFAULT=10
#defMonFunc= lambda x: x**2
monitoringFunction=lambda coeff, data: coeff[0]*data[0]+coeff[1]*data[1]+coeff[2]*data[2]
balancing="Classic"