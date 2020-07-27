#!/usr/bin/env bash

#apt install unzip libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev
#apt install libncursesw5-dev xz-utils python-pip python-virtualenv python3-pip python3-venv python-dev python3-dev
#apt install libopenblas-base libopenblas-dev
#sudo apt install curl gnupg
#curl -f https://bazel.build/bazel-release.pub.gpg | sudo apt-key add -
#echo "deb [arch=amd64] https://storage.googleapis.com/bazel-apt stable jdk1.8" | sudo tee /etc/apt/sources.list.d/bazel.list
#sudo apt update && sudo apt install bazel
#sudo apt update && sudo apt full-upgrade
#sudo apt install openjdk-11-jdk

git clone https://github.com/tensorflow/tensorflow.git
cd tensorflow
./configure



bazel build //tensorflow/tools/pip_package:build_pip_package
./bazel-bin/tensorflow/tools/pip_package/build_pip_package /tmp/tensorflow_pkg
pip install /tmp/tensorflow_pkg/tensorflow-version-tags.whl