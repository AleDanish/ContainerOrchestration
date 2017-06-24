
monitoringFunction=lambda coeff, data: coeff[0]*data[0]+coeff[1]*data[1]+coeff[2]-data[2]#ax+by+c-z
balancing="Classic"
MONITORING_FILE = "dataset.txt"
MONITORING_TIMEFRAME = 2
MONITORING_TIMEFRAME_INIT = 0.5
NUM_TRAINING_DATA = 20
