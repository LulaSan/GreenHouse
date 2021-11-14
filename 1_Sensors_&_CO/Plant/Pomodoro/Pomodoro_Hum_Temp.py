from MyMQTT import*
from Emulated_sensors import *
# import paho.mqtt.client as mqtt
import time
import random
import numpy as np
import requests


if __name__=="__main__":

    # Simulated val_hue
    time_alive = 24*60*1000
    lam = 24
    val_h = 20+0.7*np.random.poisson(lam, time_alive) 
    val_h = np.clip(val_h, 10, 60)
    
    val_t = 25+0.3*np.random.poisson(lam, time_alive) 
    val_t = np.clip(val_t, 10, 60)

    x = np.arange(0, 3 * np.pi, 0.005)
    batt = 40 + 20* np.sin(x)
    batt = np.clip(batt, 0, 100)

    # Configuration for MQTT

    # conf=json.load(open("settings.json"))
    id="84F3EB33DB49"
    
    S_db=Sensor_plant(id,"/p4iot/plants/{}/sensors_pomo".format(id),"13.59.136.106", 1883)
    S_tb = TB_Sensor_plant(id,'FgbOm7jGYMFUENoeISR0','demo.thingsboard.io','v1/devices/me/telemetry',1883,60)
    print("Subscriber connected to: /p4iot/plants/{}/sensors_pomo".format(id))


    S_db.run()      
    S_tb.con()
    
    for cnt in range(len(val_h)):
        plantInfo = json.loads(requests.get(
        'http://ec2-13-59-136-106.us-east-2.compute.amazonaws.com:2000/plants'
        ).text)
        
        status_h = plantInfo[["PLANT_ID"]==id]["STATUS_PUMP"]
        
        sensor_data = {"humidity" : val_h[cnt], "temperature": val_t[cnt], "battery": batt[cnt] ,"status_pump": status_h}  
        S_db.sendData(val_h[cnt],val_t[cnt],batt[cnt],status=status_h,binar=id)
        S_tb.pub_tb(sensor_data)
        time.sleep(1)

    S_db.end()

    S_tb.unconn()