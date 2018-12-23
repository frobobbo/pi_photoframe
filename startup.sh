#!/bin/sh
# startup.sh
# launch the photo fram python script

# download the latest config file
# TODO: This URL should and frameID should be pulled from a Global Config file
curl -X POST -F "frameID=1" https://auth.cstoneweb.com/getConfig.php -o ./PhotoFrame/config.ini

# download the latest user dats
sudo -u pi python /home/pi/PhotoFrame/getGoogleCreds.py

#launch the python script to download the files
sudo -u pi python /home/pi/PhotoFrame/launch.py

# stop the bootscreen service
sudo service bootscreen stop

#launch the fbi slideshow
sudo fbi -T 1 -noverbose -a -t 60 -u ~/PhotoFrame/photos/*
