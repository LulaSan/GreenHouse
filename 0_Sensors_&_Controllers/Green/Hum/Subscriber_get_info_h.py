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
    def myID(self):
        id= (self.id)
        print(id)
        return id

if __name__=='__main__':
    BROKER="13.59.136.106"

    coll=Subscriber_get_info_h("controller_brght","/p4iot/greenhouses/+/sensors/humidity","13.59.136.106",1883)
    coll.start()
    print("here there are the value of your temperatire sensor, \n--> ")
    finish=0;
    while True:
        time.sleep(1)
        finish+=1;
        if finish==180:
            break
    coll.stop()
