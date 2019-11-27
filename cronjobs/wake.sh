#!/bin/sh
# wake.sh
# turn the display on and restart the slideshow

sudo /opt/vc/bin/tvservice -p; fbset -depth 8; fbset -depth 16

# execute startup
sh /home/pi/startup.sh > /home/pi/startuplog 2>&1
