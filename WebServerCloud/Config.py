
WEB_SERVER_PORT = 8888
APP_NAME = "app"
MODE = {'mobile_presence':'MOBILE_PRESENCE', 'scale_up':'SCALE_UP', 'scale_down':'SCALE_DOWN' }
DEVICE_HOSTNAME_MAP = {}


''' FOG NODES '''
WEB_SERVER_FOG_PORT = 8888
MONITORING_FILE = "dataset.txt"
NUM_SAMPLE = 20
THRESHOLD_DEFAULT=20
MAP_HOSTNAME_IP = {'alessandro-VirtualBox2':'192.168.56.102','alessandro-VirtualBox3':'192.168.56.103'}
MONITORING_FUNCTION=lambda coeff,data:coeff[0]*data[0]+coeff[1]*data[1]+coeff[2]-data[2]#ax+by+c-z


''' MQTT '''
MQTT_IP = "172.17.0.1"
MQTT_CLIENT_NAME = "coordinator"
MQTT_TOPIC = "orchestration/scale"
MQTT_MESSAGE = "move"
