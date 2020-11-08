import hashlib
import math

'''
This is a implementation of the FBR algorithm in python
'''


# A linked list node
class Node:
    # Constructor to create a new node
    def __init__(self, data):
        self.data = data
        self.next = None
        self.prev = None
        self.id = self.get_hash()
        self.new = False
        self.old = False
        self.count = 0

    def get_hash(self):
        y = str.encode(str(self.data))
        ha = hashlib.sha256(y)
        hash_no = ha.hexdigest()
        return hash_no

    @property
    def details(self):
        d = lambda x: None if x is None else x.data
        return {'data': self.data, 'new': self.new, 'old': self.old, 'next': d(self.next), 'prev': d(self.prev),
                'count': self.count}

    def reduce_count(self):
        self.count = math.ceil(self.count / 2)


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


class CountChain:      # replace and maintain count and maintain boundary
    def __init__(self, cache_size):
        self.length = 0
        self.cache_size = cache_size
        self.sections = [.4, .3]
        self.section_count = [round(i * self.cache_size) for i in self.sections]  # middle, old
        self.new_boundary = None
        self.old_boundary = None
        self.total_count = 0
        self.a_max = 3  # maximum average of counts
        self.c_max = 8  # maximum chain count
        self.table = {}  # to check if a block exists | stores the reference of a block if it exists {id: node}
        self.chain = {i: LRUChain() for i in range(1, self.c_max+1)}
        self.hit = 0
        self.miss = 0

    @property
    def average_count(self):
        return round(self.total_count / self.length, 2)

    def maintain_count(self):
        if self.average_count > self.a_max:
            # print('start: ', self.details_display())
            new_chain = {i: LRUChain() for i in range(1, self.c_max+1)}

            def reduce_count(node):
                while node:
                    node.reduce_count()
                    new_chain[node.count].push(node)
                    node = node.prev

            for chain in self.chain.values():
                reduce_count(chain.tail)
            self.chain = new_chain
            # print('end: ', self.details_display())
            # print('b', self.total_count, self.average_count)
            self.total_count = math.ceil(self.total_count / 2)
            # print('a', self.total_count, self.average_count)

    def find_match(self, count, old, new, boundary, new_node):
        tails = [boundary.prev] + [self.chain[i].tail for i in range(count + 1, self.c_max + 1)] + [self.chain[i].tail for i in range(1, count)] + [self.chain[count].tail]
        # print(tails)

        # print({i:self.chain[i].list() for i in self.chain})

        def find(n_node):
            while n_node is not None:
                if n_node.id == new_node.id:
                    n_node = n_node.prev
                    continue
                if (n_node.old is old) and (n_node.new is new):
                    return n_node
                n_node = n_node.prev
            return None

        for tail in tails:
            match = find(tail)
            if match is not None:
                return match

    def maintain_boundary(self, new_node, status, replace):    # status => hit or miss
        if self.length > sum(self.section_count):
            # print(self.new_boundary.data, self.old_boundary.data)

            if (status == 'miss' and self.length == self.cache_size and replace is True) or (status == 'hit' and new_node.old is True):
                # middle and new boundary changes
                self.old_boundary = self.find_match(count=self.old_boundary.count, old=False, new=False,
                                                    boundary=self.old_boundary, new_node=new_node)
                self.old_boundary.old = True
                # print('new old', self.old_boundary.data)
                self.new_boundary = self.find_match(count=self.new_boundary.count, old=False, new=True,
                                                    boundary=self.new_boundary, new_node=new_node)
                self.new_boundary.new = False

            elif status == 'hit' and new_node.new is True:
                pass    # no boundary changes
            elif (status == 'hit') and (new_node.old is False) and (new_node.new is False):
                # only middle boundary changes | status is hit and new_node is in the middle
                self.new_boundary = self.find_match(count=self.new_boundary.count, old=False, new=True,
                                                    boundary=self.new_boundary, new_node=new_node)
                self.new_boundary.new = False

            new_node.new, new_node.old = True, False

        elif self.length == sum(self.section_count):
            self.new_boundary = new_node
        elif self.length == self.section_count[1]:
            self.old_boundary = new_node
            new_node.old = True
        elif self.length <= self.section_count[1]:
            new_node.old = True

    def maintain_cache_size(self):
        if self.length > self.cache_size:
            victim = self.find_victim()
            self.total_count -= victim.count
            self.length -= 1
            self.table.pop(victim.id)
            self.chain[victim.count].delete_node(victim)
            return True

    def find_victim(self):
        def find_match(n_node):
            while n_node is not None:
                # print('victim finder', n_node.data, n_node.old)
                if n_node.old is True:
                    return n_node
                n_node = n_node.prev
        for no in range(1, self.c_max+1):
            chain = self.chain[no]
            node = find_match(chain.tail)
            if node:
                return node

    def push(self, data):
        # creating boundaries and labelling new and old sections
        new_node = Node(data)
        status = 'miss'
        if new_node.id in self.table:
            new_node = self.table[new_node.id]
            new_node = self.chain[new_node.count].delete_node(new_node)         # self.table[new_node.id]
            new_node.prev, new_node.next = None, None
            self.hit += 1
            status = 'hit'
        else:
            self.table[new_node.id] = new_node
            self.length += 1
            self.miss += 1

        replace = self.maintain_cache_size()

        if not new_node.new:
            new_node.count += 1
            self.total_count += 1

        self.chain[new_node.count].push(new_node)

        self.maintain_count()  # maintains the average count

        self.maintain_boundary(new_node=new_node, status=status, replace=replace)

    def freq_count_display(self):
        return {i.data: i.count for i in self.table.values()}

    def data_display(self):
        return {i: self.chain[i].list() for i in self.chain}

    def details_display(self):
        return {i: self.chain[i].details() for i in self.chain}

    def hit_ratio(self):
        return round((self.hit/(self.hit+self.miss))*100, 2)


# d_l = CountChain(7)
# # for j in range(8):
# #     d.push(j)
# # print(d.new_boundary.data, d.old_boundary.data)
# # print('f', d.freq_count_display())
#
# p_list = [i for i in range(1, 8)] + [1, 1, 5, 6, 1, 2, 8, 3, 4, 7, 5, 3, 2] + [1,5,7,2,3,5,1,3,7,2]
# n_n = lambda x: None if x is None else x.data
# for i in p_list:
#     d_l.push(i)
#     print(f'\nboundary {i} | old-> {n_n(d_l.old_boundary)}  | new-> {n_n(d_l.new_boundary)}')
#     print(f'details {i}: ', d_l.details_display())
#
# print('f_count:', d_l.freq_count_display())
# print('d_data:', d_l.data_display())
# print(d_l.average_count)
# print(len(d_l.table))
# print(d_l.hit_ratio())