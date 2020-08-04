import hashlib
import math
import random as r
import pandas as pd
import time
import os
import psutil
import heapq
import json
import requests
from threading import Thread
from mlxtend.frequent_patterns import fpgrowth
from mlxtend.frequent_patterns import apriori
from mlxtend.frequent_patterns import association_rules
import socket
import wget
import subprocess as sp
import argparse
import config
import smtplib
from email.message import EmailMessage
import pickle
import paho.mqtt.client as mqtt
import re


class Record:
    system = psutil.Process(os.getpid())

    def __init__(self, window_size, title):
        self.data_set = []
        self.window_size = window_size
        self.title = title
        self.count = 0

    def get_data(self):
        return 1

    def add_data(self):
        data = self.get_data()
        new_avg = self.calculate_mov_avg(data)
        self.check_window_size()
        self.data_set.append(new_avg)

    def check_window_size(self):
        if len(self.data_set) > self.window_size:
            outfile = open(f'results/{self.title}/{self.count}.pickle', 'wb')
            pickle.dump(self.data_set, outfile)
            outfile.close()
            self.data_set = self.data_set[-1:]
            self.count += 1

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
        try:
            lst = self.data_set[-1]
        except IndexError:
            lst = psutil.cpu_percent(percpu=False)
        return round(abs(cpu - lst), 4)


class Memory(Record):

    def get_data(self):
        return round(self.system.memory_percent(), 4)


class Delay:
    def __init__(self, window_size):
        self.data_set = []
        self.window_size = window_size
        self.count = 0

    def add_data(self, data):
        new_avg = self.calculate_mov_avg(data)
        self.data_set.append(new_avg)
        self.check_window_size()

    def calculate_mov_avg(self, a1):
        _count = len(self.data_set)
        if _count == 0:
            avg1 = 0
        else:
            avg1 = self.data_set[-1]
        _count += 1
        avg1 = ((_count - 1) * avg1 + a1) / _count  # cumulative average formula μ_n=((n-1) μ_(n-1)  + x_n)/n
        return round(avg1, 4)

    def check_window_size(self):
        if len(self.data_set) > self.window_size:
            outfile = open(f'results/delay/{self.count}.pickle', 'wb')
            pickle.dump(self.data_set, outfile)
            outfile.close()
            self.data_set = self.data_set[-1:]
            self.count += 1


class Heap:
    def __init__(self):
        self.heap = []  # delay
        heapq.heapify(self.heap)
        self.table = {}  # delay : mec

    def unique_delay(self, delay):
        if delay in self.heap:
            delay -= 0.00001
            return self.unique_delay(delay)
        else:
            return delay

    def push(self, delay, mec):
        if mec not in self.table.values():
            delay = self.unique_delay(delay)
            heapq.heappush(self.heap, delay)
            self.table[delay] = mec

    def remove(self, mec):
        if mec in self.table.values():
            t_mec = dict(zip(self.table.values(), self.table.keys()))
            delay_key = t_mec[mec]
            self.heap.remove(delay_key)
            heapq.heapify(self.heap)
            self.table.pop(delay_key)

    def list(self):
        return [self.table[i] for i in self.heap]

    def get_head(self):
        if len(self.heap) != 0:
            return self.table[self.heap[0]]
        else:
            return None

    def __len__(self):
        return len(self.heap)

    def pop(self):
        return heapq.heappop(self.heap)

    def push_pop(self, item):
        """:arg
        Push item on the heap, then pop and return the smallest item from the heap
        """
        return heapq.heappushpop(self.heap, item)

    def replace(self, item):
        """:arg
        Pop and return the smallest item from the heap, and also push the new item
        """
        return heapq.heapreplace(self.heap, item)


class CollaborativeCache:
    def __init__(self, no_mec):
        self.cache_store = {}  # {cache_id: heap({mec1, mec2}), ..}
        self.w = 0.1  # No of MEC that can store a cache in percentage
        self.no_mec = no_mec

    def cache_decision(self, length):
        if length < math.ceil(self.w * self.no_mec):
            return 1
        else:
            return 0

    @staticmethod
    def ping(host):
        cmd = [f'ping -c 1 {host}']
        try:
            output = str(sp.check_output(cmd, shell=True), 'utf-8').split('\n')
        except sp.CalledProcessError:
            print(f'{host} -> destination unreachable..')
            return None
        try:
            value = float(output[-2].split('=')[-1].split('/')[0])
        except ValueError:
            print(f"{output[-2].split('=')[-1].split('/')[0]} -> Ping Value Error")
            value = None
        return value

    def get_delay(self, mec):
        rtt = self.ping(mec)
        if rtt:
            return round(rtt, 4)
        else:
            return self.get_delay(mec)

    def add_cache(self, cache_content_hash, mec):  # multi-cast from mec
        mec_delay = self.get_delay(mec)
        if cache_content_hash not in self.cache_store:
            self.cache_store[cache_content_hash] = Heap()
        self.cache_store[cache_content_hash].push(mec_delay, mec)

    @staticmethod
    def __getfile(mec, content_hash):
        request_link = f"ftp://{mec}/cache/{content_hash}.html"
        name = f'{content_hash}.html'
        start = time.perf_counter()
        filename = f'temp/{name}'
        try:
            wget.download(request_link, filename)
        except Exception as e:
            wget.download(request_link, filename)

        cost = round(time.perf_counter() - start, 5)

        return cost

    def find_cache(self, cache_content_hash):
        try:
            mec = self.cache_store[cache_content_hash].get_head()
            return self.__getfile(mec, cache_content_hash), self.cache_decision(len(self.cache_store[cache_content_hash]))
        except KeyError:
            return None

    def table(self):
        return {i: self.cache_store[i].list() for i in self.cache_store}

    def replace(self, mec, old_cache, new_cache):  # multi-cast from mec
        self.cache_store[old_cache].remove(mec)
        if len(self.cache_store[old_cache]) == 0:
            self.cache_store.pop(old_cache)
        self.add_cache(new_cache, mec)


# A linked list node
class Node:
    # Constructor to create a new node
    def __init__(self, data):
        self.data = data
        self.next = None
        self.prev = None
        self.id = self.get_hash()
        self.count = 0
        self.last_access = time.time()
        self.retrieval_cost = 0
        self.content_id = None

    @property
    def page_no(self):
        return re.findall('[0-9]+', self.data.split('/')[-1])

    def get_hash(self):
        y = str.encode(str(self.data))
        ha = hashlib.sha256(y)
        hash_no = ha.hexdigest()
        return hash_no

    @property
    def details(self):
        d = lambda x: None if x is None else x.data
        return {'data': self.data, 'next': d(self.next), 'prev': d(self.prev), 'count': self.count}

    def reduce_count(self):
        self.count = math.ceil(self.count / 2)


class FIFO:
    def __init__(self, maxsize):
        self.head = None
        self.tail = None
        self.length = 0
        self.table = {}
        self.maxsize = maxsize

    # Given a reference to the head of a list and an
    # integer, inserts a new node on the front of list
    def push(self, new_node):

        # 1. Allocates node
        # 2. Put the data in it

        self.table[new_node.id] = new_node

        # 3. Make next of new node as head and
        # previous as None (already None)
        new_node.next = self.head

        # 4. change prev of head node to new_node
        if self.head is not None:
            self.head.prev = new_node

            # 5. move the head to point to the new node
        self.head = new_node
        if not self.tail:
            self.tail = new_node

        self.length += 1
        self.maintain_size()

        return new_node

    def maintain_size(self):
        if self.length > self.maxsize:
            self.delete(self.tail)

    def delete(self, node):
        if node.id in self.table:
            node = self.table.pop(node.id)
            if node.prev:
                if node.next:  # delete a middle node
                    node.prev.next = node.next
                    node.next.prev = node.prev
                else:  # delete last node
                    node.prev.next = None
                    self.tail = node.prev

            else:  # delete head node
                self.head = node.next
                if node.next:
                    node.next.prev = None
                else:
                    self.tail = None
            self.length -= 1
        return node

    def list(self):
        d_list = []
        node = self.head
        while node:
            d_list.append(node.data)
            node = node.next
        return d_list

    def reduce_count(self):
        node = self.head
        while node:
            node.reduce_count()
            node = node.next


# Class to create a Doubly Linked List
class LRUChain:

    # Constructor for empty Doubly Linked List
    def __init__(self):
        self.head = None
        self.tail = None
        self.length = 0
        self.table = {}

    # Given a reference to the head of a list and an
    # integer, inserts a new node on the front of list
    def push(self, new_node):

        # 1. Allocates node
        # 2. Put the data in it

        if new_node.id in self.table:
            new_node = self.delete_node(self.table[new_node.id])
            new_node.next = None
            new_node.prev = None
        self.table[new_node.id] = new_node

        # 3. Make next of new node as head and
        # previous as None (already None)
        new_node.next = self.head

        # 4. change prev of head node to new_node
        if self.head is not None:
            self.head.prev = new_node

            # 5. move the head to point to the new node
        self.head = new_node
        if not self.tail:
            self.tail = new_node

        self.length += 1

        return new_node

    def print_list(self, node):
        print("\nTraversal in forward direction")
        while node is not None:
            print(node.data)
            node = node.next

        print("\nTraversal in reverse direction")
        last = self.tail
        while last is not None:
            print(last.data)
            last = last.prev

    def find(self, id_):
        node = self.head
        while node:
            if node.id == id_:
                result = f'id: {id_} \nData: {node.data}'
                print(result)
                return node
            node = node.next
        return None

    def remove_with_id(self, id_):
        node = self.find(id_)
        if node:
            if node.prev:
                if node.next:  # delete a middle node
                    node.prev.next = node.next
                    node.next.prev = node.prev
                else:  # delete last node
                    node.prev.next = None
                    self.tail = node.prev
                print(f'Deleted {id_}')
            else:  # delete head node
                self.head = node.next
                if node.next:
                    node.next.prev = None
                else:
                    self.tail = None
                print(f'Deleted {id_}')
            self.length -= 1
        return node

    def remove_with_data(self, data):
        node = self.head
        while node:
            if node.data == data:
                if node.prev:
                    if node.next:  # delete a middle node
                        node.prev.next = node.next
                        node.next.prev = node.prev
                    else:  # delete last node
                        node.prev.next = None
                        self.tail = node.prev
                    print(f'Deleted {data}')
                else:  # delete head node
                    self.head = node.next
                    if node.next:
                        node.next.prev = None
                    else:
                        self.tail = None
                    print(f'Deleted {data}')
                self.length -= 1
                return node
            node = node.next
        return None

    def delete_node(self, node):
        if node.id in self.table:
            node = self.table.pop(node.id)
            if node.prev:
                if node.next:  # delete a middle node
                    node.prev.next = node.next
                    node.next.prev = node.prev
                else:  # delete last node
                    node.prev.next = None
                    self.tail = node.prev

            else:  # delete head node
                self.head = node.next
                if node.next:
                    node.next.prev = None
                else:
                    self.tail = None
            self.length -= 1
        return node

    def list(self):
        d_list = []
        node = self.head
        while node:
            d_list.append(node.data)
            node = node.next
        return d_list

    def details(self):
        d_list = []
        node = self.head
        while node:
            d_list.append(node.details)
            node = node.next
        return d_list

    def count_display(self):
        d_list = []
        node = self.head
        while node:
            d_list.append(node.count)
            node = node.next
        return d_list

    def hash_table(self):
        d_list = {}
        node = self.head
        while node:
            d_list[node.id] = node.data
            node = node.next
        return d_list


class NameResolutionServer:
    def __init__(self, content_name_server):
        self.content_name_server = content_name_server

    def get_json_data(self, endpoint, send=None):
        url = f'http://{self.content_name_server}/'
        if send:
            response = requests.post(url + endpoint, json=json.dumps(send))
        else:
            response = requests.get(url + endpoint)
        data = json.loads(response.content)
        return data

    def add_to_server(self, location_hash, content_hash, url):
        self.get_json_data(endpoint='add/', send=[location_hash, content_hash, url])

    def get_content_hash(self, location_hash):
        return self.get_json_data(endpoint=f'read/hash/{location_hash}')['hash']


class Matches:
    def __init__(self, size):
        self.size = size
        self.matches = []  # [{match1: [0,0], match2: 1, ...}, {}]   0 means not precache, 1 means precache
        self.right = 0
        self.wrong = 0
        self.right_cache = 0
        self.wrong_cache = 0

    @property
    def total(self):
        return self.right + self.wrong

    def contains(self, item):
        for match_dict in self.matches:
            if item in match_dict:
                self.right += 1
                match_dict[item][1] = 1  # item has been used
                if match_dict[item][0] == 1:
                    self.right_cache += 1

    def push(self, match):
        if len(self.matches) >= self.size:
            self.check_wrong(self.matches.pop(0))
        self.matches.append(match)

    def check_wrong(self, match):
        for key in match:
            if match[key][1] == 0:
                self.wrong += 1
                if match[key][0] == 1:
                    self.wrong_cache += 1

    def __len__(self):
        return len(self.matches)


class LocalCache:

    def __init__(self, cache_size, max_freq, avg_max, window_size, content_name_server, delay):
        self.cache_size = cache_size
        self.max_freq = max_freq
        self.history = FIFO(cache_size * 8)
        self.chain = {}
        self.table = {}
        self.length = 0
        self.hit = 0
        self.miss = 0
        self.mec_hit = 0
        self.avg_max = avg_max
        self.min_freq = 1
        self.content_name_server = content_name_server
        self.delay = delay
        self.cache_dir = '/srv/ftp/cache'
        self.req_window = window_size ** 2
        self.window_size = window_size
        self.req = []
        self.to_delete = ['test']
        self.pre_cached = 0
        self.no_rules = 6
        self.rules = RuleStore(ant_max=4, max_length=20)
        self.matches = Matches(5)
        self.content_name_resolution = NameResolutionServer(content_name_server=content_name_server)
        self.rule_matches = {'window_count': 0, 'window_size': int(self.window_size / 2), 'rule_count': 0}

    @staticmethod
    def web_page(request):
        return f"https://competent-euler-834b51.netlify.app/pages/{request}.html"

    @staticmethod
    def get_hash(data):
        y = str.encode(str(data))
        ha = hashlib.sha256(y)
        hash_no = ha.hexdigest()
        return hash_no

    @staticmethod
    def mec_cache_link(content_hash, mec):
        return f"ftp://{mec}/cache/{content_hash}.html"

    def rename_to_content_hash(self, web_link, filename, temp=0):
        file_ = open(filename, 'rb')
        content_hash = hashlib.sha256(file_.read()).hexdigest()
        file_.close()
        self.content_name_resolution.add_to_server(content_hash=content_hash, url=web_link,
                                                   location_hash=self.get_hash(web_link))
        if temp == 0:
            os.system(f'mv {self.cache_dir}/temp {self.cache_dir}/{content_hash}.html')
        return content_hash

    def get_file(self, request_link, temp=0):
        name = request_link.split('/')[-1]
        start = time.perf_counter()
        if temp == 1:
            filename = f'temp/{name}'
            try:
                wget.download(request_link, filename)
            except Exception as e:
                wget.download(request_link, filename)
        else:
            filename = f'{self.cache_dir}/temp'
            try:
                wget.download(request_link, filename)
            except Exception as e:
                wget.download(request_link, filename)
        cost = round(time.perf_counter() - start, 5)
        content_hash = self.rename_to_content_hash(web_link=request_link, filename=filename, temp=temp)

        return cost, content_hash

    def association_match_count(self, req):
        self.matches.contains(req)

    def add_req_to_list(self, cache):
        self.window_check()
        self.req.append(cache)

    def window_check(self):
        if len(self.req) > self.req_window:
            self.req.pop(0)

    @property
    def average_count(self):
        return round(sum(self.chain.keys()) / len(self.chain), 2)

    def maintain_count(self):
        if self.average_count > self.avg_max:
            # print('start: ', self.details_display())
            new_chain = {}
            event = 'maintaining count... ..'
            display_event(kind='notify', event=event, origin='maintain_count')

            def reduce_count(node):
                while node:
                    node.reduce_count()
                    if node.count not in new_chain: new_chain[node.count] = LRUChain()
                    new_chain[node.count].push(node)
                    if node.count < self.min_freq: self.min_freq = node.count
                    node = node.prev

            for chain in self.chain.values():
                reduce_count(chain.tail)
            self.history.reduce_count()
            self.chain = new_chain

    def increment_count_decision(self, node):
        diff = 1
        # event = f'loop list -> {list(range(node.count-1, 0, -1))}'
        # display_event(kind='notify', event=event, origin='increment_count_decision')
        for tf in range(node.count - 1, 0, -1):
            try:
                q = self.chain[tf]
                print('in->', tf, q)
                break
            except KeyError:
                diff += 1
        if diff < self.max_freq:
            return True, diff
        else:
            return False, diff

    def request(self, page):
        self.push(page)
        self.association_match_count(page)
        if self.rule_matches['window_count'] == self.rule_matches['window_size']:
            self.get_association_rules()
            self.apply_association()
            self.rule_matches['window_count'] = 0
        else:
            if len(self.rules) > 0:
                self.apply_association()
            self.rule_matches['window_count'] += 1

    def push(self, page, precache=0):
        web_link = self.web_page(page)
        new_node = Node(web_link)
        if precache == 0:
            self.add_req_to_list(page)
        decision = [1, None]  # 0 means don't cache, 1 means cache
        if new_node.id in self.table:
            if precache == 1:
                decision[0] = 0
                display_event(kind='notify', event='Association Precache already in store', origin='push')
            else:
                self.delay.add_data(0)
                display_event(kind='notify', event=f'Cache Hit', origin='push from LocalCache')
                new_node = self.table[new_node.id]  # dont remove this, it is useful, even if you dont think it is
                new_node = self.chain[new_node.count].delete_node(new_node)  # self.table[new_node.id]
                new_node.prev, new_node.next = None, None
                new_node.last_access = time.time()
                self.hit += 1
                result = self.increment_count_decision(new_node)
                if self.chain[new_node.count].length == 0:
                    self.chain.pop(new_node.count)

                    if result[0] and (self.min_freq == new_node.count):
                        self.min_freq += 1
                if result[0]:
                    display_event(kind='notify', event=f'incrementing ->{result}', origin='push from LocalCache')
                    new_node.count += 1
                else:
                    display_event(kind='notify', event=f'Not incrementing ->{result}', origin='push from LocalCache')
            # print('hit')

        else:
            display_event(kind='notify', event='cache miss', origin='push from LocalCache')
            reply = self.check_mec(new_node)  # None or (decision, node) or (decision, node, replace)
            if reply:
                if precache == 0:
                    self.mec_hit += 1
                decision = reply

                print(f'\n\nMEC cache -> {collaborative_cache.table()} \n\n')
                new_node = decision[1]
                # do if only cache is to be stored! maintain min freq
                if (decision[0] == 1) and ((precache == 0) or (new_node.count == 0)):
                    new_node.count += 1
                    event = f'incrementing new ->{new_node.count} | {self.chain.keys()}'  # incremented always for miss
                    display_event(kind='notify', event=event, origin='push from LocalCache')
                if decision[0] == 1:
                    event = 'cached from mec'
                    display_event(kind='notify', event=event, origin='push from LocalCache')
                    self.table[new_node.id] = new_node
                    self.length += 1
                    if new_node.count < self.min_freq:
                        if self.min_freq - self.max_freq > new_node.count:
                            new_node.count = self.min_freq - self.max_freq
                        self.min_freq = new_node.count

                else:
                    event = 'Obtained from mec, Not Cached'
                    display_event(kind='notify', event=event, origin='push from LocalCache')
                    event = f'Not stored | Not incrementing new ->{new_node.count} | {self.chain.keys()}'
                    display_event(kind='notify', event=event, origin='push from LocalCache')
                if len(decision) == 3:
                    if decision[2]:
                        messenger.publish('cache/replace',
                                          pickle.dumps([ip_address(), decision[2].content_id, new_node.content_id]))
                elif self.length < self.cache_size:  # decision is right | send add cache only when length > cache_size
                    messenger.publish('cache/add', pickle.dumps([new_node.content_id, ip_address()]))

            else:
                if precache == 0:
                    self.miss += 1
                if self.length >= self.cache_size:
                    decision = self.maintain_cache_size(new_node)

                if decision[0] == 1:
                    new_node = new_node if decision[1] is None else decision[1]
                    if (precache == 0) or (new_node.count == 0):
                        if new_node.count + 1 < self.min_freq:
                            if self.min_freq - self.max_freq > new_node.count + 1:
                                new_node.count = self.min_freq - self.max_freq
                            self.min_freq = new_node.count + 1
                        new_node.count += 1
                    event = f'incrementing new ->{new_node.count} | {self.chain.keys()}'
                    display_event(kind='notify', event=event, origin='push from LocalCache')
                    self.table[new_node.id] = new_node
                    self.length += 1
                    new_node.retrieval_cost, new_node.content_id = self.get_file(request_link=web_link, temp=0)
                else:
                    if precache == 0:
                        new_node.count += 1
                    new_node.retrieval_cost, new_node.content_id = self.get_file(request_link=web_link, temp=1)
                    event = f'incrementing new ->{new_node.count} | {self.chain.keys()}'
                    display_event(kind='notify', event=event, origin='push from LocalCache')
                if len(decision) == 3:
                    if decision[2]:
                        messenger.publish('cache/replace',
                                          pickle.dumps([ip_address(), decision[2].content_id, new_node.content_id]))

                elif self.length < self.cache_size:  # decision is right | send add cache only when length > cache_size
                    messenger.publish('cache/add', pickle.dumps([new_node.content_id, ip_address()]))

            if precache == 0:
                self.delay.add_data(new_node.retrieval_cost)

        if decision[0] == 1:
            try:
                self.chain[new_node.count].push(new_node)
            except KeyError:
                self.chain[new_node.count] = LRUChain()
                self.chain[new_node.count].push(new_node)
        self.maintain_count()
        if precache == 1:
            return decision[0]

    def mec_rename_temp(self, content_hash):
        filename_full = rf'temp/{content_hash}.html'
        os.system(f'mv {filename_full} {self.cache_dir}/{content_hash}.html')

    def check_mec(self, new_node):
        """:arg
        This function returns one of the following:
        1. None
        2. (Decision, node)  => node plus cost and time
        3. (Decision, node, replace)  => node plus cost and time
        """
        def get_response(content_hash):
            response = collaborative_cache.find_cache(content_hash)
            new_node.content_id = content_hash
            if response:  # response = None or (cost, decision)
                new_node.retrieval_cost = response[0]
                if (response[1] == 1) and (self.length >= self.cache_size):
                    reply = self.maintain_cache_size(new_node)  # result => cache_decision, node, replaced
                    if reply[0] == 1:
                        self.mec_rename_temp(content_hash)
                    return reply, 1
                elif response[1] == 0:
                    return (response[1], new_node), 0
                else:
                    self.mec_rename_temp(content_hash)
                    return (response[1], new_node), 1
            else:
                return None, 1
        if new_node.id in self.history.table:
            con_id = self.history.table[new_node.id].content_id
            decision = get_response(con_id)
            if (decision[0] != None) and (decision[1] == 0):
                new_node = self.history.delete(new_node)
                new_node.next, new_node.prev = None, None
                self.history.push(new_node)
            new_node.last_access = time.time()
            return decision[0]
        else:
            content_id = self.content_name_resolution.get_content_hash(location_hash=new_node.id)
            if content_id:
                new_node.last_access = time.time()
                return get_response(content_id)[0]
        return None

    def find_new_min_freq(self):
        found = False
        for i in range(self.min_freq, self.min_freq + self.max_freq + 1):
            try:
                tail_node = self.chain[i].tail
                self.min_freq = tail_node.count
                found = True
                break
            except KeyError:
                pass
        if found:
            event = f'next min freq found -> {self.min_freq}'
            display_event(kind='notify', event=event, origin='find_new_min_freq')
        else:
            event = f'next min freq not found-> {self.min_freq} | ' \
                    f'{list(range(self.min_freq, self.min_freq + self.max_freq + 1))}'
            display_event(kind='notify', event=event, origin='find_new_min_freq')

    def maintain_cache_size(self, node):
        cache_decision = 0  # 0 means don't cache, 1 means cache
        replaced = None
        if node.id in self.history.table:
            node = self.history.delete(node)
            node.next, node.prev = None, None
            min_queue = self.chain[self.min_freq]
            victim = min_queue.tail
            # print(self.sorted_freq.heap)
            # print('comparing: ', node.data, victim.data, '->', self.data_display())
            if (node.last_access > victim.last_access) or (node.retrieval_cost > victim.retrieval_cost):
                # print('before eviction ++++',  self.data_display() )
                display_event(kind='notify', event=f'evicting {victim.content_id}', origin='maintain_cache_size')
                self.evict(victim)
                replaced = victim
                victim.next, victim.prev = None, None
                self.history.push(victim)
                node.last_access = time.time()
                cache_decision += 1
                # print('evicted: ++++', victim.data, 'recap: ', self.data_display())
            else:
                node.last_access = time.time()
                self.history.push(node)

        else:
            self.history.push(node)

        return cache_decision, node, replaced

    def evict(self, victim):
        os.system(f'rm {self.cache_dir}/{self.to_delete.pop(0)}.html')
        self.to_delete.append(victim.content_id)
        self.chain[victim.count].delete_node(victim)
        self.length -= 1
        self.table.pop(victim.id)
        if self.chain[victim.count].length == 0:
            self.chain.pop(victim.count)
            self.find_new_min_freq()

        return victim

    def apply_association(self):
        match = 0
        match_dict = {}
        for i in range(1, self.rules.ant_max + 1):
            try:
                cons = self.rules.rules[i][tuple(self.req[-i:])]
                # [{match1: [0,0], match2: 1, ...}, {}]
                display_event(kind='notify', event=f'association match {cons}', origin='apply_association')
                for page in cons:
                    match_dict[page] = [self.push(page, precache=1), 0]
                    match += 1
            except KeyError:
                pass
        if match == 0:
            display_event(kind='notify', event=f'No association Match', origin='apply_association')
        else:
            self.matches.push(match_dict)

    def get_association_rules(self):
        if len(self.req) >= self.window_size:
            group_no = len(set(self.req[-self.window_size:]))
            data_len = group_no ** 2
            if len(self.req) >= data_len:
                data = self.req[-data_len:]
                print(f'Generating Association rules for data {group_no}x{len(data)}')
                t1 = time.time()
                rules = AssociateCache(data=data, rule_no=self.no_rules, group_no=group_no).gen_rules()
                self.rules.add_rules(rules)
                self.rule_matches['rule_count'] += 1
                t2 = time.time()
                display_event(kind=f'Association Rules | Time: {round(t2-t1, 5)}', event=rules,
                              origin='get_association_rules')

    def total_hit_ratio(self):
        return round((((self.hit + self.mec_hit) / (self.hit + self.mec_hit + self.miss)) * 100), 2)

    def mec_hit_ratio(self):
        return round((self.mec_hit / (self.hit + self.mec_hit)) * 100, 2)

    def hit_ratio(self):
        return round((self.hit / (self.hit + self.mec_hit + self.miss)) * 100, 2)

    def right_predictions(self):
        return round((self.matches.right / (self.matches.right + self.matches.wrong)) * 100)

    def data_display(self):
        return {i: self.chain[i].list() for i in self.chain}

    def details_display(self):
        return {i: self.chain[i].details() for i in self.chain}

    def outcome_details(self):
        text = {'right_match': self.matches.right,
                'Wrong_match': self.matches.wrong,
                'right_pre_cache': self.matches.right_cache,
                'wrong_pre_cache': self.matches.wrong_cache,
                'total_hit_ratio': self.total_hit_ratio(),
                'mec_hit_ratio': self.mec_hit_ratio(),
                'hit_ratio': self.hit_ratio()
                }

        return text

    def experiment_details(self):
        print('Total Hit ratio: ', self.total_hit_ratio(), '%')
        print('mec hit ratio: ', self.mec_hit_ratio(), '%')
        print('hit ratio: ', self.hit_ratio(), '%')
        print('Pre-cached: ', self.pre_cached)
        total_matches = (self.matches.right + self.matches.wrong)
        if total_matches != 0:
            pred = round((self.matches.right / total_matches) * 100)
        else:
            pred = 0
        print('Right Predictions: ', pred, '%')
        print(f"Generated {self.rule_matches['rule_count']} rules ")
        print(f"No of association matches: ", self.matches.total)
        print(f"Right: {self.matches.right}   | Wrong: {self.matches.wrong}")
        print(f"right Pre_cache: {self.matches.right_cache} |"
              f" wrong pre_cache: {self.matches.wrong_cache}")


class RuleStore:
    def __init__(self, ant_max, max_length):
        self.rules = {i: {} for i in range(1, ant_max + 1)}  # {length_of_ant: {ant: cons}, ..}
        self.lru_list = []  # stores antecedants
        self.ant_max = ant_max
        self.max_length = max_length

    def add_rules(self, rules):
        # [((13,), (88, 18, 47)), ((13, 47), (88, 18)), ((18, 47), (88, 13))]
        self.maintain_length(len(rules))
        for rule_set in rules:
            if rule_set[0] in self.lru_list:
                self.lru_list.remove(rule_set[0])
                self.rules[len(rule_set[0])].pop(rule_set[0])
            self.lru_list.append(rule_set[0])
            self.rules[len(rule_set[0])][rule_set[0]] = rule_set[1]

    def maintain_length(self, length):
        new_length = len(self.lru_list) + length
        if new_length > self.max_length:
            remove_no = new_length - self.max_length
            for i in range(remove_no):
                victim = self.lru_list.pop(0)
                self.rules[len(victim)].pop(victim)

    def __len__(self):
        return len(self.lru_list)


class AssociateCache:
    def __init__(self, data, rule_no, group_no):
        self.data = data  # a list of dataset = [2, 3, 4, 5, ...]
        self.rule_no = rule_no  # how many rules you want to generate
        self.group_no = group_no  # group_no = len(set(self.data))
        self.mem_max = 80
        self.min_support = 0.45
        self.sparse_threshold = 0.55

    def data_preparation(self):
        length = len(self.data)

        b = list(range(0, length - 1, self.group_no))
        a = list(range(self.group_no, length, self.group_no))
        h = {i: [0] * len(a) for i in set(self.data)}
        pos = 0
        for i in range(len(a)):
            data_sliced = self.data[b[i]:a[i]]
            for j in data_sliced:
                h[j][pos] = 1
            pos += 1
        df = pd.DataFrame.from_dict(h)
        # sdf = df.astype(pd.SparseDtype("int", 0))
        return df

    def get_freq_items(self, algorithm, support, data):
        print('supp->', support)
        if algorithm == 'apriori':
            freq_items = apriori(data, min_support=support, use_colnames=True)
        else:
            freq_items = fpgrowth(data, min_support=support, use_colnames=True)
        if freq_items.size == 0:
            print('reducing support')
            return self.get_freq_items(algorithm, support - 0.25, data)
        else:
            # print('freq items->', freq_items)
            return freq_items

    def freq_items_algorithm_decision(self, sdf):
        # sdf.columns = [str(i) for i in sdf.columns]
        if (memory_record.get_data() < self.mem_max) and (
                sdf.astype(pd.SparseDtype("int", 0)).sparse.density > self.sparse_threshold):
            event = 'using apriori'
            display_event(kind='notify', event=event, origin='Association | freq_items_algorithm')
            return self.get_freq_items(algorithm='apriori', support=self.min_support, data=sdf)
        else:
            event = 'using fpgrowth'
            display_event(kind='notify', event=event, origin='Association | freq_items_algorithm')
            return self.get_freq_items(algorithm='fpgrowth', support=self.min_support, data=sdf)

    def gen_rules(self):
        sdf = self.data_preparation()
        frequent_items = self.freq_items_algorithm_decision(sdf)
        rules = association_rules(frequent_items, metric='lift', min_threshold=1)
        rul_sort = rules.sort_values(by=['support', 'conviction', 'lift'])  # ['support', 'confidence', 'lift']
        if len(rul_sort) > self.rule_no:
            rule_dict = [(tuple(rul_sort.values[-i, 0]), tuple(rul_sort.values[-i, 1])) for i in
                         range(1, self.rule_no + 1)]
        else:
            event = f'generated rules less than rule number | {len(rul_sort)} rules'
            display_event(kind='Notify', event=event, origin='ApAssociate gen_rules')
            rule_dict = [(tuple(rul_sort.values[i, 0]), tuple(rul_sort.values[i, 1])) for i in range(len(rul_sort))]
        return rule_dict


class BrokerCom:
    def __init__(self, user, pw, ip, sub_topic):
        self.user = user
        self.pw = pw
        self.ip = ip
        self.port = 1883
        self.topic = sub_topic
        self.client = mqtt.Client()
        self.mec_ip = ip_address()
        self.run = 1

    def on_connect(self, connect_client, userdata, flags, rc):
        print("Connected with Code :" + str(rc))
        # Subscribe Topic from here
        connect_client.subscribe(self.topic)

    def on_message(self, message_client, userdata, msg):
        print(f'Topic received: {msg.topic}')
        topic_recv = msg.topic
        if topic_recv == 'cache/add':
            data = pickle.loads(msg.payload)
            if data[1] != self.mec_ip:
                collaborative_cache.add_cache(data[0], data[1])  # cache/add [cache_content_hash, mec]

        elif topic_recv == 'cache/replace':
            data = pickle.loads(msg.payload)
            if data[1] != self.mec_ip:
                collaborative_cache.replace(data[0], data[1], data[2])  # [mec, old_cache, new_cache]

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


def display_event(kind, event, origin):
    tab = 50
    print('\n' + '*' * tab)
    print(f'Kind : {kind}')
    print('-' * tab)
    print(f'Kind : {origin}')
    print('-' * tab)
    print(event)
    print('\n' + '*' * tab + '\n')


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
    step = int(total_req_no / no_mec)
    start = host_no * step
    return start + initial, start + step + initial


def send_email(msg):
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com')
        server.ehlo()
        server.login(config.email_address, config.password)
        subject = 'Caching results {} {}'.format('Proposed caching', get_hostname())
        # msg = 'Attendance done for {}'.format(_timer)
        _message = 'Subject: {}\n\n{}\n\n SENT BY RIHANNA \n\n'.format(subject, msg)
        server.sendmail(config.email_address, config.send_email, _message)
        server.quit()
        print("Email sent!")
    except Exception as e:
        print(e)


def send_email_attachment(file):
    msg = EmailMessage()

    msg['Subject'] = 'Caching results {} {}'.format('Proposed caching', get_hostname())

    msg['From'] = config.email_address

    msg['To'] = config.send_email
    msg.set_content(file)
    with open(file, 'rb') as f:
        file_data = f.read()
        # file_type = imghdr.what(f.name)
        file_name = f.name

    msg.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=file_name)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(config.email_address, config.password)
        smtp.send_message(msg)


def save_data(mem, cpu, delay, no, cache_details):
    host = get_hostname()
    host_no = int(re.findall('[0-9]+', host)[0])
    data = f"""
    memory{host_no}_{no} = {mem}
    cpu{host_no}_{no} = {cpu}
    delay{host_no}_{no} = {delay}
    """
    detail = '\n'
    for det in cache_details:
        detail += f'{det}{host_no}_{no} = {cache_details[det]}\n'
    data += detail
    send_email(data)
    file = open(f'results/output{host_no}_{no}.py', 'w')
    file.write(data)
    file.close()
    send_path = '/home/osboxes/results/'
    sp.run(
        ["scp", f'results/output{host_no}_{no}.py', f"osboxes@{result_server_ip}:{send_path}"])
    for res in ['memory', 'cpu', 'delay']:
        os.system(f'zip results/{res}{host_no}_{no}.zip results/{res}/*')
        sp.run(
            ["scp", f'results/{res}{host_no}_{no}.zip', f"osboxes@{result_server_ip}:{send_path}"])
        send_email_attachment(f'results/{res}{host_no}_{no}.zip')
        time.sleep(r.uniform(1, 10))


def arrival_distribution():
    # Poisson Distribution
    host = get_hostname()
    host_no = int(re.findall('[0-9]+', host)[0])
    file = open(f'dist/{host_no}.pickle', 'rb')
    arrival_dist = pickle.load(file)
    file.close()
    return (i for i in arrival_dist)


result_server_ip = '192.168.205.142'
memory_record = Memory(window_size=200, title='memory')
cpu_record = CPU(window_size=200, title='cpu')


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
    br = BrokerRequest(user='mec', pw='password', ip=broker_ip, sub_topic='control')
    br.broker_loop()
    del br
    print('starting ....')


def run(no_mec):
    global collaborative_cache
    global messenger

    os.system('clear')
    print('Waiting for Start command from Control...')
    initialization()
    broker_dict = {'user': 'mec', 'pw': 'password', 'sub_topic': 'cache/#', 'ip': broker_ip}
    messenger = BrokerCom(**broker_dict)
    h1 = Thread(target=messenger.broker_loop)
    h1.start()

    collaborative_cache = CollaborativeCache(no_mec=no_mec)
    request_data = pd.read_csv(f'request_data.csv')
    # no_reqs = int(request_data.shape[0] * 0.3)  # testing data is 30 % => 67,259
    no_reqs = 20000  # testing data is 30 % => 67,259
    n = 5 * 8 * 10
    no_of_requests = (no_reqs // n) * n  # No of requests should be divisible by 5, 10, 15 MECs |  67,200

    network_cost_record = Delay(window_size=200)
    content_name_server = '192.168.205.130'
    # (self, cache_size, max_freq, avg_max, window_size, content_name_server, delay)
    d_slice = data_slice(no_mec=no_mec, total_req_no=no_of_requests, initial=request_data.shape[0] - no_of_requests)
    store = LocalCache(cache_size=50, max_freq=15, avg_max=100, window_size=20,
                       content_name_server=content_name_server,
                       delay=network_cost_record)
    # pickle_in = open('dict.pickle','rb')
    # example_dict = pickle.load(pickle_in)
    arrival_dist = arrival_distribution()
    s = d_slice[1] - d_slice[0]
    for i in range(d_slice[0], d_slice[1]):
        print(f"requesting-> {request_data['movieId'][i]}")
        store.request(request_data['movieId'][i])
        cpu_record.add_data()
        memory_record.add_data()
        time.sleep(arrival_dist.__next__())
        s -= 1
        print(f'\nRemaining -> {s} \n')
    store.experiment_details()
    save_data(mem=memory_record.data_set, cpu=cpu_record.data_set, delay=network_cost_record.data_set, no=no_mec,
              cache_details=store.outcome_details())

    messenger.run = 0
    print('experiment concluded!')


def main():
    global broker_ip

    parser = argparse.ArgumentParser()  # --n=5
    parser.add_argument('--n', type=int, default=1, help='Number of MEC nodes')
    parser.add_argument('--ip', type=str, default='localhost', help='broker ip address')
    args = parser.parse_args()
    broker_ip = args.ip
    run(no_mec=args.n)


if __name__ == '__main__':
    main()
