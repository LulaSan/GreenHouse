from MyMQTT import*
from Emulated_sensors import Sensor_b, TB_Sensor_b
# import paho.mqtt.client as mqtt
import time
import random
import numpy as np
import requests


if __name__=="__main__":

    # Simulated Value
    time_alive = 24*60*1000
    lam = 24
    val = 25+0.3*np.random.poisson(lam, time_alive) 
    val = np.clip(val, 10, 60)

    x = np.arange(0, 3 * np.pi, 0.000005)
    batt = 40 + 20* np.sin(x)
    batt = np.round(batt, 2)
    batt = np.clip(batt, 0, 100)
    

    # Configuration for MQTT

    # conf=json.load(open("settings.json"))
    # conf=json.load(open("settings.json"))
    

    id="84F3EB33D049"
    S_cat=Sensor_b(id+'brg',"/p4iot/greenhouses/{}/brigthness".format(id),"13.59.136.106", 1883)
    S_tb = TB_Sensor_b(id,'Wsx4vSU7SCBUPqH4BRN6','demo.thingsboard.io','v1/devices/me/telemetry',1883,60)
    
    S_cat.run()    
    S_tb.con()

    for cnt in range(len(val)): 

        greenHouseInfo = json.loads(requests.get(
            'http://ec2-13-59-136-106.us-east-2.compute.amazonaws.com:2000/greenhouses'#/ABCDEFG/COMMANDS_TOPIC'
            ).text)
        #THRESHOLD_BRIGHT
        status = greenHouseInfo[["GREENHOUSE_ID"]==id]["STATUS_CONTROLL_BRIGTH"]

        sensor_data = {"brightness" : val[cnt], "battery": batt[cnt] ,"status": status}  
        S_cat.sendData(val[cnt],batt[cnt],status)
        S_tb.pub_tb(sensor_data)
        time.sleep(1)

    S_cat.end()
    S_tb.unconn()
