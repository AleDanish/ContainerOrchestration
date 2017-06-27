
''' HOSTAPD THREAD '''
HOSTAPD_TIMEFRAME = 5
WEB_SERVER_PORT="8888"
WEB_SERVER_IP="192.168.56.101"


''' MONITORING THREAD '''
monitoringFunction=lambda coeff, data: coeff[0]*data[0]+coeff[1]*data[1]+coeff[2]-data[2]#ax+by+c-z
MONITORING_FILE = "dataset.txt"
MONITORING_TIMEFRAME = 2
MONITORING_TIMEFRAME_INIT = 0.5
NUM_TRAINING_DATA = 21


U_SHARED = 0
V_SHARED = 0
E_SHARED = 0
DELTA_SHARED = 0

''' MQTT '''
MQTT_IP = "172.17.0.1"
MQTT_CLIENT_NAME = "coordinator"
MQTT_TOPIC = "orchestration/scale"
MQTT_MESSAGE = "move"
