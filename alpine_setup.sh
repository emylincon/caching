#!/usr/bin/env bash

apk update && apk upgrade
pip3 install mlxtend
pip3 install pandas
pip3 install paramiko
pip3 install paho-mqtt
pip3 install requests