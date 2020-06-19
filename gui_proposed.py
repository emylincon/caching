import matplotlib
import ping_code as pc
from threading import Thread
import threading
import pandas as pd
import time
import os
import json
import requests
import hashlib
from mlxtend.frequent_patterns import apriori
from mlxtend.frequent_patterns import association_rules
import socket
import subprocess as sp
import paramiko
import pickle
import paho.mqtt.client as mqtt
import re
import psutil
from drawnow import *
import matplotlib.pyplot as plt

shared_resource_lock = threading.Lock()
matplotlib.use('TkAgg')
# plt.ion()

fig = plt.figure()
ax1 = fig.add_subplot(231)
ax2 = fig.add_subplot(232)
ax3 = fig.add_subplot(233)
ax4 = fig.add_subplot(234)
ax5 = fig.add_subplot(235)
ax6 = fig.add_subplot(236)


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

    def plot_data(self, ax, col):
        ax.grid(True)
        ax.plot(list(range(len(self.data_set))), self.data_set, linewidth=2, label=self.title, color=col)
        ax.set_ylabel(self.title)
        ax.set_xlabel('Time (seconds)')
        ax.fill_between(list(range(len(self.data_set))), self.data_set, 0, alpha=0.5, color=col)
        ax.legend()
        ax.set_title(f'{self.title} Utilization over Time')
        plt.subplot(ax)


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


class MecDelay:
    def __init__(self, window_size):
        self.delays = {}  # {mec: []}
        self.window_size = window_size
        self.my_ip = ip_address()

    def add_mec(self, mec):
        if (mec not in self.delays) and (mec != self.my_ip):
            shared_resource_lock.acquire()
            self.delays[mec] = [self.get_delay(mec)]
            shared_resource_lock.release()

    def get_delay(self, mec):
        rtt = pc.verbose_ping(mec)
        if rtt:
            return round(rtt, 4)
        else:
            return self.get_delay(mec)

    def add_delay(self):  # call this on a while loop
        shared_resource_lock.acquire()
        for mec in self.delays:
            delay = self.get_delay(mec)
            avg_delay = self.calculate_mov_avg(self.delays[mec], delay)
            self.check_window_size(mec)
            self.delays[mec].append(avg_delay)
        shared_resource_lock.release()

    def check_window_size(self, mec):
        if len(self.delays[mec]) > self.window_size:
            self.delays[mec].pop(0)

    @staticmethod
    def calculate_mov_avg(ma1, a1):
        _count = len(ma1)
        avg1 = ma1[-1]
        _count += 1
        avg1 = ((_count - 1) * avg1 + a1) / _count  # cumulative average formula μ_n=((n-1) μ_(n-1)  + x_n)/n
        return round(avg1, 4)

    def plot_data(self, ax):
        style1 = [{'color': 'g', 'marker': '^'}, {'color': 'aqua', 'marker': '*'}, {'color': 'purple', 'marker': 'X'},
                  {'color': 'r', 'marker': 'v'}, {'color': 'k', 'marker': '>'}, {'color': 'brown', 'marker': 'D'},
                  {'color': 'b', 'marker': 's'}, {'color': 'c', 'marker': '1'}, {'color': 'olive', 'marker': 'p'}, ]
        hosts = list(self.delays)
        ax.grid(True)
        for i in self.delays:
            mv = self.delays[i][:]
            pt = mv[0:len(mv):int((len(mv) / 7)) + 1]
            if pt[-1] != mv[-1]:
                pt.append(mv[-1])
            d = list(range(len(mv)))
            ptx = d[0:len(d):int((len(d) / 7)) + 1]
            if ptx[-1] != d[-1]:
                ptx.append(d[-1])
            if len(ptx) > len(pt):
                ptx = ptx[:-1]
            elif len(ptx) < len(pt):
                pt = pt[:-1]
            ax.plot(ptx,
                    pt,
                    **style1[hosts.index(i)],
                    linestyle=(0, (3, 1, 1, 1, 1, 1)),
                    linewidth=2,
                    label=i)
        ax.set_title('RTT Utilization over Time')
        ax.set_ylabel('Moving RTT')
        ax.legend()
        plt.subplot(ax)


class MecCache:
    def __init__(self):
        self.nodes = set()
        self.cache_store = {}  # {cache_id: {mec1, mec2}, ..}

    def add_cache(self, cache_content_hash, mec):  # multi-cast from mec
        if mec not in self.nodes:
            self.nodes.add(mec)
            mec_rtt.add_mec(mec)
        if cache_content_hash in self.cache_store:
            self.cache_store[cache_content_hash].add(mec)
        else:
            self.cache_store[cache_content_hash] = {mec}

    def find_cache(self, cache_content_hash):
        def get_min_delay_mec(mec_list):
            min_dict = {i: mec_rtt.delays[i][-1] for i in mec_list}
            return min(min_dict, key=min_dict.get)

        if cache_content_hash in self.cache_store:
            n_nodes = self.cache_store[cache_content_hash]
            if len(n_nodes) > 1:
                return get_min_delay_mec(n_nodes)
            elif len(n_nodes) == 1:
                return list(n_nodes)[-1]
        return None

    def replace(self, mec, old_cache, new_cache):  # multi-cast from mec
        if mec in self.cache_store[old_cache]:
            self.cache_store[old_cache].remove(mec)
            if len(self.cache_store[old_cache]) == 0:
                del self.cache_store[old_cache]
        self.add_cache(new_cache, mec)


class LocalCache:
    def __init__(self, cache_size, window_size, content_name_server):
        self.content_name_server = content_name_server
        self.cache_size = cache_size
        self.hit = 0
        self.mec_hit = 0
        self.miss = 0
        self.req = []
        self.cache_dir = 'cache'
        self.req_window = window_size ** 2
        self.window_size = window_size
        self.cache_store = {}
        self.cache_history = {}  # id : {'steps': 1, 'freq':1}
        self.hash_dns = {'all': [], 'window': 600}  # {location_hash: content_hash}
        self.to_delete = ['test']
        self.pre_cached = 0
        self.rule_matches = {'match': [], 'right': 0, 'wrong': 0, 'rules': {}, 'window_count': 0,
                             'window_size': int(self.window_size / 2)}

    def get_json_data(self, endpoint, send=None):
        url = f'http://{self.content_name_server}/'
        if send:
            response = requests.post(url + endpoint, json=json.dumps(send))
        else:
            response = requests.get(url + endpoint)
        data = json.loads(response.content)
        return data

    @staticmethod
    def get_data(url):
        response = requests.get(url)
        data = response.text
        return data

    @staticmethod
    def get_hash(content):
        y = str.encode(content)
        ha = hashlib.sha256(y)
        hash_no = ha.hexdigest()
        return hash_no

    def add_hash_dns(self, content_hash, url, location_hash=None):
        if location_hash and (location_hash not in self.hash_dns):
            if len(self.hash_dns) > self.hash_dns['window']:
                del self.hash_dns[self.hash_dns['all'].pop(0)]
            self.hash_dns[location_hash] = content_hash
            self.hash_dns[content_hash] = url
            self.hash_dns['all'].append(location_hash)
            self.hash_dns['all'].append(content_hash)
        elif content_hash not in self.hash_dns:
            if len(self.hash_dns) > self.hash_dns['window']:
                del self.hash_dns[self.hash_dns['all'].pop(0)]
            self.hash_dns[content_hash] = url
            self.hash_dns['all'].append(content_hash)

    def get_content_hash(self, location_hash, url):
        if location_hash in self.hash_dns:
            self.hash_dns['all'].remove(location_hash)
            self.hash_dns['all'].append(location_hash)
            return self.hash_dns[location_hash]
        else:
            content_hash = self.get_json_data(endpoint=f'read/hash/{location_hash}')
            if content_hash['hash']:
                self.add_hash_dns(location_hash=location_hash, content_hash=content_hash['hash'], url=url)
                return content_hash['hash']
            else:
                return None

    def get_hash_url(self, content_hash):
        if content_hash in self.hash_dns:
            self.hash_dns['all'].remove(content_hash)
            self.hash_dns['all'].append(content_hash)
            return self.hash_dns[content_hash]
        else:
            url = self.get_json_data(endpoint=f'read/url/{content_hash}')['url']
            if url:
                self.add_hash_dns(content_hash=content_hash, url=url)
                return url
            else:
                return None

    def association_match_count(self, req):
        if len(self.rule_matches['match']) != 0:
            if req in self.rule_matches['match']:
                self.rule_matches['right'] += 1
            else:
                self.rule_matches['wrong'] += 1
            self.rule_matches['match'] = []

    def request(self, url):
        location_hash = self.get_hash(url)
        content_hash = self.get_content_hash(location_hash=location_hash, url=url)
        if content_hash and (content_hash in self.cache_store):
            self.cache_hit(content_hash)
        elif not content_hash:
            self.cache_miss(location_id=location_hash, url=url, add_content_hash=1)
        else:
            self.cache_miss(location_id=location_hash, content_hash=content_hash, url=url, add_content_hash=0)
        if content_hash:
            self.add_req_to_list(content_hash)
            self.association_match_count(content_hash)
        else:
            content_hash = self.get_content_hash(location_hash=location_hash, url=url)
            self.add_req_to_list(content_hash)
            self.association_match_count(content_hash)
        if self.rule_matches['window_count'] == self.rule_matches['window_size']:
            self.check_association()
            self.rule_matches['window_count'] = 0
        else:
            self.rule_matches['window_count'] += 1

    @staticmethod
    def display_data(kind, content_hash=None, data=None):
        print('\n' + ('*' * 100))
        print(f'Type : {kind}')
        print('-' * 100)
        if content_hash:
            os.system(f'cat cache/{content_hash}')
        else:
            print(data)
        print('\n' + ('*' * 100) + '\n')

    def cache_hit(self, content_hash):
        self.hit += 1
        self.cache_history[content_hash][0] += 1  # increase frequency
        self.cache_history[content_hash][1] = time.time()  # reinitialise history
        self.display_data(content_hash=content_hash, kind='Hit')

    def cache_miss(self, location_id, add_content_hash, content_hash=None, url=None):
        cache_obtained = 0  # checks if cache has been obtained
        if content_hash:
            node = mec_cache.find_cache(content_hash)
            if node:
                cache = self.fetch_from_mec(hash_no=content_hash, host_ip=node)
                cache_obtained = 1
                self.miss_decision(content_hash, cache)
                self.mec_hit += 1
                self.display_data(data=cache, kind='MEC Hit')

        if url and (cache_obtained == 0):
            self.miss += 1
            cache = self.get_data(url)
            con_hash = self.get_hash(cache)
            self.miss_decision(con_hash, cache)
            self.display_data(data=cache, kind='Miss')
            if add_content_hash == 1:
                self.get_json_data(endpoint='add/', send=[location_id, con_hash, url])  # add to dns chain
                self.add_hash_dns(location_hash=location_id, content_hash=con_hash, url=url)

    def miss_decision(self, hash_no, data):
        if self.is_cache_full():
            cache_decision = self.replace(hash_no)
            if cache_decision == 1:
                self.cache_data(hash_no, data, pub=0)
        else:
            self.cache_data(hash_no, data)  # caches data
            self.cache_store[hash_no] = 0  # adds to cache store
            self.cache_history[hash_no] = [1,
                                           time.time()]
            # if cache is not full and there is a miss, cache wont be in history

    @staticmethod
    def fetch_from_mec(hash_no, host_ip):
        c = paramiko.SSHClient()
        un = 'mec'
        pw = 'password'
        port = 22

        c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        c.connect(host_ip, port, un, pw)
        cmd = 'cat /home/mec/caching/cache/{}'.format(hash_no)
        stdin, stdout, stderr = c.exec_command(cmd)
        data = ''
        for line in stdout:
            data += line
        return data

    def cache_data(self, content_hash, data, pub=1):
        file = open(f'{self.cache_dir}/{content_hash}', 'w')
        file.write(data)
        file.close()
        if pub == 1:
            messenger.publish('cache/add', pickle.dumps([content_hash, ip_address()]))  # [cache_content_hash, mec]

    def remove_cache(self, content_hash, replace):
        messenger.publish('cache/replace',
                          pickle.dumps([ip_address(), replace, content_hash]))  # [mec, old_cache, new_cache]
        del self.cache_store[replace]
        self.to_delete.append(replace)  # scheduling delete
        try:
            victim = self.to_delete.pop(0)
            os.remove(f'{self.cache_dir}/{victim}')
        except FileNotFoundError:
            print('cannot delete \nFileNotFound')

    def add_req_to_list(self, cache):
        self.window_check()
        self.req.append(cache)

    def window_check(self):
        if len(self.req) > self.req_window:
            self.req.pop(0)

    def is_cache_full(self):
        if len(self.cache_store) >= self.cache_size:
            return True
        else:
            return False

    def get_victim(self):
        self.cache_store = {i: self.cache_history[i] for i in self.cache_store}
        victim = sorted(self.cache_store.items(), key=lambda e: (e[1][0], e[1][1]))[0][0]  # replace min freq,history
        return victim

    def replace(self, cache_hash):
        cache_decision = 0  # 0 means don't cache, 1 means cache
        if cache_hash in self.cache_history:  # cache only if its in history
            replace = self.get_victim()
            if self.cache_history[cache_hash][1] > self.cache_history[replace][1]:
                # replace only if it has occurred more recently than the victim
                self.remove_cache(cache_hash, replace)
                self.cache_store[cache_hash] = 0
                d = f'scores: {self.cache_history} | {replace} replaced'
                self.display_me(header='Replace', data=d)
                cache_decision = 1
            self.cache_history[cache_hash][0] += 1
            self.cache_history[cache_hash][1] = time.time()  # reinitialise history
            self.display_me(header='Replace', data=f'Not replaced \nNot cached {cache_hash}')
        else:
            self.cache_history[cache_hash] = [1, time.time()]  # initialize

        return cache_decision

    def pre_cache(self, cache_hash):
        if cache_hash not in self.cache_store:
            node = mec_cache.find_cache(cache_hash)
            if node:
                cache = self.fetch_from_mec(hash_no=cache_hash, host_ip=node)
            else:
                url = self.get_hash_url(content_hash=cache_hash)
                cache = self.get_data(url=url)
            if self.is_cache_full():
                replace = self.get_victim()
                self.remove_cache(cache_hash, replace)
            self.cache_store[cache_hash] = 0
            self.cache_data(cache_hash, cache, pub=0)
            self.display_me(header='Association Pre-cache', data=f'Pre-cached {cache_hash}')
            self.pre_cached += 1
        else:
            self.display_me(header='Association Pre-cache', data=f'Already in Store {cache_hash}')

    def apply_association(self, rules):
        match = 0
        for association in rules:  # rules = [[[1,2], [2]], [[1,2], [2]]]
            self.rule_matches['rules'][tuple(association[0])] = association[1]
            if self.req[-len(association[0]):] == association[0]:
                self.display_me(header=f'Association Match {match + 1}', data=association)
                self.rule_matches['match'] += association[1]
                for i in association[1]:
                    self.pre_cache(i)
                    match += 1

        if match == 0:
            print('No Association Match!')

    @staticmethod
    def display_me(header, data):
        print('\n' + '*' * 100)
        print(f'header : {header}')
        print('-' * 100)
        print(data)
        print('\n' + '*' * 100 + '\n')

    def check_association(self):
        if len(self.req) >= self.window_size:
            group_no = len(set(self.req[-self.window_size:]))
            data_len = group_no ** 2
            if len(self.req) >= data_len:
                data = self.req[-data_len:]
                print(f'Generating Association rules for data {group_no}x{len(data)}')
                t1 = time.time()
                rules = AssociateCache(data=data, rule_no=6, group_no=group_no).gen_rules()
                t2 = time.time()
                self.display_me(header=f'Association Rules | Time: {round(t2-t1, 5)}', data=rules)
                self.apply_association(rules=rules)

    def plot_association_accuracy(self, ax):
        explode = []
        val = [self.rule_matches['right'], self.rule_matches['wrong']]
        for i in val:
            if i == max(val):
                explode.append(0.1)
            else:
                explode.append(0)

        ax.pie(val, autopct='%1.1f%%', shadow=True, explode=explode, colors=['g', 'r'])
        ax.set_title('Association Prediction')
        plt.subplot(ax)

    def plot_association(self, ax):
        data = list(self.rule_matches['rules'].items())[-6:]
        if len(data) != 0:
            legend_control = 0
            for i in range(len(data)):
                ant_name = data[i][0]
                if type(ant_name).__name__ == 'str':
                    ant_name = [ant_name]
                ant = range(len(ant_name))
                con_name = data[i][1]
                if type(con_name).__name__ == 'str':
                    con_name = [con_name]
                con = range(len(ant_name), len(con_name) + len(ant_name))
                con1 = range(len(ant_name) - 1, len(con_name) + len(ant_name))
                if legend_control == 0:
                    ax.plot(con1, [i for _ in con1], color='g', marker='>', markersize=7,
                            linestyle=(0, (3, 1, 1, 1, 1, 1)),
                            linewidth=2, label='antecedent')
                    ax.plot(ant, [i for _ in ant], color='b', marker='o', markersize=9,
                            linestyle=(0, (3, 1, 1, 1, 1, 1)),
                            linewidth=2, label='consequent')
                    legend_control += 1
                else:
                    ax.plot(con1, [i for _ in con1], color='g', marker='>', markersize=7,
                            linestyle=(0, (3, 1, 1, 1, 1, 1)),
                            linewidth=2)
                    ax.plot(ant, [i for _ in ant], color='b', marker='o', markersize=9,
                            linestyle=(0, (3, 1, 1, 1, 1, 1)),
                            linewidth=2)
                lix = list(range(len(con) + len(ant)))
                liy = [i for _ in lix]
                lab = list(ant_name) + list(con_name)
                for x, y in zip(lix, liy):
                    name = self.get_hash_url(lab[x]).split('/')[-1].split('.')[0]
                    label = fr'$Url{name}$'
                    # this method is called for each point
                    ax.annotate(label,  # this is the text
                                (x, y),  # this is the point to label
                                textcoords="offset points",  # how to position the text
                                xytext=(0, 7),  # distance from text to points (x,y)
                                ha='center')  # horizontal alignment can be left, right or center
            ax.set_title('Association Rules')
            #ax.legend()
            ax.axis('off')
            plt.subplot(ax)

    @staticmethod
    def percent(value, total):
        if value > 0:
            return round((value / total) * 100, 2)
        else:
            return 0

    def plot_cache_performance(self, ax):
        keys = ['Hit', 'Miss', 'M-Hit']
        total = self.miss + self.hit + self.mec_hit

        val = [self.percent(self.hit, total),
               self.percent(self.miss, total),
               self.percent(self.mec_hit, total)]
        cols = ['g', 'r', 'b']
        ypos = ([0, 1, 2])

        values = [self.hit, self.miss, self.mec_hit]
        for i in values:
            j = values.index(i)
            ax.text(j - 0.1, values[j], '{}%'.format(val[j]), rotation=0,
                    ha="center", va="center", bbox=dict(boxstyle="round", ec=(1., 0.5, 0.5), fc=(1., 0.8, 0.8), ))
        ax.set_xticks(ypos)
        ax.set_xticklabels(keys)
        ax.bar(ypos, values, align='center', color=cols, alpha=0.3)
        ax.set_title('Cache Performance')
        plt.subplot(ax)

    def hit_ratio(self):
        print('Hit ratio: ', round((((self.hit + self.mec_hit) / (self.hit + self.mec_hit + self.miss)) * 100)), '%')
        print('mec hit ratio: ', round((self.mec_hit / (self.hit + self.mec_hit)) * 100), '%')
        print('Pre-cached: ', self.pre_cached)
        pred = round((self.rule_matches['right'] / (self.rule_matches['right'] + self.rule_matches['wrong'])) * 100)
        print('Right Predictions: ', pred, '%')
        print(f"Generated {self.rule_matches['right']+self.rule_matches['wrong']} rules | "
              f"{len(self.rule_matches['rules'])} are unique")


class AssociateCache:
    def __init__(self, data, rule_no, group_no):
        self.data = data  # a list of dataset = [2, 3, 4, 5, ...]
        self.rule_no = rule_no  # how many rules you want to generate
        self.group_no = group_no  # group_no = len(set(self.data))

    def gen_rules(self):
        df = self.data_preparation()
        frequent_items = apriori(df, min_support=0.4, use_colnames=True)
        rules = association_rules(frequent_items, metric='lift', min_threshold=1)
        rul_sort = rules.sort_values(by=['support', 'confidence', 'lift'])
        if len(rul_sort) > self.rule_no:
            rule_dict = [[list(rul_sort.values[-i, 0]), list(rul_sort.values[-i, 1])] for i in
                         range(1, self.rule_no + 1)]
        else:
            print(f'generated rules less than rule number | {len(rul_sort)} rules')
            rule_dict = [[list(rul_sort.values[i, 0]), list(rul_sort.values[i, 1])] for i in range(len(rul_sort))]
        return rule_dict

    def data_preparation(self):
        length = len(self.data)

        b = list(range(0, length - 1, self.group_no))
        a = list(range(self.group_no, length, self.group_no))
        h = {i: [0] * len(a) for i in set(self.data)}
        pos = 0
        for i in range(len(a)):
            data_slice = self.data[b[i]:a[i]]
            for j in data_slice:
                h[j][pos] = 1
            pos += 1
        return pd.DataFrame.from_dict(h)


class BrokerCom:
    def __init__(self, user, pw, ip, sub_topic):
        self.user = user
        self.pw = pw
        self.ip = ip
        self.port = 1883
        self.topic = sub_topic
        self.client = mqtt.Client()
        self.run = 1

    def on_connect(self, connect_client, userdata, flags, rc):
        print("Connected with Code :" + str(rc))
        # Subscribe Topic from here
        connect_client.subscribe(self.topic)

    @staticmethod
    def on_message(message_client, userdata, msg):
        print(f'Topic received: {msg.topic}')
        topic_recv = msg.topic
        if topic_recv == 'cache/add':
            data = pickle.loads(msg.payload)
            mec_cache.add_cache(data[0], data[1])  # cache/add [cache_content_hash, mec]  [mec, old_cache, new_cache]

        elif topic_recv == 'cache/replace':
            data = pickle.loads(msg.payload)
            mec_cache.replace(data[0], data[1], data[2])  # [mec, old_cache, new_cache]

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


def ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]


def split_data(_id_, no_mec):
    data = pd.read_csv(r'cache_request/cache_data.csv')  # replace with your data-set
    d_step = len(data) // no_mec
    return data[_id_ * d_step:(_id_ + 1) * d_step]


def get_host_id():
    cmd = ['cat /etc/hostname']
    hostname = str(sp.check_output(cmd, shell=True), 'utf-8')[:-1]
    try:
        host_id = int(re.findall('[0-9]+', hostname)[0])
        return host_id
    except ValueError:
        print(f'invalid hostname: {hostname} \nValid hostname -> mec11 \nlast 1 or 2 characters must be digit')


def plot_graphs():
    axis = [ax1, ax2, ax3, ax4, ax5, ax6]

    # plot asso
    local_cache.plot_association(ax=axis[0])
    # plot asso acuracy
    local_cache.plot_association_accuracy(ax=axis[1])
    # plot_rtts()
    mec_rtt.plot_data(ax=axis[2])
    # plot_cpu()
    cpu_record.add_data()
    cpu_record.plot_data(ax=axis[3], col='m')
    # plot_memory()
    memory_record.add_data()
    memory_record.plot_data(ax=axis[4], col='b')
    # plot hit ratio
    local_cache.plot_cache_performance(ax=axis[5])
    fig.suptitle('MEC Performance During Caching Experiment')


def show_graphs():
    drawnow(plot_graphs)


def run_me():
    global mec_cache
    global mec_rtt
    global messenger
    global cpu_record
    global memory_record
    global local_cache

    os.system('clear')
    # Variable initializations
    broker_dict = {'user': 'mec', 'pw': 'password', 'sub_topic': 'cache/#'}
    '''
    web server ip: '192.168.205.137'  # 
    Broker ip: '192.168.205.139'     # 
    content name server: '192.168.205.138'  # 
    '''
    no_mec = int(input('number of mecs: '))
    web_server = '192.168.205.137'  # input('web server ip: ')
    broker_ip = '192.168.205.139'  # input('Broker ip: ')
    broker_dict.update({'ip': broker_ip})
    host_id = get_host_id()
    data_df = split_data(host_id, no_mec)
    # local_cache_details = {'cache_size': 5, 'content_name_server': input('content name server: ')}
    local_cache_details = {'cache_size': 5, 'content_name_server': '192.168.205.138'}
    local_cache_details.update({'window_size': local_cache_details['cache_size'] * 8})

    # initialization of objects
    mec_rtt = MecDelay(window_size=300)
    cpu_record = CPU(window_size=300, title='CPU')
    memory_record = Memory(window_size=300, title='Memory')
    messenger = BrokerCom(**broker_dict)
    h1 = Thread(target=messenger.broker_loop)
    h1.start()
    mec_cache = MecCache()
    local_cache = LocalCache(**local_cache_details)  # cache_size, window_size, content_name_server
    input('start: ')
    time.sleep(5)
    try:
        for req in data_df.values:
            url = f'http://{web_server}/{req[0]}.html'
            print(f'Requesting {url}')
            local_cache.request(url)
            mec_rtt.add_delay()
            show_graphs()
            time.sleep(1)

        local_cache.hit_ratio()
        messenger.run = 0
        print('Done!')
    except KeyboardInterrupt:
        os.system('sh clean_up.sh')
        print('killed!')


if __name__ == '__main__':
    run_me()
