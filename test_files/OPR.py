import time
ref = [1,2,1,1,2,3,1,1,3,5,6,1,2,4,2,3,5,2,2,5,2,2,5,6,1,3,4,6,3,2,0,1,5]
#ref = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1,4,3,2,0,1]
cache_store = {}
hit = 0
miss = 0
cache_size = 3


def hit_ratio():
    print('Hit ratio: ', round((hit/(len(ref)-6)*100)), '%')


for i in range(len(ref)-6):
    if ref[i] in cache_store:
        hit += 1
        print(f'{i} hit, cache: {list(cache_store.keys())}')
    else:
        miss += 1
        if len(cache_store) >= cache_size:
            for j in cache_store:
                cache_store[j] = ref[i + 1:].index(j) + 1
            del cache_store[max(cache_store, key=cache_store.get)]
        cache_store[ref[i]] = 0
        print(f'{i} miss, cache: {list(cache_store.keys())}')


hit_ratio()