import hashlib
import math
import time
import random as r


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


class LFRU:

    def __init__(self, cache_size):
        self.cache_size = cache_size
        self.max_freq = 5
        self.history = FIFO(cache_size*8)
        self.chain = {}
        self.table = {}
        self.length = 0
        self.hit = 0
        self.miss = 0
        self.avg_max = 6
        self.min_freq = 1

    @property
    def average_count(self):
        return round(sum(self.chain.keys()) / len(self.chain), 2)

    def maintain_count(self):
        if self.average_count > self.avg_max:
            # print('start: ', self.details_display())
            new_chain = {}
            print('maintaining count... ..')

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

    def get_retrieval_cost(self, request):
        return r.randrange(5)
        #return 1

    def increment_count_decision(self, node):
        diff = 1
        print(f'loop list -> {list(range(node.count-1, 0, -1))}')
        for tf in range(node.count-1, 0, -1):
            try:
                q = self.chain[tf]
                print('in->', tf)
                break
            except KeyError:
                diff += 1
        if diff < self.max_freq:
            return True, diff
        else:
            return False, diff

    def push(self, data):
        # print(data)
        new_node = Node(data)
        decision = (1, None)
        if new_node.id in self.table:
            new_node = self.table[new_node.id]   # dont remove this, it is useful, even if you dont think it is
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
                print('incrementing ->', result)
                new_node.count += 1
            else:
                print('Not incrementing ->', result)
            # print('hit')

        else:
            # print('miss')
            new_node.retrieval_cost = self.get_retrieval_cost(data)
            if self.length >= self.cache_size:
                decision = self.maintain_cache_size(new_node)
            if decision[0] == 1:
                new_node = new_node if decision[1] is None else decision[1]
                if new_node.count+1 < self.min_freq:
                    if self.min_freq - self.max_freq > new_node.count+1:
                        new_node.count = self.min_freq - self.max_freq
                    self.min_freq = new_node.count+1
                new_node.count += 1
                print(f'incrementing new ->{new_node.count} | {self.chain.keys()}')
                self.table[new_node.id] = new_node
                self.length += 1
            else:
                new_node.count += 1
                print(f'incrementing new ->{new_node.count} | {self.chain.keys()}')
            self.miss += 1

        if decision[0] == 1:
            try:
                self.chain[new_node.count].push(new_node)
            except KeyError:
                self.chain[new_node.count] = LRUChain()
                self.chain[new_node.count].push(new_node)
        self.maintain_count()

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
            print(f'next min freq found -> {self.min_freq}')
        else:
            print(f'next min freq not found-> {self.min_freq} | {list(range(self.min_freq, self.min_freq + self.max_freq + 1))}')

    def maintain_cache_size(self, node):
        cache_decision = 0  # 0 means don't cache, 1 means cache
        if node.id in self.history.table:
            node = self.history.delete(node)
            node.next, node.prev = None, None
            min_queue = self.chain[self.min_freq]
            victim = min_queue.tail
            # print(self.sorted_freq.heap)
            # print('comparing: ', node.data, victim.data, '->', self.data_display())
            if (node.last_access > victim.last_access) or (node.retrieval_cost > victim.retrieval_cost):
                #print('before eviction ++++',  self.data_display() )
                self.evict(victim)
                victim.next, victim.prev = None, None
                self.history.push(victim)
                node.last_access = time.time()
                cache_decision += 1
                #print('evicted: ++++', victim.data, 'recap: ', self.data_display())
            else:
                node.last_access = time.time()
                self.history.push(node)

        else:
            self.history.push(node)
        return cache_decision, node

    def evict(self, victim):
        self.chain[victim.count].delete_node(victim)
        self.length -= 1
        self.table.pop(victim.id)
        if self.chain[victim.count].length == 0:
            self.chain.pop(victim.count)
            self.find_new_min_freq()

        return victim

    def hit_ratio(self):
        return round((self.hit/(self.hit+self.miss))*100, 2)

    def data_display(self):
        return {i: self.chain[i].list() for i in self.chain}

    def details_display(self):
        return {i: self.chain[i].details() for i in self.chain}


my_cache = LFRU(3)

#ref = [1,2,1,1,2,3,1,1,3,5,6,1,2,4,2,3,5,2,2,5,2,2,5,6,1,3,4]
ref = [1, 2, 4, 2, 2, 1, 2, 3, 2, 1, 1, 1, 1, 0, 4, 5, 1, 4, 0, 5, 4, 2, 5, 4, 4, 2, 3, 3, 3, 3, 1, 1, 1, 0, 1, 5, 1, 6, 3, 5, 0, 5, 1, 1, 2, 3, 0, 1, 1, 1, 1, 5, 5, 1, 2, 4, 1, 4, 2, 1, 5, 0, 3, 3, 2, 4, 3, 5, 3, 1]
#ref = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1]
for j in ref:
    my_cache.push(j)
    print(f'data ({j}) ->', my_cache.data_display())
    #print('avg_freq', my_cache.average_count)
    print(f'min freq ->', my_cache.min_freq)
    time.sleep(0.0000001)


print(my_cache.hit_ratio())