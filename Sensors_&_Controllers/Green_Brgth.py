from MyMQTT import*
from Emulated_sensors import Sensor_b, TB_Sensor_b
# import paho.mqtt.client as mqtt
import time
import random
import numpy as np


if __name__=="__main__":

    # Simulated Value
    minute_x_day = 24*60
    lam = 24
    val = 35+0.3*np.random.poisson(lam, minute_x_day) 
    val = np.clip(val, 10, 60)

    x = np.arange(0, 3 * np.pi, 0.005)
    batt = 40 + 20* np.sin(x)
    batt = np.clip(batt, 0, 100)

    # Configuration for MQTT

    conf=json.load(open("settings.json"))
    id=random.choice(["84F3EB33D049"])#,"aAAAAAAAAAAA"])
    S_cat=Sensor_b(id,"/p4iot/greenhouses/{}/sensors".format(id),"127.0.0.1", 1883)
    S_tb = TB_Sensor_b(id,'Wsx4vSU7SCBUPqH4BRN6','demo.thingsboard.io','v1/devices/me/telemetry',1883,60)
    
    S_cat.run()    
    S_tb.con()

    for cnt in range(len(val)): 
        with open('Catalog.json') as cat:
            data = json.load(cat)
            greenHouseInfo= data['Greenhouses']
            #THRESHOLD_BRIGHT
            status = greenHouseInfo[0]["STATUS_CONTROLL_BRIGTH"]

        sensor_data = {"humidity" : val[cnt], "battery": batt[cnt] ,"status": status}  
        S_cat.sendData(val[cnt],batt[cnt],status)
        S_tb.pub_tb(sensor_data)
        
        # print(f"Temperature: {val[cnt]}   battery: {batt[cnt]}    by: {id}")
        time.sleep(5)

    S_cat.end()
    S_tb.unconn()
