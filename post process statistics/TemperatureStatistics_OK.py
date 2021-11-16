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
        self.count=data['count']
        

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
                    'min_t':100000,
                    'max_t':0,
                    'avg_t':1,
                    'total_t':0,
                    'sample_t':0,
                    'count':0
                }
        
    def start(self):
        self.client=MyMQTT(clientID,broker,port,self)
        self.client.start()
        self.client.mySubscribe(self.topic)
        #TB start
        self.TBclient = mqtt.Client()
        self.temperature_period=1
        
    def notify(self,topic,msg):
        payload=json.loads(msg) #from payload i receive a string message-> convert it in a json 
        temperature=payload["temperature"] #from the payload.json i set all the variable 
        bn=str(payload["bn"])#id
        ts=payload["ts"]        
        battery=payload["battery"]
        
        if bn in self.IDlist:
            print(f"The temperature sensor {bn} sent a value of {temperature}°C at {ts}")
            print(f"The level of the battery is: {battery}")
            if battery < 10:
                print(f"The level of the battery is less than 10%. Please recharge the battery related to the sensor {bn}")
            self.register[bn]['total_t'] += temperature
            self.register[bn]['sample_t'] += 1
            self.register[bn]['count'] += 1
            
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
            #publish the new statistics to TB
            
            if self.register[bn]['count'] == self.water_period:
                self.register[bn]['count']=0
                self.TBclient.username_pw_set(bn)
                self.TBclient.connect(self.TBbroker,self.TBport,60)
                self.TBclient.loop_start()
                self.TBclient.publish(self.TBpath,json.dumps(result))
                self.TBclient.loop_stop()
                print(f'Dati inviati a TB sulla pianta {bn}')
                
            if self.last_water_period != self.water_period:
                self.register[bn]['count']=0
        else:
            return f"the device {bn} is not registered"
        
    def timing(self,server,port,topic_period):
        self.last_water_period=self.water_period
        self.water_period=json.loads(requests.get(str("http://"+str(server)+':'+str(port)+topic_period)).text)

        return self.water_period
      

if __name__=="__main__":
    IDlist=[]
    try:
        file = open("settings_temperature.json", "r")
        json_str = file.read()
        file.close()
    except:
        print("Error in reading settings_temperature.json file!")
    
    # Si accede al catalog per ottenere l'IP e la porta del broker e il periodo di aggiornamento dati
    json_dic = json.loads(json_str)
    topic_sub= json_dic['topic_sub']
    response = requests.get(str("http://"+str(json_dic["server"])+':'+str(json_dic["port_s"])+str(json_dic["path"])))
   

    if response.status_code == 200:
        content=json.loads(response.text)
        broker = str(content[0]["BROKER_HOST"]) 
        port = int(content[0]["BROKER_PORT"])
        
        print( response.status_code)
        #ottengo la lista completa delle piante registrate nel catalog
        for p in range(len(content)):
            IDlist.append(content[p]["PLANT_ID"])
        
        print(IDlist)
    else:
        print(f'status code:{response.status_code} error during the request')
        

    clientID='TemperatureStatistics'
    c=Client_temperature(clientID,topic_sub,broker,port)
    c.start()

    while True:
        temperature_period=c.timing(json_dic["server"],json_dic["port_s"],"/statistic/water_period")
        print('valore aggiornamento statistiche'+':'+ str(temperature_period))
        time.sleep(temperature_period)
