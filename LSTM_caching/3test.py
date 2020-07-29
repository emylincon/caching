import pandas as pd
import time
import os
import subprocess as sp
import re
import random as r

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


def get_hostname():
    cmd = ['cat /etc/hostname']
    hostname = str(sp.check_output(cmd, shell=True), 'utf-8')[0:-1]
    return hostname


def fix():
    host = get_hostname()
    no = 10
    send_path = '/home/osboxes/results/'
    host_no = int(re.findall('[0-9]+', host)[0])
    for res in ['memory', 'cpu', 'delay']:
        os.system(f'zip results/{res}{host_no}_{no}.zip results/{res}/*')
        sp.run(
            ["scp", f'results/{res}{host_no}_{no}.zip', f"osboxes@192.168.200.101:{send_path}"])
        #time.sleep(r.uniform(1, 10))


fix()