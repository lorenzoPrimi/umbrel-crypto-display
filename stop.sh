#!/bin/bash
echo "Stopping the service..."
crontab -u umbrel -l | grep -v 'python3 /home/umbrel/umbrel-crypto-display/scripts/cryptoprice.py'  | crontab -u umbrel -
rm /home/umbrel/umbrel-crypto-display/images/*
sudo pkill slideshow.sh
sudo killall fbi
