import pandas as pd
import time
import os
import subprocess as sp


def run():

    print('Waiting for Start command from Control...')

    request_data = pd.read_csv(f'../request_data.csv')
    # no_reqs = int(request_data.shape[0] * 0.3)  # testing data is 30 % => 67,259
    no_reqs = 1000  # testing data is 30 % => 67,259
    length = request_data.shape[0]

    for i in range(length-no_reqs, length):
        print(f"requesting-> {request_data['movieId'][i]}")
        r, t = request_data['movieId'][i], request_data['timestamp'][i]

        cmd = [f'python3 play.py --r={r} --t="{t}"']
        ans = str(sp.check_output(cmd, shell=True), 'utf-8')[0:-1]

        # os.system(f'python3 play.py --r={r} --t="{t}"')
        # time.sleep(2)
        # file = open('out.txt', 'r')
        # ans = file.readlines()
        # file.close()
        print('prediction|| ->', float(ans))
        #print(float(ans))
        time.sleep(1)
        #print('answer ->', ans)
        print('remaining ->', i)


run()