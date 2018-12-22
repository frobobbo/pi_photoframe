#!/bin/sh
# startup.sh
# launch the photo fram python script

# stop the bootscreen service

# download the latest config file
curl -X POST -F "frameID=1" https://auth.cstoneweb.com/getConfig.php -o ./PhotoFrame/config.ini

#launch the python script to download the files
sudo -u pi python /home/pi/PhotoFrame/launch.py

#launch the fbi slideshow
sudo fbi -T 1 -noverbose -a -t 60 -u ~/PhotoFrame/photos/*
