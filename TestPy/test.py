import DBManager
from MQTTClient import MQTTClient

ip="127.0.0.1"
port_mongo = "27017"
db = "testDB"
collection = "user"

client = MQTTClient(ip, "client1")
client.connect()
client.subscribe("test/data1")
client.publish("test/data1", "MESSAGE")
client.log()
client.disconnect()

#time.sleep(5)
#client.publish("test/data1", "MESSAGE")


#clientDB = DBManager.connect(ip, port_mongo)
#DBManager.initilize_collection(clientDB, db, collection)
#data = [{"_id" : 1, "foo" : "Hello"}, {"_id" : 2, "foo2" : "Bye"}]
#DBManager.insert_data(clientDB, db, collection, data)
#cursor = DBManager.read_document(clientDB, db, collection, {})
#for doc in cursor:
#    print(doc)
#DBManager.remove_document(clientDB, db, collection, "foo", "Hello")