import pandas as pd
import time
import os
import subprocess as sp
import re
import smtplib
from email.message import EmailMessage
import random as r


def send_email(file):
    EMAIL_ADDRESS = "spicetala@gmail.com"
    EMAIL_PASSWORD = ""

    msg = EmailMessage()

    msg['Subject'] = 'LSTM Caching size=50'

    msg['From'] = EMAIL_ADDRESS

    msg['To'] = 'suitelabb@gmail.com'
    msg.set_content('file')
    with open(file, 'rb') as f:
        file_data = f.read()
        # file_type = imghdr.what(f.name)
        file_name = f.name

    msg.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=file_name)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)


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
    for res in ['memory', 'cpu', 'delay', 'mems', 'cpus']:
        os.system(f'zip results/{res}{host_no}_{no}.zip results/{res}/*')
        send_email(f'results/{res}{host_no}_{no}.zip')
        # sp.run(
        #     ["scp", f'results/{res}{host_no}_{no}.zip', f"osboxes@192.168.200.101:{send_path}"])
        #time.sleep(r.uniform(1, 10))


fix()