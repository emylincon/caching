#!/usr/bin/env bash

clear
echo '============ Preparing your MEC Platform =============='
sleep 3
echo "\nupdating repository...\n"
apt update && apt upgrade -y

echo -e "installing python3...\n"
apt install python3 -y
apt install python3-pip -y

echo "installing required python3 packages..."
echo "(drawnow, psutil, matplotlib, paramiko, pyfiglet, numpy)\n"
pip3 install drawnow
apt install python3-psutil -y
apt install python3-paramiko -y
apt install python3-pyfiglet -y
apt install python3-numpy -y
pip3 install paho-mqtt
pip3 install netifaces
pip3 install mlxtend
pip3 install pandas
pip3 install requests
pip3 install wget
echo "installing openssh...\n"
apt install openssh-client -y
apt install openssh-server -y
pip3 install --upgrade pip
pip3 install tensorflow==2.2.0
pip3 install numpy scipy scikit-learn pillow h5py
pip3 install keras==2.3.1
pip3 install matplotlib=3.3.2

echo "installing network tools..."
echo "(wget, apt-utils, iputils-ping, net-tools, nmap)\n"
apt install wget -y
apt install apt-utils -y
apt install iputils-ping -y
apt install net-tools -y
apt install nano -y
apt install nmap -y
clear
echo "starting ssh server..\n"
sleep 1.5
/etc/init.d/ssh start
echo '============= All done.. Ready to use! ==============='