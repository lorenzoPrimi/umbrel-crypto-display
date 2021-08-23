#!/bin/bash
if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi
apt-get -y install fbi
echo "dtoverlay=piscreen,speed=16000000,rotate=270" >> /boot/config.txt
echo "dtparam=spi=on"  >> /boot/config.txt
modprobe spi-bcm2835
chmod +x *.sh
echo "To see the screen, you need to reboot your Raspberry Pi. Do you want to do it now?"
select yn in "Yes" "No"; do
    case $yn in
        Yes ) reboot; break;;
        No ) exit;;
    esac
done
