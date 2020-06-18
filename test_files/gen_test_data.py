import numpy as np
from datetime import datetime, timedelta
import random as r


def zipf_dist(length, maximum):  # length = length of array, maximum = max number in array
    raw_list = np.random.zipf(1.35, size=length)
    formated_list = [i % maximum for i in raw_list]
    count_dict = {i: formated_list.count(i) for i in set(formated_list)}
    # print(f'Frequency count: {count_dict}')
    return formated_list

def main():
    zipf_data = zipf_dist(length=3000, maximum=20)

    #path = r'C:\Users\emyli\PycharmProjects\Machine_learning'
    file = open(f'..\cache_request\cache_data.csv', 'w', encoding='utf-8')
    file.write(f"Cache_id\n")
    for i in range(len(zipf_data)):
        file.write(f"{zipf_data[i]+1}\n")  # zipf_data[i] + 1 to remove zero index
    file.close()

# print('zipf: ', zipf_dist(20, 6))
# print('Times: ', timestamps(20, 8))


if __name__ == '__main__':
    main()
