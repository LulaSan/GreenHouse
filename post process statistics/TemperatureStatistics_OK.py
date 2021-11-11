from MyMQTT import *
import json
import cherrypy
import requests
import time
import paho.mqtt.client as mqtt

class TemperatureStatistics():
    def __init__(self,temperature,data,bn,ts):
        self.bn=bn
        self.temperature=temperature
        self.time=ts
        self.minimum=data['min_t']
        self.maximum=data['max_t']
        self.total=data['total_t']
        self.samples=data['sample_t']
        

    def avarage(self):
        avg = self.total / self.samples
        return avg

    def max(self,):
        if self.temperature > self.maximum:
            self.maximum = self.temperature
        return self.maximum
        
    def min(self,):
        if self.temperature < self.minimum:
            self.minimum = self.temperature
        return self.minimum

class Client_temperature():
    def __init__(self,clientID,topic,broker,port):
        register={}
        self.clientID=clientID
        self.broker=broker
        self.port=port
        self.topic=topic
        self.IDlist=IDlist
        self.register=register.fromkeys(self.IDlist,0)
        for k in self.register:
            self.register[k]={
                    #'bn':'',
                    'min_t':100000,
                    'max_t':0,
                    'avg_t':1,
                    'total_t':0,
                    'sample_t':0
                }
        
    def start(self):
        self.client=MyMQTT(clientID,broker,port,self)
        self.client.start()
        self.client.mySubscribe(self.topic)
        #TB start
        self.TBclient = mqtt.Client()
        self.TBclient.connect('demo.thingsboard.io',1883,60)
        self.TBclient.loop_start()
    

    def notify(self,topic,msg):
        payload=json.loads(msg) #from payload i receive a string message-> convert it in a json 
        temperature=payload["temperature"] #from the payload.json i set all the variable 
        bn=str(payload["bn"])#id
        ts=float(payload["ts"])        
        battery=payload["batt"]
        
        if bn in self.IDlist:
            print(f"The temperature sensor {bn} sent a value of {temperature}°C at {ts}")
            print(f"The level of the battery is: {battery}")
            if battery < 10:
                print(f"The level of the battery is less than 10%. Please recharge the battery related to the sensor {bn}")
            self.register[bn]['total_t'] += temperature
            self.register[bn]['sample_t'] += 1
            current_data=TemperatureStatistics(temperature,self.register[bn],bn,ts)

            #aggiorno le statistiche per pubblicarle
            self.register[bn].update({
                'bn':bn,
                'min_t':current_data.min(),
                'max_t':current_data.max(),
                'avg_t':current_data.avarage()
                 })

            result={
                'bn':bn,
                'min_t':current_data.min(),
                'max_t':current_data.max(),
                'avg_t':current_data.avarage()
            }
            #publish the new statistics
            #self.client.myPublish("/p4iot/greenhouse/{}/temperature/statistics".format(bn), result)
            self.TBclient.username_pw_set(bn)
            self.TBclient.publish('v1/devices/me/telemetry',json.dumps(result))
        else:
            return f"the device {bn} is not registered"
      

if __name__=="__main__":
    IDlist=[]
    try:
        file = open("settings_temperature.json", "r")
        json_str = file.read()
        file.close()
    except:
        print("Error in reading settings.json file!")
    
    # Si accede al catalog per ottenere l'IP e la porta del broker e il periodo di aggiornamento dati
    json_dic = json.loads(json_str)
    #response=requests.get("http://p4iotgreenhouse.ddns.net:2000/plants")
    #response = requests.get(str("http://"+str(json_dic["broker"])+':'+str(json_dic["port"])+str(json_dic["path"])))
    response = requests.get(str("http://localhost:2000/plants"))

    if response.status_code == 200:
        content=json.loads(response.text)
        #broker = str(content[0]["BROKER_HOST"]) 
        #port = int(content[0]["BROKER_PORT"])
        broker="localhost"
        port=1883
        print( response.status_code)
        #ottengo la lista completa delle piante registrate nel catalog
        for p in range(len(content)):
            IDlist.append(content[p]["PLANT_ID"])
        
        print(IDlist)
    else:
        print(f'status code:{response.status_code} error during the request')
        

    clientID='TemperatureStatistics'
    c=Client_temperature(clientID,"/p4iot/greenhouses/+/sensors",broker,port)
    c.start()

    while True:
        time.sleep(5)
