from MyMQTT import*
import paho.mqtt.client as mqtt
import string
import time
import random
import numpy as np


class Sensor_h():
    def __init__(self, clientID, topic, broker, port):
        self.client = MyMQTT(clientID, broker, port, None)
        self.topic = topic
        self.__message = {}
    def run(self):
        self.client.start()
    def end(self):
        self.client.stop()
    def sendData(self, hm, batt, status, binar=''):
        message = self.__message
        message["humidity"] = hm
        message["ts"] = time.strftime("%H:%M:%S")
        message["batt"] = batt
        message["status"] = status
        message["bn"] = binar
        self.client.myPublish(self.topic, message)
        print(message)


class TB_Sensor_h():
    def __init__(self, clientID, token, host, topic, broker, port):
        self.clientID = clientID
        self.token = token
        self.host = host
        self.topic = topic
        self.broker = broker
        self.port = port
        self.ccc = mqtt.Client(self.clientID, True)
    def con(self):
        self.ccc.username_pw_set(self.token)
        self.ccc.connect(self.host, self.broker, self.port)
        self.ccc.loop_start()
    def pub_tb(self, msg):
        self.ccc.publish(self.topic, json.dumps(msg))
    def unconn(self):
        self.ccc.loop_stop()
        self.ccc.disconnect()
class Sensor_t():
    def __init__(self, clientID, topic, broker, port):
        self.client = MyMQTT(clientID, broker, port, None)
        self.topic = topic
        self.__message = {}
    def run(self):
        self.client.start()
    def end(self):
        self.client.stop()
    def sendData(self, temp, batt, status, binar=''):
        message = self.__message
        message["temperature"] = temp
        message["ts"] = time.strftime("%H:%M:%S")
        message["batt"] = batt
        message["status"] = status
        message["bn"] = binar
        self.client.myPublish(self.topic, message)
        print(message)


class TB_Sensor_t():
    def __init__(self, clientID, token, host, topic, broker, port):
        self.clientID = clientID
        self.token = token
        self.host = host
        self.topic = topic
        self.broker = broker
        self.port = port
        self.ccc = mqtt.Client(self.clientID, True)
    def con(self):
        self.ccc.username_pw_set(self.token)
        self.ccc.connect(self.host, self.broker, self.port)
        self.ccc.loop_start()
    def pub_tb(self, msg):
        self.ccc.publish(self.topic, json.dumps(msg))
    def unconn(self):
        self.ccc.loop_stop()
        self.ccc.disconnect()


class Sensor_b():
    def __init__(self, clientID, topic, broker, port):
        self.client = MyMQTT(clientID, broker, port, None)
        self.topic = topic
        self.__message = {}
    def run(self):
        self.client.start()
    def end(self):
        self.client.stop()
    def sendData(self, brgth, batt, status, binar=''):
        message = self.__message
        message["brightness"] = brgth
        message["ts"] = time.strftime("%H:%M:%S")
        message["batt"] = batt
        message["status"] = status
        message["bn"] = binar
        self.client.myPublish(self.topic, message)
        print(message)


class TB_Sensor_b():
    def __init__(self, clientID, token, host, topic, broker, port):
        self.clientID = clientID
        self.token = token
        self.host = host
        self.topic = topic
        self.broker = broker
        self.port = port
        self.ccc = mqtt.Client(self.clientID, True)
    def con(self):
        self.ccc.username_pw_set(self.token)
        self.ccc.connect(self.host, self.broker, self.port)
        self.ccc.loop_start()
    def pub_tb(self, msg):
        self.ccc.publish(self.topic, json.dumps(msg))
    def unconn(self):
        self.ccc.loop_stop()
        self.ccc.disconnect()


class Sensor_plant():
    def __init__(self, clientID, topic, broker, port):
        self.client = MyMQTT(clientID, broker, port, None)
        self.topic = topic
        self.__message = {}
    def run(self):
        self.client.start()
    def end(self):
        self.client.stop()
    def sendData(self, hum, temperature, batt, status, binar=''):
        message = self.__message
        message["humidity"] = hum
        message["temperature"] = temperature
        message["ts"] = time.time()
        # message["ts"] = time.strftime("%H:%M:%S")
        message["battery"] = batt
        message["status_pump"] = status
        message["bn"] = binar
        self.client.myPublish(self.topic, message)
        print(message)


class TB_Sensor_plant():
    def __init__(self, clientID, token, host, topic, broker, port):
        self.clientID = clientID
        self.token = token
        self.host = host
        self.topic = topic
        self.broker = broker
        self.port = port
        self.ccc = mqtt.Client(self.clientID, True)
    def con(self):
        self.ccc.username_pw_set(self.token)
        self.ccc.connect(self.host, self.broker, self.port)
        self.ccc.loop_start()
    def pub_tb(self, msg):
        self.ccc.publish(self.topic, json.dumps(msg))
    def unconn(self):
        self.ccc.loop_stop()
        self.ccc.disconnect()

# # if __name__ == "__main__":
# #     minute_x_day = 24*60
# #     lam = 24
# #     val = 35+0.3*np.random.poisson(lam, minute_x_day)
# #     val = np.clip(val, 10, 60)
# #     x = np.arange(0, 3 * np.pi, 0.005)
# #     batt = 40 + 20 * np.sin(x)
# #     batt = np.clip(batt, 0, 100)
# #     conf = json.load(open("settings.json"))
# #     id = random.choice(["84F3EB33D049"])
# #     S_cat = Sensor_h(
# #         id, "/p4iot/greenhouses/{}/sensors".format(id), "127.0.0.1", 1883)
# #     S_tb = TB_Sensor_h(id, 'svOmnwGu4RlAydXbdMHf','demo.thingsboard.io', 'v1/devices/me/telemetry', 1883, 60)
# #     S_tb.con()
# #     S_cat.run()
# #     for cnt in range(len(val)):
# #         sensor_data = {
# #             "humidity": val[cnt], "battery": batt[cnt], "status": random.randint(0, 1)}
# #         S_cat.sendData(val[cnt], batt[cnt], status=random.randint(0, 1))
# #         S_tb.pub_tb(sensor_data)
# #         time.sleep(5)
# #     S_cat.end()
# #     S_tb.unconn()
