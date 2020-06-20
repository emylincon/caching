import pickle
import paho.mqtt.client as mqtt
from threading import Thread
import time


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


def exp_control():
    it = input('MEC Iterations(5 10 15): ')
    broker_dict = {'user': 'mec', 'pw': 'password', 'sub_topic': 'cache/control', 'ip': 'localhost'}
    if it == '':
        exp_no = [5, 10, 15]
    else:
        exp_no = [int(i) for i in it.split()]
    input('start: ')
    messenger = BrokerCom(**broker_dict)
    h1 = Thread(target=messenger.broker_loop)
    h1.start()
    for mec_no in exp_no:
        messenger.publish(topic=broker_dict['topic'], data=pickle.dumps(['start', [i for i in range(mec_no)], mec_no]))
        print(f'Experiment {mec_no} has commenced!')
        while len(messenger.stopped) != mec_no:
            time.sleep(10)
        messenger.stopped = []
        print(f'Experiment {mec_no} is concluded!')
        print('Waiting for 60 seconds Time Lapse!')
        time.sleep(60)
    messenger.run = 0


if __name__ == '__main__':
    exp_control()
