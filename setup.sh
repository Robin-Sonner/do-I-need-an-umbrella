#!/bin/bash

sudo apt-get update
sudo apt-get install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get install -y python3.13 python3.13-venv
sudo apt-get install -y libxcb-cursor0 libgl1 libxkbcommon-x11-0 libglx-mesa0 libegl1 libfontconfig1 libxcb-xkb1 libxcb-icccm4 libxcb-keysyms1 libxcb-shape0 fonts-noto-color-emoji fonts-noto fontconfig

python3.13 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install ".[dev,gui]"
