import paho.mqtt.client as PahoMQTT
import time
import json


class Subscriber_get_info_t:
		def __init__(self, clientID,topic,broker,brokerPort):
			self.clientID = clientID
			# create an instance of paho.mqtt.client
			self._paho_mqtt = PahoMQTT.Client(clientID, False)

			# register the callback
			self._paho_mqtt.on_connect = self.myOnConnect
			self._paho_mqtt.on_message = self.myOnMessageReceived

			self.topic = topic
			self.messageBroker = broker
			self.messageBrokerPort = brokerPort
		def start (self):
			#manage connection to broker
			self._paho_mqtt.connect(self.messageBroker, self.messageBrokerPort)
			self._paho_mqtt.loop_start()
			# subscribe for a topic
			self._paho_mqtt.subscribe(self.topic, 2)

		def stop (self):
			self._paho_mqtt.unsubscribe(self.topic)
			self._paho_mqtt.loop_stop()
			self._paho_mqtt.disconnect()

		def myOnConnect (self, paho_mqtt, userdata, flags, rc):
			print ("Connected to %s with result code: %d" % (self.messageBroker, rc))

		def myOnMessageReceived (self, paho_mqtt , userdata, msg):
			# A new message is received
			# print ("Topic:'" + msg.topic+"', QoS: '"+str(msg.qos)+"' Message: '"+str(msg.payload) + "'")
			payload=json.loads(msg.payload)
			if payload["temperature"] in payload:	
				# self.temperature = payload["temperature"]
				# self.brightness = payload["brightness"]
				self.temperature = payload["temperature"]
				# print(self.temperature)
				print(payload)
				self.flag = self.temperature
			else:
				self.flag = {"temperature" : 0}

			# print(self.temperature)
			# print(self.humidity)
			# print(self.brightness)

		def myT(self):
			if self.flag == {"temperature" : 0}:
				t= float(self.flag)
			else:
				t= float(self.temperature)
				# print(t)
				return t

		# def myB(self):
		# 	b= (self.brightness)
		# 	return b

		# def myH(self):
		# 	h= (self.humidity)
		# 	return h

		# print(temperature)
###################################################
			# return temperature
#######################################################

if __name__ == "__main__":
    sub_get_info = Subscriber_get_info_t("controller_temp",'/p4iot/greenhouses/84F3EB33D049/temperature', '13.59.136.106', 1883)
    sub_get_info.start ()
    # temper = sub_get_info.myOnMessageReceived( paho_mqtt , userdata, msg)
    # print()

    a = 0
    while (a < 30):
        a += 1
        time.sleep(1)
        t = sub_get_info.myH()

        print(t)
    sub_get_info.stop()