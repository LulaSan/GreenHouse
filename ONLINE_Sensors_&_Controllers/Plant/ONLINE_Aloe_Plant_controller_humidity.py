from ssl import HAS_TLSv1_3
from Subscriber_get_info_h import *
import time
import paho.mqtt.client as PahoMQTT
import random
import requests
import json
from MyMQTT import*
import requests
# import cherrypy

class Linker:
    def __init__(self,clientID,messageBroker,messageBrokerPort):
        
        self.clientID = clientID
        self.messageBroker = messageBroker
        self.messageBrokerPort = messageBrokerPort
        
        self.topic_humid = '/window_command_message'
        self._paho_mqtt = PahoMQTT.Client(self.clientID, False)

        #   QUESTE SONO PER L'ONLINE# plantInfo = json.loads(requests.get(
        # # "http://p4iotplant.ddns.net:2000//p41ot" + "/" + "Plants"+ "/" + self.bn).text)
        plantInfo = json.loads(requests.get(
            'http://ec2-13-59-136-106.us-east-2.compute.amazonaws.com:2000' + '/' + 'plants' #/ABCDEFG/COMMANDS_TOPIC'
            ).text)
    

    
        #THRESHOLD_HUMID
        self.hum_min = plantInfo[["PLANT_ID"]==self.clientID]['THRESHOLD_MOIST_MIN'] # get path/plant
        self.hum_max = plantInfo[["PLANT_ID"]==self.clientID]['THRESHOLD_MOIST_MAX']

        # SENSOR TOPIC
        self.sensor_topic_pub = plantInfo[["PLANT_ID"]==self.clientID]['SENSORS_TOPIC']

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

    def actuator(self,hmdt ):
        #HUMIDITY
        self.hmdt = hmdt
        self.max_hu = self.hum_max
        self.min_hu = self.hum_min
        soggetto = Linker(self.clientID,self.messageBroker,self.messageBrokerPort)

        if self.hmdt > self.max_hu:
            soggetto.start_pub()
            message = {"method": "setPump",
                    "params": 0
                    }
            self._paho_mqtt.publish(self.topic_humid, json.dumps(message), 2)
            print(message)
            soggetto.stop_pub()

        elif self.hmdt < self.min_hu:
            soggetto.start_pub()
            message = {"method": "setPump",
                    "params": 1
                    }
            self._paho_mqtt.publish(self.topic_humid, json.dumps(message), 2)
            print(message)
            soggetto.stop_pub()



if __name__ == '__main__':
    
    plantH = json.loads(requests.get(
    'http://ec2-13-59-136-106.us-east-2.compute.amazonaws.com:2000' + '/' + 'plants' 
    ).text)
    
    
    num_of_plant = len(plantH)



    while True:
        for num in range(num_of_plant):
            # num = 2
            plant_ID = plantH[num]["PLANT_ID"]
            print(plant_ID)
            connect= Subscriber_get_info_h("controller_humidity",'/p4iot/plants/'+plant_ID+'/sensors', '13.59.136.106', 1883)

            
            server_name = 'http://ec2-13-59-136-106.us-east-2.compute.amazonaws.com'
            port = 2000

            operator = Linker(plant_ID,'13.59.136.106', 1883)

            # faccio partire il flusso dati
            connect.start()
            time.sleep(5)

            brgh_senor = connect.myH()
            operator.actuator(brgh_senor)

            connect.stop()









