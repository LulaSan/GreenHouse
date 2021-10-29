from ssl import HAS_TLSv1_3
from Subscriber_get_info_h import *
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
        
        self.topic_humid = '/window_command_message'
        self._paho_mqtt = PahoMQTT.Client(self.clientID, False)

        #   QUESTE SONO PER L'ONLINE# greenHouseInfo = json.loads(requests.get(
        # # "http://p4iotgreenhouse.ddns.net:2000//p41ot" + "/" + "greenhouses"+ "/" + self.bn).text)
        with open('Catalog.json') as cat:
            data = json.load(cat)
            greenHouseInfo= data['Greenhouses']
        
            #THRESHOLD_HUMID
            self.hum_min = greenHouseInfo[0]['THRESHOLD_HUMID_MIN'] # get path/greenhouse
            self.hum_max = greenHouseInfo[0]['THRESHOLD_HUMID_MAX']

            # SENSOR TOPIC
            self.sensor_topic_pub = greenHouseInfo[0]['SENSORS_TOPIC']

            #Status GreenHouse
            self.status = greenHouseInfo[0]['STATUS_CONTROLL_HUMIDITY']
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

    def actuator(self,hmdt ):
        #HUMIDITY
        self.hmdt = hmdt
        self.max_hu = self.hum_max
        self.min_hu = self.hum_min
        soggetto = Linker(self.clientID,self.messageBroker,self.messageBrokerPort)
        if self.status == 0:
            if self.hmdt > self.max_hu:
                soggetto.start_pub()
                message = {"method": "setWindow",
                        "params": 0
                        }
                self._paho_mqtt.publish(self.topic_humid, json.dumps(message), 2)
                print(message)
                soggetto.stop_pub()

            elif self.hmdt < self.min_hu:
                soggetto.start_pub()
                message = {"method": "setWindow",
                        "params": 1
                        }
                self._paho_mqtt.publish(self.topic_humid, json.dumps(message), 2)
                print(message)
                soggetto.stop_pub()
        if self.status == 1:
            pass

if __name__ == '__main__':
    with open('Catalog.json') as cat:
        data = json.load(cat)
        greenH = data['Greenhouses']
        num_of_greenHouses = len(greenH)
        
        connect= Subscriber_get_info_h("controller_temp",'/p4iot/greenhouses/84F3EB33D049/sensors', '127.0.0.1', 1883)
        operator = Linker("pubblisher_sensor",'127.0.0.1', 1883)
        # faccio partire il flusso dati
        connect.start()
        # temper = connect.myOnMessageReceived( paho_mqtt , userdata, msg)

        a = 0
        while (a < 1440):
            a += 1
            time.sleep(1)

            ### qui dentro devo verificare se i valori sono o meno maggiori o minori di quelli di soglia sparati dal sensore
            hum_sensor = connect.myH()

            operator.actuator(hum_sensor)
            
        connect.stop()