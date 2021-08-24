#!/bin/bash
echo "Stopping the service..."
rm /home/umbrel/umbrel-crypto-display/images/*
crontab -u umbrel -l | grep -v 'python3 /home/umbrel/umbrel-crypto-display/scripts/cryptoprice.py'  | crontab -u umbrel -
sudo pkill slideshow.sh
sudo killall fbi
