import paho.mqtt.client as PahoMQTT
import time
import json
from MyMQTT import*
import time


class Subscriber_get_info_h:
    def __init__(self,clientID,topic,broker,port):
        self.client=MyMQTT(clientID,broker,port,self)
        self.topic=topic
        
    def stop(self):
        self.client.stop()
    def start(self):
        self.client.start()
        self.client.mySubscribe(self.topic)
    def notify(self,topic,msg):
        payload=json.loads(msg) #payload take the string msg and it become a json object
        self.new_status=payload["humidity"]
        self.id=payload["id"]
        # json.dump(datisalvati,open("mysensor.json","w"))
        print(f"humidity: {self.new_status}  ") #the json object is printed as string
    def myH(self):
        h= (self.new_status)
        print(h)
        return h
     def myB(self):
      id=self.id
      return id

