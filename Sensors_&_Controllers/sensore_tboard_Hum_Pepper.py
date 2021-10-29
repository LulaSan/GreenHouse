from datetime import time
import time
import sys
import paho.mqtt.client as mqtt
import json
import random
import numpy as np

TB_HOST = 'thingsboard.cloud'
ACCESS_TOKEN = 'svOmnwGu4RlAydXbdMHf'
sensor_data = {"humidity" : 0,"battery" : 0}#"status" : 0
client = mqtt.Client()
client.username_pw_set(ACCESS_TOKEN)
client.connect(TB_HOST,1883,60)
client.loop_start()


minute_x_day = 24*60
loc, scale = 10, 8

hum= np.random.logistic(loc, scale,minute_x_day)

x = np.arange(0, 3 * np.pi, 0.005) # create x array of angels from range 0 to 3*3.14
batt_hum = 60 +  np.sin(x)*100
''''status_hum = random.randrange(0,2)'''

thr = 5/100
for cnt in range(len(hum)):
    
    if hum[cnt] < 0:
        hum[cnt] = 0
    elif hum[cnt] > 50:
        hum[cnt] = 50 

    if cnt >=1 and cnt<= len(hum)-2:
        if hum[cnt]< (hum[cnt-1]-(hum[cnt-1]*thr)) or hum[cnt]>(hum[cnt+1]+((hum[cnt+1]*thr))):
            hum[cnt] = ((hum[cnt-1]+(hum[cnt+1])/2))
    
    if hum[cnt] < 4:
        hum[cnt] = 5
    elif hum[cnt] > 50:
        hum[cnt] = 50 



for cnt in range(len(hum)):
    val = hum[cnt]
    btt = batt_hum[cnt]
    
    print(val)
    print(btt)
    
    
    sensor_data['humidity']= val
    sensor_data['battery']= btt
    
    
    client.publish('v1/devices/me/telemetry',json.dumps(sensor_data))
    time.sleep(3)

client.loop_stop()
client.disconnect()
