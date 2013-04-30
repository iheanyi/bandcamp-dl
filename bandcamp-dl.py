import eyed3
import json
from hsaudiotag import auto
from hsaudiotag import mpeg
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2
from mutagen.easyid3 import EasyID3
import simplejson as json
from shutil import make_archive

import demjson
import pprint

import requests
import os
import sys
import zipfile
import re
import urllib
import ast

from bs4 import BeautifulSoup


class Result:
	def __init__(self, url, name, title, which):
		self.url = url
		self.title = title
		self.type = which
		self.artist = name

	def __str__(self):

		return 



searchURL = "http://www.bandcamp.com/search?q="
#def getEyeD3Tags(path):
results = []
"""
	trackInfo = eyed3.load(path)
	tag = trackInfo.getTag()
	tag.link(path)

	print "Artist: %s" % tag.getArtist()
	print "Album: %s" % tag.getAlbum()
	print "Track: %s" % tag.getTitle()
	print "Track Length: %s" % trackInfo.getPlayTimeString()
	print "Release Year: %s" % tag.getYear()"""

def search_artist(query):
	r = requests.get(searchURL + query)
	#print r.text
	parse_results(r.text)


def zipdir(path, zip):
	for root, dirs, files in os.walk(path):
		for file in files:
			zip.write(os.path.join(root, file))


def parse_file(url):
	r = requests.get(url)
	soup = BeautifulSoup(r.text)

	if "album" in url:
		songType = "album"
	else:
		songType = "track"

	albumTitle = soup.head.title.text

	#print title

	#regex = re.compile(r'var TralbumData ([^*?])};')
	#m = regex.search(r.text)
	

	embedBlock = r.text.split("var EmbedData = ")

	embedStringBlock = embedBlock[1]
	embedStringBlock = embedStringBlock.split("};")[0] + "}"
	embedStringBlock = embedStringBlock.strip().replace("   ", "")

	tralbum_param = "tralbum_param"
	name = "name"
	value = "value"
	swf_base_url = "swf_base_url"
	album_title = "album_title"
	art_url = "art_url"
	lg_art_url = "lg_art_url"
	numtracks = "numtracks"
	title = "title"
	artist = "artist"
	linkback = "linkback"

	embedData = eval(embedStringBlock)

	artistName = embedData['artist']

	if "name" in embedData.keys():
		fileType = "track"
		trackName = embedData['name']
	else:
		fileType = "album"

	albumTitle = embedData['album_title']


	print embedData

	block = r.text.split("var TralbumData = ")
	#print block[0]

	stringBlock = block[1]

	stringBlock = stringBlock.split("};")[0] + "}"
	#print stringBlock

	stringArray = stringBlock.split("\n")
	del stringArray[1:4]
	#print stringArray

	stringBlock = "".join(stringArray).strip().replace("    ", "")


	null = None
	current = "current"
	is_preorder = "is_preorder"
	album_is_preorder = "album_is_preorder"
	album_release_date = "album_release_date"
	album_url = "album_url"
	preorder_count = "preorder_count"
	hasAudio = "hasAudio"
	artThumbURL = "artThumbURL"
	artFullsizeUrl = "artFullsizeUrl"
	trackinfo = "trackinfo"
	playing_from = "playing_from"
	featured_track_id = "featured_track_id"
	initial_track_num = "initial_track_num"
	defaultPrice = "defaultPrice"
	freeDownloadPage = "freeDownloadPage"
	packages = "packages"
	maxPrice = "maxPrice"
	minPrice = "minPrice"
	FREE = "FREE"
	PAID = "PAID"
	artist = "artist"
	item_type = "item_type"
	id = "id"
	true = True
	false = False
	#print unicode(stringBlock.strip())
	data = eval(stringBlock.strip())

	artistName = data['artist']


	firstLetter = artistName[0]

	if not firstLetter.isalpha:
		firstLetter = "0"
	else:
		firstLetter = firstLetter.capitalize()


	if not os.path.exists("files"):
		os.makedirs("files")


	letterDirectory = "files/" + firstLetter

	if not os.path.exists("files/" + firstLetter):
		if(firstLetter.isalpha):
			os.makedirs("files/" + firstLetter)


	if not os.path.exists("files/" + firstLetter + "/" + artistName):
		os.makedirs("files/" + firstLetter + "/" + artistName)


	#pprint.pprint(data)
	#print data['current']

	#print data['hasAudio']
	#print data['artFullsizeUrl']

	tracks = data['trackinfo']
	#print tracks
	

	albumPath = albumTitle.replace(" ", "").replace("/","").replace(".", "")




	albumPath = "files/" + firstLetter + "/" + artistName + "/" + albumPath
	if not os.path.exists("files/zips"):
			os.makedirs("files/zips")

	if not os.path.exists(albumPath):
		os.makedirs(albumPath)

	#albumPath = "files/" + firstLetter + "/" + artistName + "/" + albumPath
	for each in tracks:
		songTitle = each['title'].replace(" ", "").replace(".", "")
		songURL = each['file']['mp3-128']
		track_num = each['track_num']

		print "Now Downloading: " +  each['title'], each['file']['mp3-128']
		urllib.urlretrieve(songURL, albumPath + "/" + songTitle + ".mp3")



		print "Encoding . . . "
		audio = MP3(albumPath + "/" + songTitle + ".mp3")
		audio["TIT2"]=TIT2(encoding=3, text=["title"])
		audio.save()
		audio = EasyID3(albumPath + "/" + songTitle + ".mp3")
		audio["title"] = each['title']
		audio["artist"] = artistName
		audio["album"] = albumTitle
		#audio["tracknumber"] = track_num
		audio.save()

		#audiofile.tag.save()
		print "Done downloading " + songTitle

		


	if(len(tracks) > 1):
		if not os.path.isfile("files/zips/" + albumTitle.replace(" ", "") + ".zip"):
			make_archive("files/zips/" + albumTitle.replace(" ", ""), 'zip', albumPath)
		else:
			print "Already have a zipfile of this junts, serve that up!"
		#zip = zipfile.ZipFile("files/zips/" + albumTitle.replace(" ", "") + ".zip", 'w')
		#zipdir(albumPath + "/", zip)
		#zip.close


	#print a
	#print stringBlock
	#print demjson.decode(stringBlock)

	#print data
	#data = json.loads(stringBlock.strip())

	#print data['current']

	#print r.text
		#print "Match found."
		#print m.group(1)
	#albumDataBlock = 


def parse_results(text):
	soup = BeautifulSoup(text)

	items = soup.findAll("li", "searchresult")

	for item in items:
		#print item.text

		typeText = item.find(class_="itemtype").text.strip()
		albumTitle = item.find(class_="heading").text.strip()

		artistName = item.find(class_="subhead").text.strip()

		artistName = artistName.replace("by ", "")

		itemURL = item.find(class_="itemurl").text.strip()

		if "track" in itemURL:
			itemType = "track"
		else:
			itemType = "album"


		result = Result(itemURL, artistName, albumTitle, itemType)
		results.append(result)
		#print itemType, albumTitle, artistName, itemURL

def printTags():
	for r in results:
		print r.artist, r.title, r.type, r.url, r.type


def getTags(path):

	myfile = mpeg.Mpeg('inthecity.mp3')
	print myfile.artist
	print myfile.album
	print myfile.original




print EasyID3.valid_keys.keys()

url = sys.argv[1]
if(len(sys.argv) != 2):
	print "usage: bandcamp-dl.py <url to download>"
##audio["title"] = unicode("1. yewknxwusup [TWRK]")
#audio.save()
parse_file(url)
#search_artist("talib kweli")
#printTags()
#getMutagenTags("inthecity.mp3")
#getEyeD3Tags("inthecity.mp3")
#getTags("inthecity.mp3")