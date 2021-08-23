#!/bin/bash
echo "Starting the service..."
python3 /home/umbrel/umbrel-crypto-display/scripts/cryptoprice.py >/dev/null 2>&1
(crontab -u umbrel -l ; echo "*/5 * * * * python3 /home/umbrel/umbrel-crypto-display/scripts/cryptoprice.py >/dev/null 2>&1") | crontab -u umbrel -
sudo ./slideshow.sh &
