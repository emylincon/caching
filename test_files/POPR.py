import time
#ref = [1,2,1,1,2,3,1,1,3,5,6,1,2,4,2,3,5,2,2,5,2,2,5,6,1,3,4]
ref = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1]
cache_store = {}
cache_history = {}  # id : {'steps': 1, 'freq':1}
hit = 0
miss = 0
cache_size = 3

'''
avg = how many steps it took to occur/ freq(how many times it has occurred)
avg = how many steps its been in the cache/ freq
avg = how many steps it took to occur/how many steps its been in the cache
avg = how many steps it took to occur/ freq(how many times it has occurred) * how long it has been in the cache
replace one with highest average
'''


def hit_ratio():
    print('Hit ratio: ', round((hit/(len(ref))*100)), '%')



#if there is no histroy dont cache yet. if there is history compare victim and new cache entry | last time it was fetched (45%)
for i in range(len(ref)):
    print('- '*100)
    if ref[i] in cache_store:
        hit += 1
        print(f'{ref[i]} hit, cache: {list(cache_store.keys())} ')
        cache_history[ref[i]][0] += 1     # increase frequency
        cache_history[ref[i]][1] = time.time()     # reinitialise history
        print(f'| scores : {cache_history}')

    else:
        miss += 1
        if len(cache_store) >= cache_size:
            if ref[i] in cache_history:      # cache only if its in history
                cache_store = {i: cache_history[i] for i in cache_store}
                replace = sorted(cache_store.items(), key=lambda e: (e[1][0], e[1][1]))[0][0] # replace min freq,history
                if cache_history[ref[i]][1] > cache_history[replace][1]:    # replace only if it has occurred more recently than the victim
                    del cache_store[replace]
                    cache_store[ref[i]] = []
                    print(f'scores: {cache_history} | {replace} replaced')
                else:
                    print(f'scores: {cache_history} |')  # new, old = {lst[ref[i]], lst[replace]} no replacement')
                cache_history[ref[i]][0] += 1
                cache_history[ref[i]][1] = time.time()  # reinitialise history

            elif ref[i] not in cache_history:
                cache_history[ref[i]] = [1, time.time()]  # initialise freq and history

        else:
            cache_store[ref[i]] = []
            #if ref[i] not in cache_history:
            cache_history[ref[i]] = [1, time.time()]



        print(f'{ref[i]} miss, cache: {list(cache_store.keys())}')
    time.sleep(0.1)


#lst = {}
#if there is no histroy dont cache yet. if there is history compare victim and new cache entry | last time it was fetched (45%)
# for i in range(len(ref)):
#     print('- '*100)
#     if ref[i] in cache_store:
#         hit += 1
#         print(f'{ref[i]} hit, cache: {list(cache_store.keys())} ')
#         for t in cache_history:
#             cache_history[t][1] += 1  # increase history
#         cache_history[ref[i]][0] += 1     # increase frequency
#         cache_history[ref[i]][1] = 1     # reinitialise history
#         lst[ref[i]] = i                   # reinitialise last entry
#         print(f'| scores : {cache_history}, last : {lst}')
#
#     else:
#         miss += 1
#         for t in cache_store:
#             cache_history[t][1] += 1     # increase history
#         if len(cache_store) >= cache_size:
#             if ref[i] in cache_history:      # cache only if its in history
#                 keys = list(cache_store)
#                 if cache_history[keys[0]][0]==cache_history[keys[1]][0]==cache_history[keys[2]][0]: # checks if all freq is equal
#                     cache_store = {i:cache_history[i] for i in cache_store}
#                     replace = max(cache_store.items(), key=lambda e: e[1][1])[0]  # select max history
#                 else:
#                     cache_store = {i: cache_history[i] for i in cache_store}
#                     s = sorted(cache_store.items(), key=lambda e:e[1][0])
#                     if s[0][1][0] == s[1][1][0]:     # checks if the two last freq is equal
#                         replace = max(s[:-1], key=lambda e:e[1][1])[0]     # select max history
#                     else:
#                         replace = s[0][0]
#
#                 if lst[ref[i]] > lst[replace]:    # replace only if it has occurred more recently than the victim
#                     del cache_store[replace]
#                     cache_store[ref[i]] = []
#                     print(f'scores: {cache_history} | {replace} replaced')
#                 else:
#                     print(f'scores: {cache_history} | new, old = {lst[ref[i]], lst[replace]} no replacement')
#                 cache_history[ref[i]][0] += 1
#                 lst[ref[i]] = i
#             elif ref[i] not in cache_history:
#                 cache_history[ref[i]] = [1, 1]  # initialise freq and history
#                 lst[ref[i]] = i
#         else:
#             cache_store[ref[i]] = []
#             if ref[i] not in cache_history:
#                 cache_history[ref[i]] = [1, 1]
#             lst[ref[i]] = i
#
#         print(f'{ref[i]} miss, cache: {list(cache_store.keys())} | last : {lst}')

# LFRU with history  (45%)
# for i in range(len(ref)):
#     print('- '*100)
#     if ref[i] in cache_store:
#         hit += 1
#         print(f'{ref[i]} hit, cache: {list(cache_store.keys())} ')
#         for t in cache_history:
#             cache_history[t][1] += 1  # increase history
#         cache_history[ref[i]][0] += 1     # increase frequency
#         cache_history[ref[i]][1] = 1     # reintialise history
#         print(f'| scores : {cache_history}')
#
#     else:
#         miss += 1
#         for t in cache_store:
#             cache_history[t][1] += 1     # increase history
#         if len(cache_store) >= cache_size:
#             keys = list(cache_store)
#             if cache_history[keys[0]][0]==cache_history[keys[1]][0]==cache_history[keys[2]][0]: # checks if all freq is equal
#                 cache_store = {i:cache_history[i] for i in cache_store}
#                 replace = max(cache_store.items(), key=lambda e: e[1][1])[0]  # select max history
#             else:
#                 cache_store = {i: cache_history[i] for i in cache_store}
#                 s = sorted(cache_store.items(), key=lambda e:e[1][0])
#                 if s[0][1][0] == s[1][1][0]:     # checks if the two last freq is equal
#                     replace = max(s[:-1], key=lambda e:e[1][1])[0]     # select max history
#                 else:
#                     replace = s[0][0]
#             print(f'scores: {cache_history} | {replace} replaced')
#             del cache_store[replace]
#         cache_store[ref[i]] = []
#         if ref[i] not in cache_history:
#             cache_history[ref[i]] = [1, 1]  # initialise freq and history
#         else:
#             cache_history[ref[i]][0] += 1
#
#         print(f'{ref[i]} miss, cache: {list(cache_store.keys())}')


# # LFRU without history  (45%)
# for i in range(len(ref)):
#     print('- '*100)
#     if ref[i] in cache_store:
#         hit += 1
#         print(f'{ref[i]} hit, cache: {list(cache_store.keys())} ')
#         for t in cache_store:
#             cache_store[t][1] += 1  # increase history
#         cache_store[ref[i]][0] += 1     # increase frequency
#         cache_store[ref[i]][1] = 1     # reintialise history
#         print(f'| scores : {cache_store}')
#
#     else:
#         miss += 1
#         for t in cache_store:
#             cache_store[t][1] += 1     # increase history
#         if len(cache_store) >= cache_size:
#             keys = list(cache_store)
#             if cache_store[keys[0]][0]==cache_store[keys[1]][0]==cache_store[keys[2]][0]:
#                 replace = max(cache_store.items(), key=lambda e: e[1][1])[0]
#             else:
#                 s = sorted(cache_store.items(), key=lambda e:e[1][0])
#                 if s[0][1][0] == s[1][1][0]:
#                     replace = max(s[:-1], key=lambda e:e[1][1])[0]
#                 else:
#                     replace = min(cache_store, key=cache_store.get)
#             print(f'scores: {cache_store} | {replace} replaced')
#             del cache_store[replace]
#
#         cache_store[ref[i]] = [1, 1]  # initialise freq and history
#
#         print(f'{ref[i]} miss, cache: {list(cache_store.keys())}')


# avg = how many steps it took to occur/ freq(how many times it has occurred) * how long it has been in the cache without replacement (35%)
# for i in range(len(ref)):
#     print('- '*100)
#     if ref[i] in cache_store:
#         hit += 1
#         print(f'{ref[i]} hit, cache: {list(cache_store.keys())}')
#         for t in cache_history:
#             cache_history[t]['hist'] += 1
#         cache_history[ref[i]]['freq'] += 1
#         cache_history[ref[i]]['hist'] = 1
#         cache_history[ref[i]]['steps'].append(i - cache_history[ref[i]]['l'])
#     else:
#         miss += 1
#         for t in cache_history:
#             cache_history[t]['hist'] += 1
#         if len(cache_store) >= cache_size:
#             for j in cache_store:
#                 cache_store[j] = (sum(cache_history[j]['steps'])/cache_history[j]['freq'])*cache_history[j]['hist']
#             replace = min(cache_store, key=cache_store.get)
#             print(f'history: {cache_history}')
#             print(f'scores: {cache_store} | {replace} replaced')
#             del cache_store[replace]
#         cache_store[ref[i]] = 0
#         if ref[i] not in cache_history:
#             cache_history[ref[i]] = {'steps': [1], 'freq': 1, 'hist': 1, 'l':i}
#         else:
#             cache_history[ref[i]]['steps'].append(i-cache_history[ref[i]]['l'])
#
#         print(f'{ref[i]} miss, cache: {list(cache_store.keys())}')


# avg = how many steps its been in the cache/ freq  (achieved 40%)
# for i in range(len(ref)):
#     if ref[i] in cache_store:
#         hit += 1
#         print(f'{i} hit, cache: {list(cache_store.keys())}')
#         cache_history[ref[i]]['freq'] += 1
#         for t in cache_history:
#             cache_history[t]['steps'] += 1
#     else:
#         miss += 1
#         if len(cache_store) >= cache_size:
#             for j in cache_store:
#                 cache_store[j] = cache_history[j]['steps']/cache_history[j]['freq']
#             del cache_store[max(cache_store, key=cache_store.get)]
#         cache_store[ref[i]] = 0
#         cache_history[ref[i]] = {'steps': 1, 'freq': 1}
#         for t in cache_history:
#             cache_history[t]['steps'] += 1
#         print(f'{i} miss, cache: {list(cache_store.keys())}')


hit_ratio()