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
    val_h = 15+0.3*np.random.poisson(lam, time_alive) 
    val_h = np.clip(val_h, 10, 60)

    val_t = 25+0.3*np.random.poisson(lam, time_alive) 
    val_t = np.clip(val_t, 10, 60)
    
    
    x = np.arange(0, 3 * np.pi, 0.000005)
    batt = 40 + 20* np.sin(x)
    batt = np.round(batt, 2)
    batt = np.clip(batt, 0, 100)

    # Configuration for MQTT

    conf=json.load(open("settings.json"))
    # id_="84F3EB33DB49"
    id_="8888EB33DB49"
    S_cat_h=Sensor_h(id,"/p4iot/plants/{}/sensors".format(id),"13.59.136.106", 1883)
    S_tb_h = TB_Sensor_h(id,'FgbOm7jGYMFUENoeISR0','demo.thingsboard.io','v1/devices/me/telemetry',1883,60)
    
    
    S_cat_t=Sensor_t(id,"/p4iot/plants/{}/sensors".format(id),"13.59.136.106", 1883)
    S_tb_t = TB_Sensor_t(id,'FgbOm7jGYMFUENoeISR0','demo.thingsboard.io','v1/devices/me/telemetry',1883,60)
    
    

    S_cat_h.run()   
    S_cat_t.run() 
    
    S_tb_h.con()
    S_tb_t.con()
    
    for cnt in range(len(val_h)): 

        plantInfo = json.loads(requests.get(
            'http://ec2-13-59-136-106.us-east-2.compute.amazonaws.com:2000/plants'
            ).text)

        status_h = plantInfo[["PLANT_ID"]==id]["STATUS_PUMP"]
        # status_t = plantInfo[["PLANT_ID"]==id]["STATUS_PUMP"]

        sensor_data_h = {"humidity" : val_h[cnt], "battery": batt[cnt] ,"status_h": status_h} 
        sensor_data_t = {"temperature" : val_t[cnt], "battery": batt[cnt] } #,"status_t": status_t

        S_cat_h.sendData(val_h[cnt],batt[cnt],status_h)
        S_cat_t.sendData(val_t[cnt],batt[cnt])#,status_t)

        S_tb_h.pub_tb(sensor_data_h)
        S_tb_t.pub_tb(sensor_data_t)
                
        # print(f"Temperature: {val_h[cnt]}   battery: {batt[cnt]}    by: {id}")
        time.sleep(1)

    S_cat_h.end()
    S_cat_t.end()

    S_tb_h.unconn()
    S_tb_t.unconn()