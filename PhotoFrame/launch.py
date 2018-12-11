import argparse
import configparser
import filecmp
import gdata
import gdata.photos.service
import gdata.media
import gdata.geo
import gdata.gauth
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
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from gdata.photos.service import GPHOTOS_INVALID_ARGUMENT, GPHOTOS_INVALID_CONTENT_TYPE, GooglePhotosException

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw 

########################################################################
#                                                                      #
#  Set Global variables and read in configuration data                 #
#                                                                      #
########################################################################

osType = platform.system()

if osType == "Windows":
	#Windows
	configdir = os.path.expanduser("~\Documents\PhotoFrame")
	fontName = "calibrib.ttf"
else:
	#linux
	fontName = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
	configdir = os.path.expanduser("~/PhotoFrame")

currPhotoList = []
googlePhotoList = {}
googleCaptionList = {}
igPhotoList = {}

Config = configparser.ConfigParser()
Config.read("config.ini")


########################################################################
#                                                                      #
#  Oauth routine to login to Google Photos/Picasa Web API              #
#                                                                      #
########################################################################

def OAuth2Login(client_secrets, credential_store, email):
    scope='https://picasaweb.google.com/data/'
    user_agent='picasawebuploader'

    storage = Storage(credential_store)
    credentials = storage.get()
    if credentials is None or credentials.invalid:
        flow = flow_from_clientsecrets(client_secrets, scope=scope, redirect_uri='urn:ietf:wg:oauth:2.0:oob')
        uri = flow.step1_get_authorize_url()
        webbrowser.open(uri)
        code = raw_input('Enter the authentication code: ').strip()
        credentials = flow.step2_exchange(code)

    if (credentials.token_expiry - datetime.utcnow()) < timedelta(minutes=5):
        http = httplib2.Http()
        http = credentials.authorize(http)
        credentials.refresh(http)

    storage.put(credentials)

    gd_client = gdata.photos.service.PhotosService(source=user_agent,
                                                   email=email,
                                                   additional_headers={'Authorization' : 'Bearer %s' % credentials.access_token})

    return gd_client

########################################################################
#                                                                      #
#  Get A current list of all the photos in the local photos directory  #
#  This will be used to determine if a photo needs to be downloaded    #
#                                                                      #
########################################################################

def getCurrentPhotoList():
	photoPath = os.path.join(configdir,"photos")
	global currPhotoList
	currPhotoList = next(os.walk(photoPath))[2]

########################################################################
#                                                                      #
#  Get A current list of all the photos in the local photos directory  #
#  This will be used to determine if a photo needs to be downloaded    #
#                                                                      #
########################################################################

def getGooglePhotoList():
	#Connect to Google Photos and get a list of photos in selected Album

        gUserCount = int(Config.get('GoogleUsers','Count'))
	for x in range(gUserCount):
        	global googlePhotoList
                email = Config.get('GoogleUser' + str(x+1),'userid')
                albumId = Config.get('GoogleUser' + str(x+1),'albumId')
                client_secrets = os.path.join(configdir, 'client_secrets.json')
                credential_store = os.path.join(configdir, 'GoogleUser' + str(x+1) + 'Credentials.dat')
	
                gd_client = OAuth2Login(client_secrets, credential_store, email)

                photos = gd_client.GetFeed('/data/feed/api/user/%s/albumid/%s?kind=photo&imgmax=1280' % (email, albumId))

        	for photo in photos.entry:
                	googlePhotoList[photo.title.text] = photo.content.src
                	if photo.summary.text:
                                googleCaptionList[photo.title.text] = photo.summary.text
                        #else:
                                #googleCaptionList[photo.title.text] = 'None'
                #print googlePhotoList

########################################################################
#                                                                      #
#   Get the list of photos from Google Photo Album                     #
#   Compare to the list of photos stored locally                       #
#   if local file is not longer in Google Album, remove from local     #
#                                                                      #
########################################################################
		
def RemovePhotosfromAlbum():

	global currPhotoList
	global googlePhotoList

	for pic in currPhotoList:
		if pic not in googlePhotoList and "jeff" not in pic:
			#delete photo from local album
			filePath = os.path.join(configdir,"photos",pic)
			os.remove(filePath)

########################################################################
#                                                                      #
#  Get A current list of all the photos in the local photos directory  #
#  This will be used to determine if a photo needs to be downloaded    #
#                                                                      #
########################################################################

def DownloadPhotosfromGoogle():
	#Download photos from Google Album
	#But only if they are not already downloaded
	global currPhotoList
	global googlePhotoList

	for pic in googlePhotoList:
		if pic not in currPhotoList or pic in googleCaptionList:
			#Download the photo
                        print "Download: " + str(googlePhotoList.get(pic))
			urllib.urlretrieve(googlePhotoList.get(pic), os.path.join(configdir,"photos",pic))
                        if pic in googleCaptionList:
                                print "Photo will be captioned with: " + str(googleCaptionList.get(pic))
                                addRoundedCaption(os.path.join(configdir,"photos",pic),googleCaptionList.get(pic))

########################################################################
#                                                                      #
#  Add semi-transparent caption box and enter caption in the box       #
#  Add rounded corners to the captions box                             #
#                                                                      #
########################################################################

def round_corner(radius, cfill):
        corner = Image.new('RGBA', (radius, radius), (0, 0, 0, 0))
        draw = ImageDraw.Draw(corner)
        draw.pieslice((0, 0, radius * 2, radius * 2), 180, 270, fill=cfill)
        return corner

def addRoundedCaption(photo,txt):
        img = Image.open(photo)
        lineSpacing = 27
	font = ImageFont.truetype(fontName, 24)
	lines = textwrap.wrap(txt, 60, break_long_words=False)

	imgCapH = len(lines) * lineSpacing + (2 * lineSpacing)
        imgCapW = img.width * .7
        
        imgCap = Image.new("RGBA", (int(imgCapW),int(imgCapH)))

        colorFill = (255,255,255,127)
        radius = 10
        
        pdraw = ImageDraw.Draw(imgCap)
        pdraw.rectangle(((0,0), (imgCapW,imgCapH)), fill=colorFill, outline=(255,255,255,255))
        
        corner = round_corner(radius, colorFill)
        imgCap.paste(corner, (0, 0))
        imgCap.paste(corner.rotate(90), (0, imgCapH - radius)) # Rotate the corner and paste it
        imgCap.paste(corner.rotate(180), (int(imgCapW - radius), imgCapH - radius))
        imgCap.paste(corner.rotate(270), (int(imgCapW - radius), 0))

       	n = 0
	for line in lines:
                text_size = pdraw.textsize(line, font)
                print "text size: " + str(text_size)
                print "Drawing text: " + line
		pdraw.text((((imgCapW - text_size[0])/2), lineSpacing+n),line,(0,0,0),font=font)
		n += lineSpacing


        img.paste(imgCap, (int((img.width - imgCapW)/2),20), mask=imgCap)
        img.save(photo)


def ajaxRequest(url=None):
	"""
	Makes an ajax get request.
	url - endpoint(string)
	"""
	req = urllib2.Request(url)
	f = urllib2.urlopen(req)
	response = f.read()
	f.close()
	return response	
		
def getIgPhotoList():
	global igPhotoList
	userid = Config.get('Instagram','userid')
	igToken = Config.get('Instagram','igToken')
	
	instagramURL = "https://api.instagram.com/v1/users/" + userid + "/media/recent/?access_token=" + igToken
	instagramJSON = ajaxRequest(instagramURL)
	instagramDict = json.loads(instagramJSON)
	instagramData = instagramDict["data"]
	# for every picture
	profilePic = ""
	filesDownloaded = 0
	yesterday = datetime.now() - timedelta(days = 720)
	yesterday_beginning = datetime(yesterday.year, yesterday.month, yesterday.day,0,0,0,0)
	yesterday_beginning_time = int(time.mktime(yesterday_beginning.timetuple()))
	global svPhotoPath
	svPhotoPath = ""
	
	for picDict in instagramData:
		# get the image url and current time
		image = picDict["images"]["standard_resolution"]
		caption = picDict["caption"]["text"]
		createTime = picDict["caption"]["created_time"]
		imageUrl = image["url"]
		profilePic = picDict["user"]["profile_picture"]
		if not picDict["location"]:
                        title = ""
                else:
                        title = picDict["location"]["name"]
                picDate = datetime.utcfromtimestamp(int(createTime)).strftime('%m/%d/%Y')
		if int(createTime) > int(yesterday_beginning_time):
			svPhotoName = "jeff-" + createTime + ".jpg"
			svPhotoPath = os.path.join(configdir,"photos",svPhotoName)
			svProfilePath = os.path.join(configdir,"photos","ProfPic.jpg")
			urllib.urlretrieve(imageUrl, svPhotoPath)
			urllib.urlretrieve(profilePic, svProfilePath)
			addTextToPhoto(svPhotoPath,caption,svProfilePath,title,picDate)
			filesDownloaded+=1
	
	if int(filesDownloaded) > 0:
		os.remove(svProfilePath)
			
def addTextToPhoto(photo,txt,prof,title,dt):
	img = Image.open(photo)
	#font = ImageFont.truetype(<font-file>, <font-size>)
	font = ImageFont.truetype(fontName, 18)
	titleFont = ImageFont.truetype(fontName, 26)
	dtFont = ImageFont.truetype(fontName, 20)
	#draw.text((x, y),"Sample Text",(r,g,b))

	foreground = Image.open(prof)
	finalImg = Image.new(mode='RGB',size=(1138,640),color=(0,0,0))
	finalImg.paste(img, (480,0))
	finalImg.paste(foreground, (20,0))
	
	lines = textwrap.wrap(txt, 50, break_long_words=False)
	n = 0

	finalImg.save(photo)
	pix = finalImg.load()
	
	draw = ImageDraw.Draw(finalImg)
	print photo
	
	draw.text((20, 180),title,(255,255,255),font=titleFont)
	draw.text((20, 220),dt,(255,255,255),font=dtFont)

	for line in lines:
		draw.text((20, 360+n),line,(255,255,255),font=font)
		n += 22
			
	finalImg.save(photo)
	
#Download photos from Instagram
if Config.get('Plugins','Instagram') == 'True':
        getIgPhotoList()

#Download photos from Google Photos Album
if Config.get('Plugins','GooglePhotos') == 'True':
        getCurrentPhotoList()
        getGooglePhotoList()
        RemovePhotosfromAlbum()
        DownloadPhotosfromGoogle()

#Start the slideshow		
#os.system('sudo fbi -T 1 -noverbose -a -t 60 -u ~/PhotoFrame/photos/*')
