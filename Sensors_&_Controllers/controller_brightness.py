from ssl import HAS_TLSv1_3

from numpy.lib.shape_base import apply_over_axes
from Subscriber_get_info_b import *
import time
import paho.mqtt.client as PahoMQTT
import random
import requests
import json
from MyMQTT import*

BN_INDEX_PROTO = ["84F3EB33D049" ]#,"111111111111","000000000000"] #"bn": "84F3EB33DB49",

class Linker:
    def __init__(self,clientID,messageBroker,messageBrokerPort):
        
        self.clientID = clientID
        self.messageBroker = messageBroker
        self.messageBrokerPort = messageBrokerPort
        
        self.topic_bright = '/light_command_message'
        self._paho_mqtt = PahoMQTT.Client(self.clientID, False)

        #   QUESTE SONO PER L'ONLINE# greenHouseInfo = json.loads(requests.get(
        # # "http://p4iotgreenhouse.ddns.net:2000//p41ot" + "/" + "greenhouses"+ "/" + self.bn).text)
        with open('Catalog.json') as cat:
            data = json.load(cat)
            greenHouseInfo= data['Greenhouses']

            #THRESHOLD_BRIGHT
            self.brigth_min = greenHouseInfo[0]['THRESHOLD_BRIGHT_MIN']
            self.brigth_max = greenHouseInfo[0]['THRESHOLD_BRIGHT_MAX']
            
            self.status = greenHouseInfo[0]["STATUS_CONTROLL_BRIGTH"]

            # SENSOR TOPIC
            self.sensor_topic_pub = greenHouseInfo[0]['SENSORS_TOPIC']
    ############################
    # Pub
    ############################
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
        
        if self.status == 1: #automatico
            if self.brgh > self.max_br:
                soggetto.start_pub()
                message = {"method": "setLight",
                        "params": 0
                        }
                self._paho_mqtt.publish(self.topic_bright, json.dumps(message), 2)
                print(message)
                soggetto.stop_pub()

            elif self.brgh < self.min_br:
                soggetto.start_pub()
                message = {"method": "setLight",
                        "params": 1
                        }
                self._paho_mqtt.publish(self.topic_bright, json.dumps(message), 2)
                print(message)
                soggetto.stop_pub()
        else:
            if self.brgh > self.min_br and self.brgh < self.max_br:
                sub=Subscriber_get_info_b("controller_temp",'/p4iot/greenhouses/84F3EB33D049/sensors', '127.0.0.1', 1883)
                sub.start()
                
                
                
                SE APERTO --> CHIUDO
                SE CHIUSO --> apply_over_axes
                
                AGGIORNO STATO DA MANUALE  A AUTOMATICO
                
                ########################## DOVE TROVO IL MESSAGGIO DI AZIONAMENTO DEGLI ATTUATORI??
                
                
                
                
                
                
                sub.stop()

if __name__ == '__main__':
    with open('Catalog.json') as cat:
        data = json.load(cat)
        greenH = data['Greenhouses']
        num_of_greenHouses = len(greenH)
        
        connect= Subscriber_get_info_b("controller_temp",'/p4iot/greenhouses/84F3EB33D049/sensors', '127.0.0.1', 1883)
        operator = Linker("pubblisher_sensor",'127.0.0.1', 1883)
        # faccio partire il flusso dati
        connect.start()
            # temper = connect.myOnMessageReceived( paho_mqtt , userdata, msg)
            # # print()
        a = 0
        while (a < 30):
            a += 1
            time.sleep(1)
                # print(connect.myT())
            ### qui dentro devo verificare se i valori sono o meno maggiori o minori di quelli di soglia sparati dal sensore
            brgh_senor = connect.myB()
            # print(temp_sensor,brgh_senor,hum_sensor)
            operator.actuator(brgh_senor)
            
        connect.stop()