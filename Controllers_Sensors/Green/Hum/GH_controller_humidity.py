from ssl import HAS_TLSv1_3

from numpy.lib.shape_base import apply_over_axes
from Subscriber_get_info_h import *
import time
import paho.mqtt.client as PahoMQTT
import json
from MyMQTT import*
import requests

class Linker:
    def __init__(self,clientID,messageBroker,messageBrokerPort):
        
        self.clientID = clientID
        self.messageBroker = messageBroker
        self.messageBrokerPort = messageBrokerPort
        
        self.topic_tempt = '/light_command_message'
        self._paho_mqtt = PahoMQTT.Client(self.clientID, False)

        self.conf=json.load(open("settings_controller.json"))
        greenHouseInfo = json.loads(requests.get(
            self.conf['url']+'/greenhouses'
            ).text)


        self.hum_min = greenHouseInfo[["GREENHOUSE_ID"]==self.clientID]['THRESHOLD_HUMID_MIN']
        self.hum_max = greenHouseInfo[["GREENHOUSE_ID"]==self.clientID]['THRESHOLD_HUMID_MAX']
        
        # SENSOR TOPIC
        self.sensor_topic_pub = greenHouseInfo[["GREENHOUSE_ID"]==self.clientID]['SENSORS_TOPIC_HUM']
        
        #Mode: 0=Automatic || 1= Manual
        self.mode = greenHouseInfo[["GREENHOUSE_ID"]==self.clientID]['STATUS_CONTROLL_HUMIDITY']
        
        # Status Actuator
        self.status = greenHouseInfo[["GREENHOUSE_ID"]==self.clientID]["STATUS_PUMP"]
        
    def start_pub(self):
        self._paho_mqtt.connect(self.messageBroker, self.messageBrokerPort)
        self._paho_mqtt.loop_start()


    def stop_pub(self):
        self._paho_mqtt.loop_stop()
        self._paho_mqtt.disconnect()

    def myOnConnect(self, paho_mqtt, userdata, flags, rc):
        print("PUBLISHER --> Connected to %s with result code: %d" % (self.messageBroker, rc))

    def actuator(self,hum):
        #humNESS
        self.hum = hum
        self.max_hum = self.hum_max
        self.min_hum = self.hum_min
        soggetto = Linker(self.clientID,self.messageBroker,self.messageBrokerPort)
    
        self.server_name = self.conf['url']
        self.port = 2000

        if self.mode == 1: #automatic
            if self.hum > self.max_hum and self.status == 1:
                soggetto.start_pub()
                message = {"method": "setPump",
                        "params": 0
                        }
                self._paho_mqtt.publish(self.topic_tempt, json.dumps(message), 2)
                print(message)
                soggetto.stop_pub()

                new_value = {"STATUS_PUMP": 0} 
                greenhouse_id=self.clientID
                res =(requests.post(self.server_name + ':' + str(self.port) + f"/greenhouse/{greenhouse_id}",json=new_value).text) 
                print(res)                        

            elif self.hum < self.min_hum and self.status == 0:
                soggetto.start_pub()
                message = {"method": "setPump",
                        "params": 1
                        }
                self._paho_mqtt.publish(self.topic_tempt, json.dumps(message), 2)
                print(message)
                soggetto.stop_pub()

                new_value = {"STATUS_PUMP": 1} 
                greenhouse_id=self.clientID
                res =(requests.post(self.server_name + ':' + str(self.port) + f"/greenhouse/{greenhouse_id}",json=new_value).text) 
                print(res)

        else:
            if self.hum > self.min_hum and self.hum < self.max_hum:
                if self.status == 0:
                    soggetto.start_pub()
                    message = {"method": "setPump",
                            "params": 1
                            }
                    self._paho_mqtt.publish(self.topic_tempt, json.dumps(message), 2)
                    print(message)
                    soggetto.stop_pub()
                    
                    new_value = {"STATUS_PUMP": 1} 
                    greenhouse_id=self.clientID
                    res =(requests.post(self.server_name + ':' + str(self.port) + f"/greenhouse/{greenhouse_id}",json=new_value).text) 
                    print(res)     
                    
                    new_value = {"STATUS_CONTROLL_HUMIDITY": 1} 
                    greenhouse_id=self.clientID
                    res =(requests.post(self.server_name + ':' + str(self.port) + f"/greenhouse/{greenhouse_id}",json=new_value).text) 
                    print(res)

                elif self.status==1:
                    soggetto.start_pub()
                    message = {"method": "setPump",
                            "params": 0
                            }
                    self._paho_mqtt.publish(self.topic_tempt, json.dumps(message), 2)
                    print(message)
                    soggetto.stop_pub()
                    
                    new_value = {"STATUS_PUMP": 0} 
                    greenhouse_id=self.clientID
                    res =(requests.post(self.server_name + ':' + str(self.port) + f"/greenhouse/{greenhouse_id}",json=new_value).text) 
                    print(res)
                    
                    new_value = {"STATUS_CONTROLL_HUMIDITY": 1} 
                    greenhouse_id=self.clientID
                    res =(requests.post(self.server_name + ':' + str(self.port) + f"/greenhouse/{greenhouse_id}",json=new_value).text) 
                    print(res)

if __name__ == '__main__':

    conf=json.load(open("settings_controller.json"))

    greenH = json.loads(requests.get(
            conf['url']+'/greenhouses'
            ).text)
    
    
    num_of_greenHouses = len(greenH)
    
    
    while True:
        for num in range(num_of_greenHouses):
            
            green_ID = greenH[num]["GREENHOUSE_ID"]
            print(green_ID)
            topic_sensor = greenH[["GREENHOUSE_ID"]==green_ID]['SENSORS_TOPIC_HUM']
            connect= Subscriber_get_info_h("controller_hum",topic_sensor, conf['broker'], conf['port'])
            
            server_name = conf['url']
            port = 2000
            operator = Linker(green_ID,conf['broker'], conf['port'])

            connect.start()
            time.sleep(5)

            humid_senor = connect.myH()
            operator.actuator(float(humid_senor))

        connect.stop()
