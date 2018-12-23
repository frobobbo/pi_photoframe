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
from pathlib import Path

from datetime import datetime, timedelta
#from urllib.request import urlopen


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

def checkFileDate(url):
	req = urllib2.Request(url)
	url_handle = urllib2.urlopen(req)
	headers = url_handle.info()
 
	last_modified = headers.getheader("Last-Modified")
	print last_modified

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
		uDatUrl = datURL+gUserID+'.dat'
		uDatFile = Path(os.path.join(configdir,gUserID+'.dat'))
		if uDatFile.exists():
			print "File Exists - do Nothing"
		else:
			print "File not found - Download"
			urllib.urlretrieve(uDatUrl,os.path.join(configdir,gUserID+'.dat'))
	
#Download photos from Google Photos Album
if Config.get('Plugins','GooglePhotos') == 'True':
	DownloadAuthfromGoogle()