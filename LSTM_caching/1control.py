import paho.mqtt.client as mqtt
import pickle


class BrokerSend:
    def __init__(self, user, pw, ip, sub_topic, data):
        self.user = user
        self.pw = pw
        self.ip = ip
        self.port = 1883
        self.topic = sub_topic
        self.client = mqtt.Client()
        self.client.username_pw_set(self.user, self.pw)
        self.client.connect(self.ip, self.port, 60)
        self.data = data

    def publish(self):
        self.client.publish(self.topic, self.data)

    def __del__(self):
        print('BrokerSend Object Deleted!')


def exp_control():
    data = pickle.dumps('start')
    broker_dict = {'user': 'mec', 'pw': 'password', 'sub_topic': 'control', 'ip': 'localhost', 'data': data}
    BrokerSend(**broker_dict).publish()


exp_control()
