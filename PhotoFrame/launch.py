import argparse
import configparser
import filecmp
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
#import emoji

from apiclient.discovery import build
from datetime import datetime, timedelta
from oauth2client.client import flow_from_clientsecrets
from oauth2client import file, client, tools
from subprocess import call

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

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
	fontName = "DejaVuSans.ttf"
elif osType == "Darwin":
	#MacOS
	fontName = "/Library/Fonts/DejaVuSans.ttf"
	configdir = os.path.expanduser("~/Documents/PhotoFrame")
else:
	#linux
	fontName = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
	configdir = os.path.expanduser("~/PhotoFrame")
    
currPhotoList = []
googlePhotoList = {}
googleExtList = {}
googleCaptionList = {}
igPhotoList = {}


Config = configparser.ConfigParser()
Config.read(Config.read(os.path.join(configdir,"config.ini")))

########################################################################
#                                                                      #
#  Oauth routine to login to Google Photos API                         #
#                                                                      #
########################################################################

def OAuth2Login(client_secrets, credential_store, email):
# Setup the Photo v1 API
	SCOPES = 'https://www.googleapis.com/auth/photoslibrary.readonly'
	store = file.Storage(credential_store)
	creds = store.get()
	if not creds or creds.invalid:
		flow = client.flow_from_clientsecrets(client_secrets, SCOPES)
		creds = tools.run_flow(flow, store)

	if (creds.token_expiry - datetime.utcnow()) < timedelta(minutes=5):
		http = httplib2.Http()
		http = creds.authorize(http)
		creds.refresh(http)

	store.put(creds)
	service = build('photoslibrary', 'v1', http=creds.authorize(httplib2.Http()))

	return service

########################################################################
#                                                                      #
#  Get A current list of all the photos in the local photos directory  #
#  This will be used to determine if a photo needs to be downloaded    #
#                                                                      #
########################################################################

def getCurrentPhotoList():
	photoPath = os.path.join(configdir,"photos")
	print photoPath
	global currPhotoList
#	currPhotoList = next(os.walk(photoPath))[2]
	l=os.listdir(photoPath)
	try:
		l.remove('.DS_Store')
	currPhotoList=[x.split('.')[0] for x in l]
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
		credential_store = os.path.join(configdir, email + '.dat')
	
		gd_client = OAuth2Login(client_secrets, credential_store, email)

		#Get Photos in Album
		body = {
			"albumId": albumId,
			"pageSize": 100
		}
		photoList = gd_client.mediaItems().search(body=body).execute()
		photos = photoList.get('mediaItems',[])

		for photo in photos:
			print "FileName: "+photo["filename"]
			print "MimeType: "+photo["mimeType"]
			photoName = os.path.splitext(photo["filename"])[0]
			if photo["mimeType"]=="image/jpeg":
				googleExtList[photoName] = "jpg"
			else:
				googleExtList[photoName] = "heic"
			print "photoName: "+photoName
#			googlePhotoList[photo["filename"]] = photo["baseUrl"]+"=w1024"
			googlePhotoList[photoName] = photo["baseUrl"]+"=w1024"
			try:
#				googleCaptionList[photo["filename"]] = photo['description'] #.encode('utf-8').strip()
				googleCaptionList[photoName] = photo['description'] #.encode('utf-8').strip()
			except KeyError:
				pass
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
	global googleExtList

	print len(currPhotoList)
	print currPhotoList[0]
	print "In RemovePhotosfromAlbum function"
	print "-----------------------------------"
	if len(currPhotoList)>1:
		for pic in currPhotoList:
			print "pic in currPhotoList: "+pic
			if pic not in googlePhotoList and "ig-" not in pic:
				#delete photo from local album
				picName = pic + '.jpg'
				filePath = os.path.join(configdir,"photos",picName)
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
		print "pic in googlePhotoList: "+pic
		if pic not in currPhotoList or pic in googleCaptionList:
			#Download the photo
			fullPic = pic+"."+str(googleExtList.get(pic))
			print "pic: "+pic
			print str(googleExtList.get(pic))
			print "Download: " + str(googlePhotoList.get(pic))
			urllib.urlretrieve(googlePhotoList.get(pic), os.path.join(configdir,"photos",fullPic))
			if googleExtList.get(pic).lower() == "heic":
				#convert to jpg
				print fullPic+ " is HEIC, will be converted"
				convertHEIC(os.path.join(configdir,"photos",pic))
			print "PIC: "+os.path.join(configdir,"photos",pic)
			if pic in googleCaptionList:
				#print "Photo will be captioned with: " + str(googleCaptionList.get(pic))
				addRoundedCaption(os.path.join(configdir,"photos",fullPic),googleCaptionList.get(pic))

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
	#"""
	#Makes an ajax get request.
	#url - endpoint(string)
	#"""
	req = urllib2.Request(url)
	f = urllib2.urlopen(req)
	response = f.read()
	f.close()
	return response	

def convertHEIC(photoName):
	photoPath = os.path.join(configdir,"photos",photoName)

	print('Converting file: ' + photoPath+'.HEIC to: ' + photoPath+'.jpg')
	# magick IMG_0606.heic test.jpg
	call(['convert', photoPath+'.HEIC', photoPath+'.jpg'])
	os.remove(photoPath+'.heic')

def getIgPhotoList():
	global igPhotoList
	igUserCount = int(Config.get('InstagramUsers','Count'))
	for x in range(igUserCount):
		userid = Config.get('InstagramUser'+ str(x+1),'userid')
		igToken = Config.get('InstagramUser'+ str(x+1),'igToken')
		instagramURL = "https://api.instagram.com/v1/users/"+userid+"/media/recent/?access_token=" + igToken
		print instagramURL
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
			print caption
			print createTime
			if not picDict["location"]:
				title = ""
				picDate = ""
			else:
				title = picDict["location"]["name"]
				picDate = datetime.utcfromtimestamp(int(createTime)).strftime('%m/%d/%Y')
			if int(createTime) > int(yesterday_beginning_time):
				svPhotoName = "ig-" + createTime + ".jpg"
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
	font = ImageFont.truetype(fontName, 24)
	titleFont = ImageFont.truetype(fontName, 26)
	dtFont = ImageFont.truetype(fontName, 20)
	#draw.text((x, y),"Sample Text",(r,g,b))

	foreground = Image.open(prof)
	finalImg = Image.new(mode='RGB',size=(1138,640),color=(0,0,0))
	finalImg.paste(img, (480,0))
	finalImg.paste(foreground, (20,0))
	
	lines = textwrap.wrap(txt, 35, break_long_words=False)
	n = 0

	finalImg.save(photo)
	pix = finalImg.load()
	
	draw = ImageDraw.Draw(finalImg)
	print photo
	
	draw.text((20, 160),title,(255,255,255),font=titleFont)
	draw.text((20, 190),dt,(255,255,255),font=dtFont)

	for line in lines:
#		emojiline = emoji.emojize(line)
		draw.text((20, 220+n),line,(255,255,255),font=font)
		n += 25
			
	finalImg.save(photo)

def getFacebookPhotos():
	fbUserCount = int(Config.get('FacebookUsers','Count'))
	for x in range(fbUserCount):
		fbToken = Config.get('FacebookUser'+ str(x+1),'fbToken')
		#Get User's Name
		fbProfileURL = "https://graph.facebook.com/me?access_token="+fbToken
		profileJSON = ajaxRequest(fbProfileURL)
		profileDict = json.loads(profileJSON)
		profileData = profileDict["name"]
		firstName = profileData.split(" ")[0]
		print "Profile Name: " + profileData
		print "First Name: " + firstName


		facebookURL = "https://graph.facebook.com/me/photos?access_token=" + fbToken
	
		print facebookURL
		facebookJSON = ajaxRequest(facebookURL)
		facebookDict = json.loads(facebookJSON)
		facebookData = facebookDict["data"]
		
		profilePic = ""
		filesDownloaded = 0
		for picDict in facebookData:
			# get the image url and current time
			picID = picDict["id"]
			caption = picDict["name"]
			profilePic = "https://graph.facebook.com/me/picture?width=130&access_token=" + fbToken
			svProfilePath = os.path.join(configdir,"photos","FBProfPic.jpg")
			urllib.urlretrieve(profilePic, svProfilePath)

			svPhotoName = "fb-" + picID + ".jpg"
			svPhotoPath = os.path.join(configdir,"photos",svPhotoName)

			imageUrl = "https://graph.facebook.com/"+picID+"?fields=images&access_token=" + fbToken
			imagesJSON = ajaxRequest(imageUrl)
			imagesDict = json.loads(imagesJSON)
			imagesData = imagesDict["images"]
			title = firstName +"'s Facebook Photo"
			picDate = ""
			for image in imagesData:
				imageW = image["width"]
				imageH = image["height"]
				imageDL = ""
				if imageW > imageH:
					print "Landscape"
					imageDL = ""
				else:
					print "Portrait"
					print "ImageH"
					print imageH
					if imageH <= 640:
						print "image is less than 640"
						imageDL = image["source"]
						print "Downloading: "+imageDL
						urllib.urlretrieve(imageDL, svPhotoPath)
						addTextToPhoto(svPhotoPath,caption,svProfilePath,title,picDate)
						filesDownloaded+=1
						break
		if int(filesDownloaded) > 0:
			os.remove(svProfilePath)

#Download photos from Instagram
if Config.get('Plugins','Instagram') == 'True':
	try:
		getIgPhotoList()
	except:
		print "there was a problem with the Instagram Plugin"

#Download photos from Facebook
if Config.get('Plugins','Facebook') == 'True':
	try:
		getFacebookPhotos()
	except:
		print "there was a problem with the Facebook Plugin"

#Download photos from Google Photos Album
if Config.get('Plugins','GooglePhotos') == 'True':
        try:
        	getCurrentPhotoList()
        except:
                print "There was a problem getting the current Photo List"
        try:
        	getGooglePhotoList()
        except:
                print "There was a problem getting the Photo List from Google"

        try:
                RemovePhotosfromAlbum()
        except:
                print "There was a problem deleting photos."
        try:
                DownloadPhotosfromGoogle()
        except:
                print "There was a problem Downloading photos from Google"

#Start the slideshow		
#os.system('sudo fbi -T 1 -noverbose -a -t 60 -u ~/PhotoFrame/photos/*')
