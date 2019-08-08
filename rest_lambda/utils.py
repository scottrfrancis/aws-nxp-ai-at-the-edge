#
# Copyright 2019 Toradex AG. or its affiliates. All Rights Reserved.
#

import urllib.request as urllib2

class Utils:
	def __init__(self):
		self.__internet_connection = False

	def isInternetConnected(self):
		# try ping google
		try:
			urllib2.urlopen('http://216.58.192.142', timeout=1)
			return True
		except urllib2.URLError as err: 
			return False
