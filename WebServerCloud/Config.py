THIS_IP = "192.168.56.101" 
MASTER_PORT = 2377
WEB_SERVER_PORT = 8888

APP_NAME = "app"
MODE = {'mobile_presence':'MOBILE_PRESENCE', 'scale_up':'SCALE_UP', 'scale_down':'SCALE_DOWN' }
DEVICE_HOSTNAME_MAP = {}

THRESHOLD_DEFAULT=10
#defMonFunc= lambda x: x**2
MONITORING_FUNCTION=lambda coeff,data:coeff[0]*data[0]+coeff[1]*data[1]+coeff[2]-data[2]#ax+by+c-z

MAP_HOSTNAME_IP = {'alessandro-VirtualBox2':'192.168.56.102','alessandro-VirtualBox3':'192.168.56.103'}
WEB_SERVER_FOG_PORT = 8888

MONITORING_FILE = "dataset.txt"
NUM_SAMPLE = 20