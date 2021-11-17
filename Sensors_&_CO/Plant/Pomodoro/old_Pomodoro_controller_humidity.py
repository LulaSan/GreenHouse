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

        plantInfo = json.loads(requests.get(
            'http://ec2-13-59-136-106.us-east-2.compute.amazonaws.com:2000' + '/' + 'plants'
            ).text)
        self.cat = plantInfo

        #THRESHOLD_BRIGHT
        self.hum_min = plantInfo[["PLANT_ID"]==self.clientID]['THRESHOLD_MOIST_MIN'] # get path/plant
        self.hum_max = plantInfo[["PLANT_ID"]==self.clientID]['THRESHOLD_MOIST_MAX']
        
        # self.status = plantInfo[["PLANT_ID"]==self.clientID]["STATUS_CONTROLL_HUMIDITY"]

        # # SENSOR TOPIC
        # self.sensor_topic_pub = plantInfo[["PLANT_ID"]==self.clientID]['SENSORS_TOPIC']
        
        # #Mode: 0=Automatic || 1= Manual
        # self.mode = plantInfo[["PLANT_ID"]==self.clientID]['STATUS_CONTROLL_HUMIDITY']
        
        # Status Actuator
        self.status = plantInfo[["PLANT_ID"]==self.clientID]["STATUS_PUMP"]
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

    def actuator(self,hmdt):
        #BRIGTHNESS
        self.hmdt = hmdt
        self.max_hum = self.hum_max
        self.min_hum = self.hum_min
        soggetto = Linker(self.clientID,self.messageBroker,self.messageBrokerPort)
    
        self.server_name = 'http://ec2-13-59-136-106.us-east-2.compute.amazonaws.com'
        self.port = 2000


        if self.hmdt > self.max_hum and self.status == 1:
            soggetto.start_pub()
            message = {"method": "setPump",
                    "params": 0
                    }
            self._paho_mqtt.publish(self.topic_tempt, json.dumps(message), 2)
            print(message)
            soggetto.stop_pub()

            new_value = {"STATUS_PUMP": 0} 
            # new_value = {"STATUS_PUMP": 0}
            PLANT_ID=self.clientID
            res =(requests.post(self.server_name + ':' + str(self.port) + f"/plant/{PLANT_ID}",json=new_value).text) 
            print(res)                        

        elif self.hmdt < self.min_hum and self.status == 0:
            soggetto.start_pub()
            message = {"method": "setPump",
                    "params": 1
                    }
            self._paho_mqtt.publish(self.topic_tempt, json.dumps(message), 2)
            print(message)
            soggetto.stop_pub()

            new_value = {"STATUS_PUMP": 1} 
            # new_value = {"STATUS_PUMP": 1} 
            PLANT_ID=self.clientID
            res =(requests.post(self.server_name + ':' + str(self.port) + f"/plant/{PLANT_ID}",json=new_value).text) 
            print(res)


if __name__ == '__main__':


    plant_cat = json.loads(requests.get(
    'http://ec2-13-59-136-106.us-east-2.compute.amazonaws.com:2000' + '/' + 'plants' 
    ).text)
    while True:

        # num = 2
        plant_ID = '84F3EB33DB49'
        print(plant_ID)
        connect= Subscriber_get_info_h("controller_brgth","/p4iot/plants/{}/sensors_pomo".format(plant_ID), '13.59.136.106', 1883)

        
        server_name = 'http://ec2-13-59-136-106.us-east-2.compute.amazonaws.com'
        port = 2000
        # operator = Linker(clinet_id,server_name, 2000)
        # operator = Linker(plant_ID,server_name, port)
        operator = Linker(plant_ID,'13.59.136.106', 1883)

        # faccio partire il flusso dati
        connect.start()
        time.sleep(5)

        humid_senor = connect.myH()
        operator.actuator(float(humid_senor))

        # connect.stop()
