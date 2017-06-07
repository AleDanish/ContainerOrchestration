import DBManager
from MQTTClient import MQTTClient
import socket

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

#ip = get_ip_address()
ip="172.17.0.1"
port_mongo = "27017"
db = "testDB"
collection = "user"

print("IP: " + ip)

print("Testing Mosquitto...")
client = MQTTClient(ip, "client1")
client.connect()
client.subscribe("test/data1")
client.publish("test/data1", "MESSAGE")
client.log()
client.disconnect()
print("Tested Mosquitto successfully")

#time.sleep(5)
#client.publish("test/data1", "MESSAGE")

print("Testing MongoDB...")
clientDB = DBManager.connect(ip, port_mongo)
DBManager.initilize_collection(clientDB, db, collection)
data = [{"_id" : 1, "foo" : "Hello"}, {"_id" : 2, "foo2" : "Bye"}]
DBManager.insert_data(clientDB, db, collection, data)
cursor = DBManager.read_document(clientDB, db, collection, {})
for doc in cursor:
    print(doc)
DBManager.remove_document(clientDB, db, collection, "foo", "Hello")
print("Tested MongoDB successfully")