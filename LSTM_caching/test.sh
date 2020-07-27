#!/usr/bin/env bash

wget http://bzip.org/1.0.6/bzip2-1.0.6.tar.gz
tar xpzf bzip2-1.0.6.tar.gz
cd bzip2-1.0.6
make
make -f Makefile-libbz2_so
make install PREFIX=/path/to/local # /usr/local by default