#!/bin/sh
# wake.sh
# turn the display on and restart the slideshow

sudo /opt/vc/bin/tvservice -p; fbset -depth 8; fbset -depth 16
sudo -u pi python /home/pi/PhotoFrame/launch.py
