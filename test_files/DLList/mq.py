import hashlib
import math


# A linked list node
class Node:
    # Constructor to create a new node
    def __init__(self, data):
        self.data = data
        self.next = None
        self.prev = None
        self.id = self.get_hash()
        self.count = 0
        self.access_time = 0
        self.expire = 0
        self.queue = 0

    def get_hash(self):
        y = str.encode(str(self.data))
        ha = hashlib.sha256(y)
        hash_no = ha.hexdigest()
        return hash_no

    @property
    def details(self):
        d = lambda x: None if x is None else x.data
        return {'data': self.data, 'queue_no': self.queue, 'next': d(self.next), 'prev': d(self.prev),
                'count': self.count}

    def set_queue_num(self):
        max_value = 8
        value = math.floor(math.log(self.count, 2))
        if value > max_value:
            self.queue = max_value
        else:
            self.queue = value


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


class MQ:
    def __init__(self, cache_size):
        self.queue_length = 8
        self.cache_size = cache_size
        self.history = {'fifo': []}
        self.chain = {i: LRUChain() for i in range(0, self.queue_length + 1)}
        self.table = {}
        self.cur_time = 0
        self.life_time = {'count': 0, 'life_time': 0}   # default lifetime is self.length if life_time = 0
        self.length = 0
        self.hit = 0
        self.miss = 0

    @property
    def history_size(self):
        return 4 * self.length

    def add_history(self, node):
        if len(self.history) >= self.history_size:
            self.history.pop(self.history['fifo'].pop(0))
        self.history['fifo'].append(node.id)
        self.history[node.id] = node

    def cal_life_time(self, node):
        """:arg
        the peak temporal distance is defined as the
        temporal distance that is greater than the number of cache blocks and that has the
        most number of accesses
        """
        temp_distance = self.cur_time - node.access_time
        if temp_distance > self.length and node.count+1 > self.life_time['count']:
            self.life_time = {'count': node.count+1, 'life_time': temp_distance}

    @property
    def l_time(self):
        return self.length if self.life_time['life_time'] == 0 else self.life_time['life_time']

    def push(self, data):
        new_node = Node(data)

        if new_node.id in self.table:
            # new_node = self.table[new_node.id]
            new_node = self.chain[new_node.queue].delete_node(new_node)  # self.table[new_node.id]
            new_node.prev, new_node.next = None, None
            self.cal_life_time(new_node)
            self.hit += 1
            print('hit')

        else:
            if new_node.id in self.history:
                self.history['fifo'].remove(new_node.id)
                new_node = self.history.pop(new_node.id)
                new_node.prev, new_node.next = None, None
            self.table[new_node.id] = new_node
            self.length += 1
            self.miss += 1
            print('miss')
            self.maintain_cache_size()

        new_node.count += 1
        new_node.set_queue_num()
        self.chain[new_node.queue].push(new_node)
        new_node.expire = self.cur_time + self.l_time
        new_node.access_time = self.cur_time
        self.cur_time += 1
        self.adjust()

    def maintain_cache_size(self):
        if self.length > self.cache_size:
            victim = self.evict()
            print('evicted: ', victim.data)
            self.add_history(victim)
            self.length -= 1
            self.table.pop(victim.id)

    def adjust(self):
        for no in range(1, self.queue_length):
            if self.chain[no].tail:
                if self.chain[no].tail.expire < self.cur_time:
                    node = self.chain[no].delete_node(self.chain[no].tail)
                    node.prev, node.next = None, None
                    node.queue -= 1
                    node.access_time = self.cur_time + self.l_time
                    self.chain[no-1].push(node)

    def evict(self):
        for chain in self.chain.values():
            if chain.tail:
                return chain.delete_node(chain.tail)

    def hit_ratio(self):
        return round((self.hit/(self.hit+self.miss))*100, 2)

    def data_display(self):
        return {i: self.chain[i].list() for i in self.chain}

    def details_display(self):
        return {i: self.chain[i].details() for i in self.chain}


# mq_chain = MQ(cache_size=7)
# p_list = [i for i in range(1, 8)] + [1, 1, 5, 6, 1, 2, 8, 3, 4, 7, 5, 3, 2] + [1,5,7,2,3,5,1,3,7,2]
#
# for j in p_list:
#     mq_chain.push(j)
#     print(f'\ndata ({j}) ->', mq_chain.data_display())
#     print(f'data ({j}) ->', mq_chain.details_display())
#
# print('\nHit ratio: ', mq_chain.hit_ratio())

