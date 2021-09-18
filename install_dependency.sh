#!/bin/bash
set -xe

sudo apt-get -y install \
  fbi \
  python3-pygame \
  python3-cachetools \
  python3-psutil \
  python3-requests \
  python3-dotenv \
  fonts-dejavu \
  python3-websockets

sudo pip3 install Pillow