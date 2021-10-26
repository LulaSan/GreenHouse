from MyMQTT import *
import json
import cherrypy
import requests
import time
import paho.mqtt.client as mqtt

class TemperatureStatistics():
    #def __init__(self,bn,minimum,maximum,avarage,act_time,moisture):
    def __init__(self,moisture,data,bn,ts):
        #ho tutti i valori precedenti delle medie, corrispondenti a bn
        self.bn=bn
        self.moisture=moisture
        self.time=ts
        self.minimum=data['min']
        self.maximum=data['max']
        self.total=data['total']
        self.samples=data['sample']
        self.status=data['status']

    def avarage(self):
        avg = self.total / self.samples
        return avg
    def max(self,):
        if self.moisture > self.maximum:
            self.maximum = self.moisture
        return self.maximum
    def min(self,):
        if self.moisture < self.minimum:
            self.minimum = self.moisture
        return self.minimum

class Client():
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
                    'min':100000,
                    'max':0,
                    'avg':1,
                    'total':0,
                    'sample':0
                }
        
    def start(self):
        self.client=MyMQTT(clientID,broker,port,self)
        self.client.start()
        self.client.mySubscribe(self.topic)
    

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
            self.register[bn]['total'] += temperature
            self.register[bn]['sample'] += 1
            #creo un oggetto con i dati correnti per poter calcolare le statistiche
            current_data=TemperatureStatistics(moisture,self.register[bn],bn,ts)
            #aggiorno le statistiche per pubblicarle
            self.register[bn].update({
                'bn':bn,
                'min':current_data.min(),
                'max':current_data.max(),
                'avg':current_data.avarage()
                 })

            result={
                'bn':bn,
                'min':current_data.min(),
                'max':current_data.max(),
                'avg':current_data.avarage()
            }
            #publish the new statistics
            self.client.myPublish("/p4iot/greenhouse/{}/temperature/statistics".format(bn), result)
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
    response = requests.get(str("http://"+str(json_dic["broker"])+':'+str(json_dic["port"])+str(json_dic["path"])))
    
    if response.status_code == 200:
        content=json.loads(response.text)
        broker = str(content[0]["BROKER_HOST"]) 
        port = int(content[0]["BROKER_PORT"])
        #broker="3.139.73.64"
        #port=1884
        print( response.status_code)
        #ottengo la lista completa delle piante registrate nel catalog
        for p in range(len(content)):
            IDlist.append(content[p]["PLANT_ID"])
        
        print(IDlist)
    else:
        print(f'status code:{r.status_code} error during the request')
        

    clientID='TemperatureStatistics'
    c=Client(clientID,"/p4iot/greenhouses/+/sensors",broker,port)
    c.start()

    ####while connect_flag==1: #aggiungere connect_flag in MyMQTT in on_connect function (better?)
    while True:
        time.sleep(1)
