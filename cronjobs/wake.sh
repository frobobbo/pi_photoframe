#!/bin/sh
# wake.sh
# turn the display on and restart the slideshow

sudo /opt/vc/bin/tvservice -p; fbset -depth 8; fbset -depth 16

# download the latest config file
curl -X POST -F "frameID=1" https://auth.cstoneweb.com/getConfig.php -o ./PhotoFrame/config.ini

#launch the python script to download the files
sudo -u pi python /home/pi/PhotoFrame/launch.py

#launch the fbi slideshow
sudo fbi -T 1 -noverbose -a -t 60 -u ~/PhotoFrame/photos/*
