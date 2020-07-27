import numpy as np
import pandas as pd
import pickle
from sklearn.preprocessing import MinMaxScaler
import os
import psutil
import wget
import time
import socket
import subprocess as sp
import re
import argparse
import smtplib
import config
import paho.mqtt.client as mqtt

trained = [1, 10, 100, 1003, 1004, 1005, 1006, 1007, 1008, 1009, 101, 1010, 1011, 1012, 1013, 1014, 1015, 1016, 1017, 1018, 1019, 1020, 1021, 1022, 1023, 1024, 1025, 1027, 1028, 1029, 1030, 1031, 1032, 1033, 1034, 1035, 1036, 1037, 1038, 104, 1040, 1041, 1042, 1043, 1044, 1046, 1047, 1049, 105, 1050, 1051, 1053, 1054, 1055, 1056, 1057, 1058, 1059, 1060, 107, 11, 110, 111, 112, 122, 125, 135, 14, 140, 141, 144, 145, 147, 150, 151, 153, 154, 155, 156, 157, 158, 159, 16, 160, 161, 162, 163, 164, 165, 166, 168, 169, 17, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 18, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 19, 190, 191, 193, 194, 195, 196, 198, 199, 2, 200, 204, 208, 21, 216, 22, 223, 224, 225, 230, 231, 235, 236, 24, 246, 247, 25, 252, 253, 256, 260, 261, 265, 266, 272, 277, 282, 288, 29, 292, 293, 296, 3, 300, 31, 315, 316, 317, 318, 32, 329, 333, 337, 339, 34, 342, 344, 345, 348, 349, 350, 353, 355, 356, 357, 36, 364, 367, 368, 370, 372, 376, 377, 380, 39, 41, 410, 420, 431, 432, 434, 435, 44, 440, 441, 442, 45, 454, 455, 457, 466, 47, 471, 474, 475, 48, 480, 485, 49272, 494, 497, 5, 50, 500, 508, 509, 515, 52, 520, 524, 527, 529, 53, 539, 54, 541, 543, 55, 551, 552, 553, 555, 57, 58, 585, 586, 587, 588, 589, 59, 590, 592, 593, 594, 595, 596, 597, 6, 60, 605, 608, 609, 61, 610, 613, 616, 62, 628, 63, 637, 6377, 64, 640, 647, 648, 65, 653, 66, 661, 662, 663, 67, 671, 673, 674, 678, 68, 688, 69, 694, 7, 70, 703, 704, 705, 707, 708, 709, 71, 710, 711, 714, 715, 718, 719, 72, 720, 722, 724, 725, 726, 728, 73, 731, 732, 733, 735, 736, 737, 74, 741, 743, 745, 748, 75, 750, 76, 761, 762, 765, 778, 780, 781, 782, 783, 784, 785, 786, 788, 79, 798, 799, 801, 802, 804, 805, 808, 809, 81, 810, 818, 82, 828, 829, 830, 832, 833, 835, 836, 837, 838, 839, 842, 848, 849, 85, 851, 852, 854, 858, 86, 860, 861, 862, 866, 867, 869, 870, 875, 876, 877, 879, 88, 880, 881, 882, 885, 886, 888, 89, 891, 892, 893, 896, 897, 898, 899, 900, 903, 904, 908, 910, 911, 912, 913, 914, 915, 916, 917, 918, 919, 92, 920, 921, 922, 923, 924, 926, 928, 93, 930, 931, 932, 933, 934, 936, 938, 94, 940, 942, 943, 944, 945, 946, 947, 948, 949, 95, 950, 951, 952, 953, 954, 955, 96, 968, 969, 97, 99, 994]


class Record:
    system = psutil.Process(os.getpid())

    def __init__(self, window_size, title):
        self.data_set = []
        self.window_size = window_size
        self.title = title

    def get_data(self):
        return 1

    def add_data(self):
        data = self.get_data()
        new_avg = self.calculate_mov_avg(data)
        self.check_window_size()
        self.data_set.append(new_avg)

    def check_window_size(self):
        if len(self.data_set) > self.window_size:
            self.data_set.pop(0)

    def calculate_mov_avg(self, a1):
        _count = len(self.data_set)
        if _count == 0:
            avg1 = 0
        else:
            avg1 = self.data_set[-1]
        _count += 1
        avg1 = ((_count - 1) * avg1 + a1) / _count  # cumulative average formula μ_n=((n-1) μ_(n-1)  + x_n)/n
        return round(avg1, 4)


class CPU(Record):
    def get_data(self):
        cpu = psutil.cpu_percent(percpu=False)
        # return round(self.system.cpu_percent(), 4)
        try:
            lst = self.data_set[-1]
        except IndexError:
            lst = psutil.cpu_percent(percpu=False)
        return round(abs(cpu - lst), 4)


class Memory(Record):

    def get_data(self):
        return round(self.system.memory_percent(), 4)


class Delay:
    def __init__(self):
        self.data_set = []

    def add_data(self, data):
        new_avg = self.calculate_mov_avg(data)
        self.data_set.append(new_avg)

    def calculate_mov_avg(self, a1):
        _count = len(self.data_set)
        if _count == 0:
            avg1 = 0
        else:
            avg1 = self.data_set[-1]
        _count += 1
        avg1 = ((_count - 1) * avg1 + a1) / _count  # cumulative average formula μ_n=((n-1) μ_(n-1)  + x_n)/n
        return round(avg1, 4)


class PredictPop:

    def __init__(self):
        self.model_path = 'models'
        self.data_path = 'data'

    @staticmethod
    def get_model(filename):
        # load the model from disk
        loaded_model = pickle.load(open(filename, 'rb'))
        return loaded_model

    @staticmethod
    def predict_next(model, data):
        scaler = MinMaxScaler(feature_range=(0, 1))

        history = np.array(data)
        dataset = scaler.fit_transform(history)
        # Scale the data to be values between 0 and 1
        # scaled_history = scaler.transform(history)
        # Create an empty list
        X_test = [dataset]
        # Convert the X_test data set to a numpy array
        X_test = np.array(X_test)

        X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))

        pred_value = model.predict(X_test)
        # undo the scaling
        pred_value = scaler.inverse_transform(pred_value)
        return pred_value[0][0]

    def process_request(self, request, t_time):
        if request in trained:
            model = self.get_model(f'{self.model_path}/model{request}.sav')
            raw_data = pd.read_csv(f'{self.data_path}/{request}.csv')
            stop = np.where(raw_data['timestamp'] == t_time)[0][-1]
            if stop >= 80:
                data = list(raw_data['rating'].values[stop-80:stop])
                data = [[i] for i in data]
                return self.predict_next(model=model, data=data)
            else:
                print(f'not enough -> {stop}')
        else:
            print(f'not in trained {request}')
        return 0


class LocalCache:
    def __init__(self, cache_size, delay):
        self.cache = {}
        self.cache_size = cache_size
        self.hit = 0
        self.miss = 0
        self.predictor = PredictPop()
        self.cache_dir = 'cache'
        self.delay = delay

    @staticmethod
    def web_page(request):
        return f"https://competent-euler-834b51.netlify.app/pages/{request}.html"

    def get_file(self, request, temp=0):
        start = time.perf_counter()
        if temp == 1:
            wget.download(self.web_page(request), f'temp/{request}.html')
        else:
            wget.download(self.web_page(request), f'{self.cache_dir}/{request}.html')
        cost = time.perf_counter() - start
        self.delay.add_data(round(cost, 5))

    def push(self, request, t_time):
        if request in self.cache:
            print('hit')
            self.hit += 1
            self.delay.add_data(0)
            popularity = self.predictor.process_request(request, t_time)
            self.cache[request] = popularity
        else:
            print('miss')
            self.miss += 1
            popularity = self.predictor.process_request(request, t_time)
            if len(self.cache) >= self.cache_size:
                min_pop_cache = min(self.cache, key=self.cache.get)
                if self.cache[min_pop_cache] <= popularity:
                    self.evict(min_pop_cache)
                    print(f'replaced {min_pop_cache}')
                    # fetch data
                    self.get_file(request)
                    self.cache[request] = popularity
                else:
                    self.get_file(request, temp=1)
                    print(f'less popularity| min: {self.cache[min_pop_cache]}, req: {popularity}')
            else:
                # fetch data
                self.get_file(request)
                self.cache[request] = popularity

    def evict(self, victim):
        self.cache.pop(victim)
        os.system(f'rm cache/{victim}.html')

    def hit_ratio(self):
        return round((self.hit / (self.hit + self.miss)) * 100, 2)


def ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]


def get_hostname():
    cmd = ['cat /etc/hostname']
    hostname = str(sp.check_output(cmd, shell=True), 'utf-8')[0:-1]
    return hostname


def data_slice(no_mec, total_req_no, initial):
    host = get_hostname()
    host_no = int(re.findall('[0-9]+', host)[0])
    step = int(total_req_no/no_mec)
    start = host_no*step
    return start+initial, start+step+initial


def send_email(msg):
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com')
        server.ehlo()
        server.login(config.email_address, config.password)
        subject = 'Deadlock results {} {}'.format('LSTM caching', get_hostname())
        # msg = 'Attendance done for {}'.format(_timer)
        _message = 'Subject: {}\n\n{}\n\n SENT BY RIHANNA \n\n'.format(subject, msg)
        server.sendmail(config.email_address, config.send_email, _message)
        server.quit()
        print("Email sent!")
    except Exception as e:
        print(e)


def save_data(mem, cpu, delay, hit_ratio, no):
    host = get_hostname()
    host_no = int(re.findall('[0-9]+', host)[0])
    data = f"""
    mem{host_no}_{no} = {mem}
    cpu{host_no}_{no} = {cpu}
    delay{host_no}_{no} = {delay}
    hit_ratio{host_no}_{no} = {hit_ratio}
    """
    send_email(data)
    file = open(f'results/output{host_no}_{no}.py', 'w')
    file.write(data)
    file.close()
    send_path = '/home/osboxes/results/'
    sp.run(
        ["scp", f'results/output{host_no}_{no}.py', f"osboxes@192.168.200.100:{send_path}"])


def arrival_distribution():
    # Poisson Distribution
    host = get_hostname()
    host_no = int(re.findall('[0-9]+', host)[0])
    arrival_dist = pickle.load(open(f'dist/{host_no}.pickle', 'rb'))
    return (i for i in arrival_dist)


class BrokerRequest:
    def __init__(self, user, pw, ip, sub_topic):
        self.user = user
        self.pw = pw
        self.ip = ip
        self.port = 1883
        self.topic = sub_topic
        self.response = None
        self.client = mqtt.Client()

    def on_connect(self, connect_client, userdata, flags, rc):
        print("Connected with Code :" + str(rc))
        # Subscribe Topic from here
        connect_client.subscribe(self.topic)

    def on_message(self, message_client, userdata, msg):
        if pickle.loads(msg.payload):
            self.response = pickle.loads(msg.payload)

    def broker_loop(self):
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.client.username_pw_set(self.user, self.pw)
        self.client.connect(self.ip, self.port, 60)
        self.client.loop_start()
        while True:
            if self.response:
                self.client.loop_stop()
                self.client.disconnect()
                return self.response

    def __del__(self):
        print('BrokerRequest Object Deleted!')


def initialization():
    br = BrokerRequest(user='mec', pw='password', ip='192.168.200.100', sub_topic='control')
    br.broker_loop()
    del br
    print('starting ....')


def run(no_mec):
    os.system('clear')
    print('Waiting for Start command from Control...')
    initialization()
    request_data = pd.read_csv(f'../request_data.csv')
    no_reqs = int(request_data.shape[0] * 0.3)  # testing data is 30 % => 67,259
    n = 150
    no_of_requests = (no_reqs // n) * n        # No of requests should be divisible by 5, 10, 15 MECs |  67,200

    cpu = CPU(window_size=1000, title='cpu')
    memory = Memory(window_size=1000, title='memory')
    network_cost_record = Delay()

    d_slice = data_slice(no_mec=no_mec, total_req_no=no_of_requests, initial=request_data.shape[0]-no_of_requests)
    store = LocalCache(cache_size=100, delay=network_cost_record)
    # pickle_in = open('dict.pickle','rb')
    # example_dict = pickle.load(pickle_in)
    arrival_dist = arrival_distribution()
    for i in range(d_slice[0], d_slice[1]):
        print(f"requesting-> {request_data['movieId'][i]}")
        store.push(request_data['movieId'][i], request_data['timestamp'][i])
        cpu.get_data()
        memory.get_data()
        print(f'cache -> {store.cache}')
        time.sleep(arrival_dist.__next__())
    print('hit ratio ->', store.hit_ratio())
    save_data(mem=memory.data_set, cpu=cpu.data_set, delay=network_cost_record.data_set,
              hit_ratio=store.hit_ratio(), no=no_mec)


def main():
    parser = argparse.ArgumentParser()   # --n=5
    parser.add_argument('--n', type=int, default=1, help='Number of MEC nodes')
    args = parser.parse_args()

    run(no_mec=args.n)


if __name__ == '__main__':
    main()
