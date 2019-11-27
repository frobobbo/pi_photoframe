import subprocess
import socket
import logging
import os
import re
from PIL import Image

def makeFullframe(filename):
    #Get the Name and Extenstion of the current file
    #Create the temp file
    name, ext = os.path.splitext(filename)
    filename_temp = "%s-frame%s" % (name, ext)

    #Get the size of the original image
    im = Image.open(filename)
    width, height = im.size
    print im.size
    print "Width: %i" % width
    print "Height: %i" % height

    #Set the Border parameters
    width_border = 15
    width_spacing = 3
    border = None
    borderSmall = None

    #Get Screen Resolution
    hdmi = subprocess.check_output(['tvservice', '-s'])
    print hdmi
    #state 0x120002 [TV is off]
    #state 0x12000a [HDMI DMT (81) RGB full 16:9], 1366x768 @ 60.00Hz, progressive
    state = hdmi.split(" ")[1]
    if state == "0x120002":
        #Display is Off
        #Default to last used Resolution - should be stored in a System.Config.ini file...
        print "Display is off"
    elif state == "0x12000a":
        #Display is on, get Resolution
        print "Display is on"
        hdmiRes = hdmi.split(", ")[1].split(" ")[0]
        print hdmiRes
        displayWidth=int(hdmiRes.split("x")[0])
        displayHeight=int(hdmiRes.split("x")[1])
        print "DisplayWidth: %s" % displayWidth
        print "DisplayHeight: %s" % displayHeight

    # Calculate the ratio of the original image, in order to size appropriately
    ar = (float)(width) / (float)(height)

    # Determine how the resolution of the image compares to that of the display
    # If the Width of the Image is larger than Display resize using the Ratio
    if width > displayWidth:
        adjWidth = int(displayWidth)
        adjHeight = int(float(displayWidth) / ar)
    # The Width of the Image is smaller than the Display, there size it appropriately
    else:
        adjWidth = int(float(displayHeight) * ar)
        adjHeight = int(displayHeight)

    print "Adjusted Width: %i"%int(adjWidth)
    print "Adjusted Height: %i"%int(adjHeight)

    if adjHeight < displayHeight:
        border = '0x%d' % width_border
	spacing = '0x%d' % width_spacing
	padding = ((displayHeight - adjHeight) / 2 - width_border)
	print('Landscape image, reframing (padding required %dpx)' % padding)
    elif adjWidth < displayWidth:
        border = '%dx0' % width_border
	spacing = '%dx0' % width_spacing
	padding = ((displayWidth - adjWidth) / 2 - width_border)
	print('Portrait image, reframing (padding required %dpx)' % padding)
    else:
        logging.debug('Image is fullscreen, no reframing needed')
	return False

    if padding < 100:
        print('That\'s less than 100px so skip reframing (%dx%d => %dx%d)', width, height, adjWidth, adjHeight)
	return False
    zoomOnly = False
    if padding < 60:
        zoomOnly = True
        
    cmd = None
    try:
        # Time to process
        if zoomOnly:
            cmd = [
                'convert',
                filename + '[0]',
                '-resize',
                '%sx%s^' % (displayWidth, displayHeight),
                '-gravity',
                'center',
                '-crop',
                '%sx%s+0+0' % (displayWidth, displayHeight),
                '+repage',
                filename_temp
	    ]
        else:
            cmd = [
                'convert',
                filename + '[0]',
                '-resize',
                '%sx%s^' % (str(displayWidth), str(displayHeight)),
                '-gravity',
                'center',
                '-crop',
                '%sx%s+0+0' % (str(displayWidth), str(displayHeight)),
                '+repage',
                '-blur',
                '0x12',
                '-brightness-contrast',
                '-20x0',
                '(',
                filename + '[0]',
                '-bordercolor',
                'black',
                '-border',
                border,
                '-bordercolor',
                'black',
                '-border',
                spacing,
                '-resize',
                '%sx%s' % (str(displayWidth), str(displayHeight)),
                '-background',
                'transparent',
                '-gravity',
                'center',
                '-extent',
                '%sx%s' % (str(displayWidth), str(displayHeight)),
                ')',
                '-composite',
                filename_temp
	    ]
    except Exception, e:
        print('Error building command line: %s')%str(e)
        print('Filename: ' + repr(filename))
        print('Filename_temp: ' + repr(filename_temp))
        print('border: ' + repr(border))
        print('spacing: ' + repr(spacing))
        return False

    try:
        subprocess.check_output(cmd, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        print('Unable to reframe the image')
        print('Output: %s' % repr(e.output))
        return False

    os.rename(filename_temp, filename)
    return True

#makeFullframe('/home/pi/PhotoFrame/photos/IMG_0843.JPG')
#makeFullframe('/home/pi/PhotoFrame/photos/IMG_0855.JPG')
