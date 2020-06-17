import time
ref = [1,2,1,1,2,3,1,1,3,5,6,1,2,4,2,3,5,2,2,5,2]
#ref = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1]

cache_store = {}
hit = 0
miss = 0
cache_size = 3


def hit_ratio():
    print('Hit ratio: ', round((hit/len(ref)*100)), '%')


for i in ref:
    if i in cache_store:
        hit += 1
        cache_store[i] = time.time()
        print('hit')
    else:
        print('miss')
        miss += 1
        if len(cache_store) >= cache_size:
            del cache_store[min(cache_store, key=cache_store.get)]
        cache_store[i] = time.time()
    time.sleep(0.1)


hit_ratio()