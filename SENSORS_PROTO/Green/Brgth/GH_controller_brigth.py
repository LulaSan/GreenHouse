from ssl import HAS_TLSv1_3

from numpy.lib.shape_base import apply_over_axes
from Subscriber_get_info_b import *
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
        
        self.topic_bright = '/light_command_message'
        self._paho_mqtt = PahoMQTT.Client(self.clientID, False)

        self.conf=json.load(open("settings_controller.json"))

        greenHouseInfo = json.loads(requests.get(
            self.conf['url']+'/greenhouses'
            ).text)
        self.cat = greenHouseInfo

        #THRESHOLD_BRIGHT
        self.brigth_min = greenHouseInfo[["GREENHOUSE_ID"]==self.clientID]['THRESHOLD_BRIGHT_MIN']
        self.brigth_max = greenHouseInfo[["GREENHOUSE_ID"]==self.clientID]['THRESHOLD_BRIGHT_MAX']
        
        self.status = greenHouseInfo[["GREENHOUSE_ID"]==self.clientID]["STATUS_CONTROLL_BRIGTH"]

        # SENSOR TOPIC
        self.sensor_topic_pub = greenHouseInfo[["GREENHOUSE_ID"]==self.clientID]['SENSORS_TOPIC']
        
        #Mode: 0=Automatic || 1= Manuale
        self.mode = greenHouseInfo[["GREENHOUSE_ID"]==self.clientID]['STATUS_CONTROLL_BRIGTH']
        
        # Status Actuator
        self.status = greenHouseInfo[["GREENHOUSE_ID"]==self.clientID]["STATUS_WINDOW"]

    def start_pub(self):
        self._paho_mqtt.connect(self.messageBroker, self.messageBrokerPort)
        self._paho_mqtt.loop_start()


    def stop_pub(self):
        self._paho_mqtt.loop_stop()
        self._paho_mqtt.disconnect()

    def myOnConnect(self, paho_mqtt, userdata, flags, rc):
        print("PUBLISHER --> Connected to %s with result code: %d" % (self.messageBroker, rc))

    def actuator(self,brgh):
        #BRIGTHNESS
        self.brgh = brgh
        self.max_br = self.brigth_max
        self.min_br = self.brigth_min
        soggetto = Linker(self.clientID,self.messageBroker,self.messageBrokerPort)
    
        self.server_name = self.conf['url']
        self.port = self.conf['port']

        if self.mode == 1: #automatico
            if self.brgh > self.max_br and self.status == 1:
                soggetto.start_pub()
                message = {"method": "setLight",
                        "params": 0
                        }
                self._paho_mqtt.publish(self.topic_bright, json.dumps(message), 2)
                print(message)
                soggetto.stop_pub()

                new_value = {"STATUS_WINDOW": 0} 
                greenhouse_id=self.clientID
                res =(requests.post(self.server_name + ':' + str(self.port) + f"/greenhouse/{greenhouse_id}",json=new_value).text) 
                print(res)                        

            elif self.brgh < self.min_br and self.status == 0:
                soggetto.start_pub()
                message = {"method": "setLight",
                        "params": 1
                        }
                self._paho_mqtt.publish(self.topic_bright, json.dumps(message), 2)
                print(message)
                soggetto.stop_pub()

                new_value = {"STATUS_WINDOW": 1} 
                greenhouse_id=self.clientID
                res =(requests.post(self.server_name + ':' + str(self.port) + f"/greenhouse/{greenhouse_id}",json=new_value).text) 
                print(res)

        else:
            if self.brgh > self.min_br and self.brgh < self.max_br:
                if self.status == 0:
                    soggetto.start_pub()
                    message = {"method": "setLight",
                            "params": 1
                            }
                    self._paho_mqtt.publish(self.topic_bright, json.dumps(message), 2)
                    print(message)
                    soggetto.stop_pub()
                    
                    new_value = {"STATUS_WINDOW": 1} 
                    greenhouse_id=self.clientID
                    res =(requests.post(self.server_name + ':' + str(self.port) + f"/greenhouse/{greenhouse_id}",json=new_value).text) 
                    print(res)     
                    
                    new_value = {"STATUS_CONTROLL_BRIGTH": 1} 
                    greenhouse_id=self.clientID
                    res =(requests.post(self.server_name + ':' + str(self.port) + f"/greenhouse/{greenhouse_id}",json=new_value).text) 
                    print(res)

                elif self.status==1:
                    soggetto.start_pub()
                    message = {"method": "setLight",
                            "params": 0
                            }
                    self._paho_mqtt.publish(self.topic_bright, json.dumps(message), 2)
                    print(message)
                    soggetto.stop_pub()
                    
                    new_value = {"STATUS_WINDOW": 0} 
                    greenhouse_id=self.clientID
                    res =(requests.post(self.server_name + ':' + str(self.port) + f"/greenhouse/{greenhouse_id}",json=new_value).text) 
                    print(res)
                    
                    new_value = {"STATUS_CONTROLL_BRIGTH": 1} 
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
            topic_sensor = greenH[["GREENHOUSE_ID"]==green_ID]['SENSORS_TOPIC_BRGHT']
            
            
            connect= Subscriber_get_info_b("controller_brgth",topic_sensor,conf['broker'], conf['port'])
            
            server_name = conf['url']
            port = 2000
            
            operator = Linker(green_ID,conf['broker'], conf['port'])

            # faccio partire il flusso dati
            connect.start()
            time.sleep(5)

            brgh_senor = connect.myB()
            print(brgh_senor)
            operator.actuator(brgh_senor)

            connect.stop()
