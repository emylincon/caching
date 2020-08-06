#!/usr/bin/env bash

#  python:3.6-alpine
apk update && apk upgrade
apk add --no-cache --repository http://dl-3.alpinelinux.org/alpine/edge/testing hdf5 hdf5-dev
apk --no-cache --update-cache add gcc gfortran python3 python3-dev py-pip build-base wget freetype-dev libpng-dev openblas-dev
apk add jpeg-dev zlib-dev freetype-dev lcms2-dev openjpeg-dev tiff-dev tk-dev tcl-dev
apk --update add libxml2-dev libxslt-dev libffi-dev gcc musl-dev libgcc openssl-dev curl
ln -s /usr/include/locale.h /usr/include/xlocale.h
pip3 install cython
apk add g++ bzip2 harfbuzz
apk add linux-headers
pip3 install --upgrade pip
python3 -m pip install --upgrade setuptools
pip3 install --no-cache-dir  --force-reinstall -Iv grpcio
pip3 install https://storage.googleapis.com/tensorflow/linux/cpu/tensorflow-1.13.1-cp36-cp36m-linux_x86_64.whl
pip3 install scipy pandas
pip3 install mlxtend
pip3 install paramiko paho-mqtt requests
apk add wget