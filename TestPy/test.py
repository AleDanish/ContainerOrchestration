import DBManager
from MQTTClient import MQTTClient

ip="127.0.0.1"
port_mongo = "27017"
db = "testDB"
collection = "user"

import re
import fileinput
docker_compose_file = "docker-compose.yml"

def count_start_spaces(string):
    count = 0
    for i in string:
        if i == ' ':
            count += 1
        else:
            return count

def edit_deploy_settings(hostname):
    host_number = re.search(r'\d+$', hostname).group(0)
    for line in fileinput.input(docker_compose_file, inplace=True):
        line = line.replace("\n","")
        if count_start_spaces(line) == 2:
            service_name = line.split(':')[0]
            service_number = re.search(r'\d+$', service_name)
            if service_number is not None:
                service_number = service_number.group(0)
                service_name = service_name[:-len(service_number)]
            print(service_name + host_number + ":")
        elif "node.hostname" in line:
            print(line.split("==")[0] + "==" + hostname)
        else:
            print(line)

edit_deploy_settings("alessandro-VirtualBox3")


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