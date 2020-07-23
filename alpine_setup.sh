#!/usr/bin/env bash

apk update && apk upgrade
echo "http://dl-8.alpinelinux.org/alpine/edge/community" >> /etc/apk/repositories
apk --no-cache --update-cache add gcc gfortran python3-dev py-pip build-base wget freetype-dev libpng-dev openblas-dev
ln -s /usr/include/locale.h /usr/include/xlocale.h
pip3 install numpy scipy pandas matplotlib
pip3 install mlxtend
pip3 install paramiko
pip3 install paho-mqtt
pip3 install requests