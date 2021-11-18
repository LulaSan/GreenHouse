from ssl import HAS_TLSv1_3

from numpy.lib.shape_base import apply_over_axes
from Subscriber_get_info_t import *
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
        
        self.topic_temp = 'vent_command_message'
        self._paho_mqtt = PahoMQTT.Client(self.clientID, False)
        
        self.conf=json.load(open("settings_controller.json"))
        
        greenHouseInfo = json.loads(requests.get(
            self.conf['url']+'/greenhouses'
            ).text)
        
        self.cat = greenHouseInfo

        #THRESHOLD_temp
        self.temp_min = greenHouseInfo[["GREENHOUSE_ID"]==self.clientID]['THRESHOLD_TEMPER_MIN']
        self.temp_max = greenHouseInfo[["GREENHOUSE_ID"]==self.clientID]['THRESHOLD_TEMPER_MAX']
        
        self.status = greenHouseInfo[["GREENHOUSE_ID"]==self.clientID]["STATUS_CONTROLL_TEMPER"]

        # SENSOR TOPIC
        self.sensor_topic_pub = greenHouseInfo[["GREENHOUSE_ID"]==self.clientID]['SENSORS_TOPIC_TEMP']
        
        #Mode: 0=Automatic || 1= Manual
        self.mode = greenHouseInfo[["GREENHOUSE_ID"]==self.clientID]['STATUS_CONTROLL_TEMPER']
        
        # Status Actuator
        self.status = greenHouseInfo[["GREENHOUSE_ID"]==self.clientID]["STATUS_VENT"]
    
    
    def start_pub(self):
        self._paho_mqtt.connect(self.messageBroker, self.messageBrokerPort)
        self._paho_mqtt.loop_start()


    def stop_pub(self):
        self._paho_mqtt.loop_stop()
        self._paho_mqtt.disconnect()

    def myOnConnect(self, paho_mqtt, userdata, flags, rc):
        print("PUBLISHER --> Connected to %s with result code: %d" % (self.messageBroker, rc))

    def actuator(self,temp):
        #temp
        self.temp = temp
        self.max_temp = self.temp_max
        self.min_temp = self.temp_min
        soggetto = Linker(self.clientID,self.messageBroker,self.messageBrokerPort)
    
        self.server_name = self.conf['url']
        self.port = 2000

        if self.mode == 1: #automatic
            if self.temp > self.max_temp and self.status == 1:
                soggetto.start_pub()
                message = {"method": "setVent",
                        "params": 0
                        }
                self._paho_mqtt.publish(self.topic_temp, json.dumps(message), 2)
                print(message)
                soggetto.stop_pub()

                new_value = {"STATUS_VENT": 0} 
                greenhouse_id=self.clientID
                res =(requests.post(self.server_name + ':' + str(self.port) + f"/greenhouse/{greenhouse_id}",json=new_value).text) 
                print(res)                        

            elif self.temp < self.min_temp and self.status == 0:
                soggetto.start_pub()
                message = {"method": "setVent",
                        "params": 1
                        }
                self._paho_mqtt.publish(self.topic_temp, json.dumps(message), 2)
                print(message)
                soggetto.stop_pub()

                new_value = {"STATUS_VENT": 1} 
                greenhouse_id=self.clientID
                res =(requests.post(self.server_name + ':' + str(self.port) + f"/greenhouse/{greenhouse_id}",json=new_value).text) 
                print(res)

        else:
            if self.temp > self.min_temp and self.temp < self.max_temp:
                if self.status == 0:
                    soggetto.start_pub()
                    message = {"method": "setVent",
                            "params": 1
                            }
                    self._paho_mqtt.publish(self.topic_temp, json.dumps(message), 2)
                    print(message)
                    soggetto.stop_pub()
                    
                    new_value = {"STATUS_VENT": 1} 
                    greenhouse_id=self.clientID
                    res =(requests.post(self.server_name + ':' + str(self.port) + f"/greenhouse/{greenhouse_id}",json=new_value).text) 
                    print(res)     
                    
                    new_value = {"STATUS_CONTROLL_TEMPER": 1} 
                    greenhouse_id=self.clientID
                    res =(requests.post(self.server_name + ':' + str(self.port) + f"/greenhouse/{greenhouse_id}",json=new_value).text) 
                    print(res)

                elif self.status==1:
                    soggetto.start_pub()
                    message = {"method": "setVent",
                            "params": 0
                            }
                    self._paho_mqtt.publish(self.topic_temp, json.dumps(message), 2)
                    print(message)
                    soggetto.stop_pub()
                    
                    new_value = {"STATUS_VENT": 0} 
                    greenhouse_id=self.clientID
                    res =(requests.post(self.server_name + ':' + str(self.port) + f"/greenhouse/{greenhouse_id}",json=new_value).text) 
                    print(res)
                    
                    new_value = {"STATUS_CONTROLL_TEMPER": 1} 
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
            topic_sensor = greenH[["GREENHOUSE_ID"]==green_ID]['SENSORS_TOPIC_TEMP']
            
            connect= Subscriber_get_info_t("controller_temperature",topic_sensor, conf['broker'], conf['port'])            
            # connect= Subscriber_get_info_t("controller_temperature",'/p4iot/greenhouses/'+green_ID+'temperature', conf['broker'], conf['port'])
            
            server_name = conf['url']
            port = 2000
            
            operator = Linker(green_ID,conf['broker'], conf['port'])

            connect.start()
            time.sleep(5)

            temp_senor = connect.myT()
            operator.actuator(temp_senor)

            connect.stop()
