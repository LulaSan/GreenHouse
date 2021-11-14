from MyMQTT import*
from Emulated_sensors import Sensor_b, Sensor_h, TB_Sensor_b, TB_Sensor_h
# import paho.mqtt.client as mqtt
import time
import random
import numpy as np
import requests

# ABCDEFG
if __name__=="__main__":

    # Simulated Value
    time_alive = 24*60*1000
    lam = 24
    val = 45+0.3*np.random.poisson(lam, time_alive) 
    val = np.clip(val, 10, 60)

    x = np.arange(0, 3 * np.pi, 0.000005)
    batt = 40 + 20* np.sin(x)
    batt = np.round(batt, 2)
    batt = np.clip(batt, 0, 100)

    # Configuration for MQTT

    # conf=json.load(open("settings.json"))
    id="ABCDEFG"    

    S_cat=Sensor_h(id,"/p4iot/greenhouses/{}/sensors/humidity".format(id),"13.59.136.106", 1883)
    S_tb = TB_Sensor_h(id,'GqJXcA2EtMZfPzs1FvaF','demo.thingsboard.io','v1/devices/me/telemetry',1883,60)
    
    S_cat.run()    
    S_tb.con()

    for cnt in range(len(val)): 

        greenHouseInfo = json.loads(requests.get(
            'http://ec2-13-59-136-106.us-east-2.compute.amazonaws.com:2000/greenhouses'#/ABCDEFG/COMMANDS_TOPIC'
            ).text)
        #THRESHOLD_BRIGHT
        status = greenHouseInfo[["GREENHOUSE_ID"]==id]["STATUS_CONTROLL_HUMIDITY"]

        sensor_data = {"humidity" : val[cnt], "battery": batt[cnt] ,"status": status,"id":id}  
        S_cat.sendData(val[cnt],batt[cnt],status,id)
        S_tb.pub_tb(sensor_data)
        time.sleep(1)

    S_cat.end()
    S_tb.unconn()
