from MyMQTT import*
import string
import time
import random
class Sensor():
    def __init__(self,clientID,topic,broker,port):
        self.client = MyMQTT(clientID,broker,port,None)
        self.topic=topic
        #self.clientID=clientID
        self.__message={"bn":clientID,"n":"pump_sensor","pump":"","ts":"","moisture":None}
        
    def run(self):
        self.client.start()
        #print('{} has started'.format(self.clientID))

    def end(self):
        self.client.stop()
        #print('{} has stopped'.format(self.clientID))

    def sendData(self,value):
        message=self.__message
        #message["bn"] = string.ascii_uppercase + string.digits
        message["moisture"] = value 
        message["ts"]=str(time.strftime("%H:%M:%S"))
        message["pump"]=random.choice([True, False])
        message["batt"]=batt
        #self.battery=payload["batt"]
        self.client.myPublish(self.topic,message)

if __name__=="__main__":
    conf=json.load(open("settings.json"))
    id=random.choice(["84F3EB33D049","aAAAAAAAAAAA"])
    s=Sensor(id,"/p4iot/plants/{}/sensors".format(id),"3.139.73.64", 1884)
    s.run()
    for i in range(25):
        value=random.randint(0,100)
        batt=random.randint(0,100)
        s.sendData(value)
        print(f"moisture: {value}   battery: {batt}    by: {id}")
        time.sleep(5)
    s.stop()
