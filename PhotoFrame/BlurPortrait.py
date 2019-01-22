import subprocess
import socket
import logging
import os
import re

def makeFullframe(filename, displayWidth, displayHeight, zoomOnly=False, autoChoose=False):
		name, ext = os.path.splitext(filename)
		filename_temp = "%s-frame%s" % (name, ext)

		with open(os.devnull, 'wb') as void:
			try:
				output = subprocess.check_output(['/usr/bin/identify', filename], stderr=void)
				print output
			except:
				logging.exception('Error trying to identify image')
				return False

		m = re.search('([1-9][0-9]*)x([1-9][0-9]*)', output)
		print m
		if m is None or m.groups() is None or len(m.groups()) != 2:
			logging.error('Unable to resolve regular expression for image size')
			return False
		width = int(m.group(1))
		height = int(m.group(2))

		width_border = 15
		width_spacing = 3
		border = None
		borderSmall = None

		# Calculate actual size of image based on display
		ar = (float)(width) / (float)(height)
		if width > displayWidth:
			adjWidth = displayWidth
			adjHeight = int(float(displayWidth) / ar)
		else:
			adjWidth = int(float(displayHeight) * ar)
			adjHeight = displayHeight

		logging.debug('Size of image is %dx%d, screen is %dx%d. New size is %dx%d', width, height, displayWidth, displayHeight, adjWidth, adjHeight)

		if adjHeight < displayHeight:
			border = '0x%d' % width_border
			spacing = '0x%d' % width_spacing
			padding = ((displayHeight - adjHeight) / 2 - width_border)
			logging.debug('Landscape image, reframing (padding required %dpx)' % padding)
		elif adjWidth < displayWidth:
			border = '%dx0' % width_border
			spacing = '%dx0' % width_spacing
			padding = ((displayWidth - adjWidth) / 2 - width_border)
			logging.debug('Portrait image, reframing (padding required %dpx)' % padding)
		else:
			logging.debug('Image is fullscreen, no reframing needed')
			return False

		if padding < 20 and not autoChoose:
			logging.debug('That\'s less than 20px so skip reframing (%dx%d => %dx%d)', width, height, adjWidth, adjHeight)
			return False

		if padding < 60 and autoChoose:
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
					'%sx%s^' % (displayWidth, displayHeight),
					'-gravity',
					'center',
					'-crop',
					'%sx%s+0+0' % (displayWidth, displayHeight),
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
					'%sx%s' % (displayWidth, displayHeight),
					'-background',
					'transparent',
					'-gravity',
					'center',
					'-extent',
					'%sx%s' % (displayWidth, displayHeight),
					')',
					'-composite',
					filename_temp
				]
		except:
			logging.exception('Error building command line')
			logging.debug('Filename: ' + repr(filename))
			logging.debug('Filename_temp: ' + repr(filename_temp))
			logging.debug('border: ' + repr(border))
			logging.debug('spacing: ' + repr(spacing))
			return False

		try:
			subprocess.check_output(cmd, stderr=subprocess.STDOUT)
		except subprocess.CalledProcessError as e:
			logging.exception('Unable to reframe the image')
			logging.error('Output: %s' % repr(e.output))
			return False
		os.rename(filename_temp, filename)
		return True

makeFullframe('/home/pi/PhotoFrame/photos/IMG_0855.JPG',1280,800)
