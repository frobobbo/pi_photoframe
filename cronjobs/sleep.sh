#!/bin/sh
# sleep.sh
# stop the slideshow and turn off the display 

sudo pkill -f fbi
sudo /opt/vc/bin/tvservice -o
