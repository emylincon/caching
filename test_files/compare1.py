import matplotlib.pyplot as plt
import numpy as np
from DLList.count_chain import CountChain
from DLList.mq import MQ
import random as r
import concurrent.futures


fig = plt.figure()
ax1 = fig.add_subplot(121)
ax2 = fig.add_subplot(122)


def hit_ratio(hit, length):
    ratio = round(((hit/length)*100))
    #print('Hit ratio: ', ratio, '%')
    return ratio


def improved_cache(ref, cache_size):
    hit = 0
    miss = 0
    lst = {}
    cache_store = {}
    cache_history = {}  # id : {'steps': 1, 'freq':1}
    # if there is no histroy dont cache yet. if there is history compare victim and new cache entry | last time it was fetched (45%)
    for i in range(len(ref)):
        #print('- '*100)
        if ref[i] in cache_store:
            hit += 1
            # print(f'{ref[i]} hit, cache: {list(cache_store.keys())} ')
            for t in cache_history:
                cache_history[t][1] += 1  # increase history
            cache_history[ref[i]][0] += 1     # increase frequency
            cache_history[ref[i]][1] = 1     # reinitialise history
            lst[ref[i]] = i                   # reinitialise last entry
            # print(f'| scores : {cache_history}, last : {lst}')
        else:
            miss += 1
            for t in cache_store:
                cache_history[t][1] += 1     # increase history
            if len(cache_store) >= cache_size:
                if ref[i] in cache_history:      # cache only if its in history
                    keys = list(cache_store)
                    if cache_history[keys[0]][0]==cache_history[keys[1]][0]==cache_history[keys[2]][0]: # checks if all freq is equal
                        cache_store = {i:cache_history[i] for i in cache_store}
                        replace = max(cache_store.items(), key=lambda e: e[1][1])[0]  # select max history
                    else:
                        cache_store = {i: cache_history[i] for i in cache_store}
                        s = sorted(cache_store.items(), key=lambda e:e[1][0])
                        if s[0][1][0] == s[1][1][0]:     # checks if the two last freq is equal
                            replace = max(s[:-1], key=lambda e:e[1][1])[0]     # select max history
                        else:
                            replace = s[0][0]

                    if lst[ref[i]] > lst[replace]:    # replace only if it has occurred more recently than the victim
                        del cache_store[replace]
                        cache_store[ref[i]] = []
                        # print(f'scores: {cache_history} | {replace} replaced')
                    else:
                        pass
                        # print(f'scores: {cache_history} | new, old = {lst[ref[i]], lst[replace]} no replacement')
                    cache_history[ref[i]][0] += 1
                    lst[ref[i]] = i
                elif ref[i] not in cache_history:
                    cache_history[ref[i]] = [1, 1]  # initialise freq and history
                    lst[ref[i]] = i
            else:
                cache_store[ref[i]] = []
                if ref[i] not in cache_history:
                    cache_history[ref[i]] = [1, 1]
                lst[ref[i]] = i
            # print(f'{ref[i]} miss, cache: {list(cache_store.keys())} | last : {lst}')
    return hit_ratio(hit, hit+miss)


# LFRU without history  (45%)
def lfru(ref, cache_size):
    hit = 0
    miss = 0
    cache_store = {}
    for i in range(len(ref)):
        #print('- '*100)
        if ref[i] in cache_store:
            hit += 1
            #print(f'{ref[i]} hit, cache: {list(cache_store.keys())} ')
            for t in cache_store:
                cache_store[t][1] += 1  # increase history
            cache_store[ref[i]][0] += 1     # increase frequency
            cache_store[ref[i]][1] = 1     # reintialise history
            #print(f'| scores : {cache_store}')

        else:
            miss += 1
            for t in cache_store:
                cache_store[t][1] += 1     # increase history
            if len(cache_store) >= cache_size:
                keys = list(cache_store)
                if cache_store[keys[0]][0]==cache_store[keys[1]][0]==cache_store[keys[2]][0]:
                    replace = max(cache_store.items(), key=lambda e: e[1][1])[0]
                else:
                    s = sorted(cache_store.items(), key=lambda e:e[1][0])
                    if s[0][1][0] == s[1][1][0]:
                        replace = max(s[:-1], key=lambda e:e[1][1])[0]
                    else:
                        replace = min(cache_store, key=cache_store.get)
                #print(f'scores: {cache_store} | {replace} replaced')
                del cache_store[replace]

            cache_store[ref[i]] = [1, 1]  # initialise freq and history
            #print(f'{ref[i]} miss, cache: {list(cache_store.keys())}')
    return hit_ratio(hit, hit + miss)


def fifo(ref, cache_size):
    hit = 0
    miss = 0
    cache_store = []

    for i in ref:
        if i in cache_store:
            hit += 1
            #print('hit')
        else:
            #print('miss')
            miss += 1
            if len(cache_store) >= cache_size:
                cache_store.pop(0)
            cache_store.append(i)
    return hit_ratio(hit, hit + miss)


def opr(ref, cache_size):
    hit = 0
    miss = 0
    cache_store = {}
    ref = ref + list(set(ref))

    for i in range(len(ref) - len(set(ref))):
        if ref[i] in cache_store:
            hit += 1
            #print(f'{i} hit, cache: {list(cache_store.keys())}')
        else:
            miss += 1
            if len(cache_store) >= cache_size:
                for j in cache_store:
                    cache_store[j] = ref[i + 1:].index(j) + 1
                del cache_store[max(cache_store, key=cache_store.get)]
            cache_store[ref[i]] = 0
            #print(f'{i} miss, cache: {list(cache_store.keys())}')

    return hit_ratio(hit, hit + miss)


def lru(ref, cache_size):
    c_store = []
    hit = 0
    miss = 0
    for i in ref:
        if i in c_store:
            hit += 1
            c_store.remove(i)
            c_store.append(i)
        else:
            miss += 1
            if len(c_store) >= cache_size:
                c_store.pop(0)
            c_store.append(i)

    return hit_ratio(hit, hit + miss)


def lfu(ref, cache_size):
    hit = 0
    miss = 0
    cache_store = {}

    for i in ref:
        if i in cache_store:
            hit += 1
            cache_store[i] += 1
            #print('hit')
        else:
            #print('miss')
            miss += 1
            if len(cache_store) >= cache_size:
                del cache_store[min(cache_store, key=cache_store.get)]
            cache_store[i] = 1

    return hit_ratio(hit, hit + miss)


# avg = how many steps its been in the cache/ freq  (achieved 40%)
def asr(ref, cache_size):
    hit = 0
    miss = 0
    cache_store = {}
    cache_history = {}

    for i in range(len(ref)):
        if ref[i] in cache_store:
            hit += 1
            #print(f'{i} hit, cache: {list(cache_store.keys())}')
            cache_history[ref[i]]['freq'] += 1
            for t in cache_history:
                cache_history[t]['steps'] += 1
        else:
            miss += 1
            if len(cache_store) >= cache_size:
                for j in cache_store:
                    cache_store[j] = cache_history[j]['steps']/cache_history[j]['freq']
                del cache_store[max(cache_store, key=cache_store.get)]
            cache_store[ref[i]] = 0
            cache_history[ref[i]] = {'steps': 1, 'freq': 1}
            for t in cache_history:
                cache_history[t]['steps'] += 1
            #print(f'{i} miss, cache: {list(cache_store.keys())}')
    return hit_ratio(hit, hit + miss)


def fbr(ref, cache_size):
    fbr_chain = CountChain(cache_size)
    for data in ref:
        fbr_chain.push(data)

    return fbr_chain.hit_ratio()


def mq(ref, cache_size):
    mq_chain = MQ(cache_size)
    for data in ref:
        mq_chain.push(data)

    return mq_chain.hit_ratio()


def plot_me(data, ax, cols, ref, cache_size):
    width = 0.20
    ind = range(len(data))
    ax.bar(ind, list(data.values()), width, color=cols, alpha=0.4)
    ax.set_xticks(ind)
    ax.set_xticklabels([i.upper() for i in data])
    ax.set_ylabel("Hit Ratio", fontsize=15)
    j = 0
    for i in data:
        ax.text(j, data[i], f'{data[i]}%', rotation=0,
                ha="center", va="center", bbox=dict(boxstyle="round", ec=(0., 0., 0.), fc=(0.7, 0.9, 1.), ))
        j+=1
    ax.set_title(f'Comparision with {cache_size} cache size')


def zipf_dist(length, maximum):  # length = length of array, maximum = max number in array
    raw_list = np.random.zipf(1.35, size=length)
    formated_list = [i % maximum for i in raw_list]
    formated_list = list(np.array(formated_list) + 1)
    count_dict = {i: formated_list.count(i) for i in set(formated_list)}
    print(f'Frequency count: {count_dict}')
    return formated_list


def plot_comparison():
    ref = zipf_dist(1500, 40)
    c_sizes = [7,10]
    axs = [ax1, ax2]
    color = ['r', 'b', 'g', 'm', 'c', 'brown', 'k', 'lime']

    algos = {'opr': opr, 'lfu': lfu, 'lru': lru, 'lfru': lfru, 'ASR': asr, 'LFHH': improved_cache, 'FBR': fbr, 'MQ': mq}
    for i in range(len(axs)):
        ax = axs[i]
        data = {}
        cache_size = c_sizes[i]
        with concurrent.futures.ThreadPoolExecutor() as executor:

            results = {executor.submit(algos[func], ref, cache_size): func for func in algos}

        # runs process and returns result as they complete
        #for f in concurrent.futures.as_completed(results):
        for f in results:
            print(f.result(), results[f])
            data[results[f]] = f.result()
        plot_me(data, ax, color, ref, cache_size)
    plt.show()


plot_comparison()