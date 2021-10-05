import pickle
import paho.mqtt.client as mqtt
from threading import Thread
import time

broker_ip = input('Enter Broker ip: ')
broker_dict = {'user': 'mec', 'pw': 'password', 'sub_topic': 'control', 'ip': broker_ip}


class BrokerCom:
    def __init__(self, user, pw, ip, sub_topic):
        self.user = user
        self.pw = pw
        self.ip = ip
        self.port = 1883
        self.topic = sub_topic
        self.client = mqtt.Client()
        self.stopped = []
        self.run = 1

    def on_connect(self, connect_client, userdata, flags, rc):
        print("Connected with Code :" + str(rc))
        # Subscribe Topic from here
        connect_client.subscribe(self.topic)

    def on_message(self, message_client, userdata, msg):
        data = pickle.loads(msg.payload)     # ['start', []], ['stop': id]
        if (data[0] == 'stop') and (data[1] not in self.stopped):
            self.stopped.append(data[1])
            print(f'{data[1]} has stopped!')

    def publish(self, topic, data):
        self.client.publish(topic, data)

    def broker_loop(self):
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.client.username_pw_set(self.user, self.pw)
        self.client.connect(self.ip, self.port, 60)
        self.client.loop_start()
        while True:
            if self.run == 0:
                self.client.loop_stop()
                self.client.disconnect()
                break

    def __del__(self):
        print('Broker Communication Object Deleted!')


def publish():
    input('start> ')
    messenger.publish(topic=broker_dict['sub_topic'], data=pickle.dumps(['start', {1, 2, 3}]))
    print('published')


def exp_control():
    global messenger

    messenger = BrokerCom(**broker_dict)
    h1 = Thread(target=messenger.broker_loop)
    h1.start()
    time.sleep(1)
    while True:
        try:
            publish()
        except KeyboardInterrupt:
            print('terminated')
            messenger.run = 0
            break


if __name__ == '__main__':
    exp_control()
