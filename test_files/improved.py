import hashlib
import math
import heapq
import time


class Heap:
    def __init__(self):
        self.heap = []
        heapq.heapify(self.heap)

    def push(self, item):
        heapq.heappush(self.heap, item)

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

    def remove(self, item):
        self.heap.remove(item)
        heapq.heapify(self.heap)

    @property
    def total_count(self):
        return sum(self.heap)


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

    @staticmethod
    def retrieval_cost(file_size):
        """:arg
        file size can be calculated by the number of characters in the file.
        Each character represents 1 byte
        """
        return 2 + (file_size/536)


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
        self.sorted_freq = Heap()
        self.history = FIFO(cache_size*8)
        self.chain = {}
        self.table = {}
        self.length = 0
        self.hit = 0
        self.miss = 0
        self.avg_max = 4

    @property
    def average_count(self):
        return round(self.sorted_freq.total_count / self.length, 2)

    def maintain_count(self):
        if self.average_count > self.avg_max:
            # print('start: ', self.details_display())
            new_chain = {}
            freq_list = Heap()

            def reduce_count(node):
                while node:
                    node.reduce_count()
                    if node.count not in new_chain: new_chain[node.count] = LRUChain()
                    new_chain[node.count].push(node)
                    if node.count not in freq_list.heap: freq_list.push(node.count)
                    node = node.prev

            for chain in self.chain.values():
                reduce_count(chain.tail)
            self.history.reduce_count()
            self.chain = new_chain
            self.sorted_freq = freq_list

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

            if self.chain[new_node.count].length == 0:
                self.chain.pop(new_node.count)
                self.sorted_freq.remove(new_node.count)
            if new_node.count+1 not in self.sorted_freq.heap:
                self.sorted_freq.push(new_node.count+1)
            # print('hit')

        else:
            # print('miss')
            if self.length >= self.cache_size:
                decision = self.maintain_cache_size(new_node)
            if decision[0] == 1:
                new_node = new_node if decision[1] is None else decision[1]
                if new_node.count+1 not in self.sorted_freq.heap:
                    self.sorted_freq.push(new_node.count+1)
                self.table[new_node.id] = new_node
                self.length += 1
            self.miss += 1

        new_node.count += 1
        if decision[0] == 1:
            try:
                self.chain[new_node.count].push(new_node)
            except KeyError:
                self.chain[new_node.count] = LRUChain()
                self.chain[new_node.count].push(new_node)
        self.maintain_count()

    def maintain_cache_size(self, node):
        cache_decision = 0  # 0 means don't cache, 1 means cache
        if node.id in self.history.table:
            node = self.history.delete(node)
            node.next, node.prev = None, None
            victim = self.chain[self.sorted_freq.heap[0]].tail
            print(self.sorted_freq.heap)
            print('comparing: ', node.data, victim.data, '->', self.data_display())
            if node.last_access > victim.last_access:
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
            self.sorted_freq.remove(victim.count)

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
    print('avg_freq', my_cache.average_count)
    time.sleep(0.0000001)


print(my_cache.hit_ratio())