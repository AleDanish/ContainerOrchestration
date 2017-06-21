import paho.mqtt.client as mqtt  #import the client
import time

class MQTTClient:
    broker_address=""
    client=None
    messages=[]
    
    def __init__(self, ip, client_name):
        self.broker_address=ip
        self.client = mqtt.Client(client_name) #create new instance
        self.client.on_connect=self.on_connect #attach function to callback
        self.client.on_message=self.on_message #attach function to callback
        self.messages=[]

    def on_connect(self, client, userdata, flags, rc):
        m="Connected flags"+str(flags)+"; result code "+str(rc)+"; client_id  "+str(client)
        print(m)
    
    def on_message(self, client, userdata, message):
        msg = str(message.payload.decode("utf-8"))
        topic = message.topic
        print("Message received  "+msg + " on topic " + topic)
        self.messages.append(topic+":"+msg)
    
    def on_log(self, client, userdata, level, buf):
        print("log: ",buf)

    def connect(self):
        self.client.connect(self.broker_address)   #connect to broker
        self.client.loop_start()   #start the loop
    
    def subscribe(self, topic):
        self.client.subscribe(topic)
    
    def publish(self, topic, message):
        self.client.publish(topic, message)
    
    def disconnect(self):
        time.sleep(5) #delay to finish the ongoing tasks before disconnect
        self.client.disconnect()
        self.client.loop_stop()
        
    def log(self):
        self.client.on_log=self.on_log
