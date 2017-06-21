import DBManager
from MQTTClient import MQTTClient
import socket
import fcntl
import struct
import time

#def get_external_ip_address():
#    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#    s.connect(("8.8.8.8", 80))
#    return s.getsockname()[0]

def get_ip_address_from_interface(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(s.fileno(),0x8915,struct.pack('256s', ifname[:15]))[20:24])

#ip = get_ip_adress()
#ip=get_ip_address_from_interface("docker0")
ip = "172.17.0.1"
#ip="127.0.0.1"
port_mongo = "27017"
db = "test"
collection = "user"

TOPIC="/test/fogorchestration"
TIMEFRAME = 10
print("IP: " + ip)

client = MQTTClient(ip, "client1")
client.connect()
client.subscribe(TOPIC)
print("Subscribed to topic " + TOPIC)
print("MQTT broker listening on port 1883")
#client.publish("test/data1", "MESSAGE")
client.log()

count=0
while True:
    messages = client.messages
    if len(messages) > 0:
        client.messages = []
        clientDB = DBManager.connect(ip, port_mongo)
        DBManager.initilize_collection(clientDB, db, collection)
        info = {}
        data = []
        for message in messages:
            info['id'] = count
            info['information'] = message
            data.append(info)
            count+=1
        DBManager.insert_data(clientDB, db, collection, data)
        print("Inserted data into the db "+ db + " collection " + collection)
        
        cursor = DBManager.read_document(clientDB, db, collection, {})
        for doc in cursor:
            print("I'm reading from datatabase " + db + " collection " + collection)
            print(doc)
        
    time.sleep(TIMEFRAME)

#client.disconnect()
#print("Tested Mosquitto successfully")

#time.sleep(5)
#client.publish("test/data1", "MESSAGE")
#print("Testing MongoDB...")4

#DBManager.remove_document(clientDB, db, collection, "foo", "Hello")
#print("Tested MongoDB successfully")