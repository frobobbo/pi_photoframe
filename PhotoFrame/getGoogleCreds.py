import argparse
import configparser
import filecmp
import getpass
import glob
import httplib2
import io
import json
import os
import platform
import string
import subprocess
import tempfile
import textwrap
import time
import urllib
import urllib2
import webbrowser

from datetime import datetime, timedelta

########################################################################
#                                                                      #
#  Set Global variables and read in configuration data                 #
#                                                                      #
########################################################################

osType = platform.system()
print osType

if osType == "Windows":
	#Windows
	configdir = os.path.expanduser("~\Documents\PhotoFrame")
	fontName = "calibrib.ttf"
elif osType == "Darwin":
	#MacOS
	fontName = "/Library/Fonts/DejaVuSerif.ttf"
	configdir = os.path.expanduser("~/Documents/PhotoFrame")
else:
	#linux
	fontName = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
	configdir = os.path.expanduser("~/PhotoFrame")

datURL = "https://auth.cstoneweb.com/auths/"
Config = configparser.ConfigParser()
Config.read("config.ini")


########################################################################
#                                                                      #
#  Read in the configuration infromation, then download the necessary  #
#  configuration fiels.                                                #
#                                                                      #
########################################################################

def DownloadAuthfromGoogle():

	gUserCount = int(Config.get('GoogleUsers','Count'))
	for x in range(gUserCount):
		gUserID = Config.get('GoogleUser' + str(x+1),'userid')
		urllib.urlretrieve(datURL+gUserID+'.dat',os.path.join(configdir,gUserID+'.dat'))
	
#Download photos from Google Photos Album
if Config.get('Plugins','GooglePhotos') == 'True':
	DownloadAuthfromGoogle()