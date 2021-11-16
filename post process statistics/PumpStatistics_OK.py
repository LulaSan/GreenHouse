from MyMQTT import *
import json
import cherrypy
import requests
import time
import paho.mqtt.client as mqtt

class PumpStatistics():
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
        self.activation_time=data['activation_time']
        self.ton=data['last_ton']
        self.toff=data['last_toff']
    
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
        
    def activation(self):
        if self.status == True: #pump On
            self.ton = self.toff
            self.activation_time += self.time - self.ton 
        else:
            self.toff = self.time
        
        return self.activation_time , self.toff ,self.ton
class Client_statistics():
    def __init__(self,clientID,topic,broker,port):
        register = {}
        self.clientID=clientID
        self.broker=broker
        self.port=port
        self.topic=topic
        self.IDlist=IDlist
        self.register=register.fromkeys(self.IDlist,0)
        
        try:
            file = open("TBsettings.json", "r")
            json_TB = json.loads(file.read())
            file.close()
        except:
            print("Error in reading TBsettings.json file!")
        
        self.TBbroker=json_TB['TBbroker']
        self.TBport=json_TB['TBport']
        self.TBpath=json_TB['TBpath']
        
        for k in self.register:
            self.register[k]={
                    #'bn':'',
                    'min':100000,
                    'max':0,
                    'avg':1,
                    'activation_time':0,
                    'status': False,
                    'total':0,
                    'sample':0,
                    'last_ton':0,
                    'last_toff':0
                }
        
    def start(self):
        self.client=MyMQTT(clientID,broker,port,self)
        self.client.start()
        self.client.mySubscribe(self.topic)
        #TB start
        self.TBclient = mqtt.Client()  

    def notify(self,topic,msg):
        payload=json.loads(msg) #from payload i receive a string message-> convert it in a json 
        moisture=payload["humidity"] #from the payload.json i set all the variable 
        bn=str(payload["bn"])#id
        self.bn=bn
        ts=payload["ts"]
        status=payload["status_pump"]
        battery=payload["battery"]
        
        if bn in self.IDlist:
            print(f"The pump has been set {status} at {ts} by {bn}")
            print(f"The level of the battery is: {battery}")
            if battery < 10:
                print(f"The level of the battery is less than 10%. Please recharge the battery related to the sensor {bn}")
            self.register[bn]['status']= status
            self.register[bn]['total'] += moisture
            self.register[bn]['sample'] += 1
            #creo un oggetto con i dati correnti per poter calcolare le statistiche
            #current_data=PumpStatistics(bn,self.register[bn]['min'],self.register[bn]['max'],self.register[bn]['avg'],self.register[bn]['activation_time'],moisture)
            current_data=PumpStatistics(moisture,self.register[bn],bn,ts)
            #aggiorno le statistiche per pubblicarle
            self.register[bn].update({
                'bn':bn,
                'min':current_data.min(),
                'max':current_data.max(),
                'avg':current_data.avarage(),
                'activation_time':current_data.activation()[0],
                'last_ton':current_data.activation()[2],
                'last_toff':current_data.activation()[1]
                 })

            result={
                'bn':bn,
                'min':current_data.min(),
                'max':current_data.max(),
                'avg':current_data.avarage(),
                'activation_time':current_data.activation()[0],
            }
            #publish the new statistics
            #self.client.myPublish("p4iot/plants/{}/pump/statistics".format(bn), result)
            # public to TB with API:
            self.TBclient.username_pw_set(bn)
            self.TBclient.connect(self.TBbroker,self.TBport,60)
            self.TBclient.loop_start()
            self.TBclient.publish(self.TBpath,json.dumps(result))
            self.TBclient.loop_stop()
        else:
            return f"the device {bn} is not registered"
      

if __name__=="__main__":
    IDlist=[]
    try:
        file = open("settings_watering.json", "r")
        json_str = file.read()
        file.close()
    except:
        print("Error in reading settings_watering.json file!")
    
    # Si accede al catalog per ottenere l'IP e la porta del broker e il periodo di aggiornamento dati

    json_dic = json.loads(json_str)
    #response=requests.get("http://p4iotgreenhouse.ddns.net:2000/plants")
    response = requests.get(str("http://"+str(json_dic["server"])+':'+str(json_dic["port_s"])+str(json_dic["path"])))
    #response = requests.get(str("http://localhost:2000/plants"))
    if response.status_code == 200:
        content=json.loads(response.text)
        #broker = str(content[0]["BROKER_HOST"]) #quello sul catalog è sbagliato
        #port = int(content[0]["BROKER_PORT"])
        broker="13.59.136.106"
        port=1883
        
        #ottengo la lista completa delle piante registrate nel catalog
        for p in range(len(content)):
            IDlist.append(content[p]["PLANT_ID"])
        
        print(IDlist)
    else:
        print(f'status code:{response.status_code} error during the request')
        

    clientID='WateringStatistics'       #devo prenderlo dal catalog?
    c=Client_statistics(clientID,"/p4iot/plants/#",broker,port)
    c.start()

    while True:
        water_period=json.loads(requests.get(str("http://"+str(json_dic["server"])+':'+str(json_dic["port_s"])+"/statistic/water_period")).text)
        time.sleep(water_period)
