""" Coded by Iheanyi Ekechukwu

http://www.twitter.com/kwuchu
http://www.github.com/iheanyi

Feel free to use this in any way you wish. I made this just for fun.

Shout out to darkf for writing a helper function for parsing the JavaScript! """

import unicodedata
import os
import urllib

from mutagen.mp3 import MP3
from mutagen.id3 import TIT2
from mutagen.easyid3 import EasyID3
from bs4 import BeautifulSoup
import requests
import sys

import jsobj


def parse_file(url):
    print "Starting the parsing for: " + url
    r = requests.get(url)
    soup = BeautifulSoup(r.text)



    embedBlock = r.text.split("var EmbedData = ")

    embedStringBlock = embedBlock[1]
    embedStringBlock = unicodedata.normalize('NFKD', embedStringBlock).encode('ascii', 'ignore')
    embedStringBlock = embedStringBlock.split("};")[0] + "};"
    embedStringBlock = jsobj.read_js_object("var EmbedData = %s" % str(embedStringBlock))



    embedData = embedStringBlock


    albumTitle = embedData['EmbedData']['album_title']

    block = r.text.split("var TralbumData = ")
    #print block[0]

    stringBlock = block[1]
    stringBlock = unicodedata.normalize('NFKD', stringBlock).encode('ascii', 'ignore')
    stringBlock = stringBlock.split("};")[0] + "};"
    stringBlock = jsobj.read_js_object("var TralbumData = %s" % str(stringBlock))


    data = stringBlock

    artistName = data['TralbumData']['artist']

    firstLetter = artistName[0]

    if not firstLetter.isalpha:
        firstLetter = "0"
    else:
        firstLetter = firstLetter.capitalize()

    if not os.path.exists("files"):
        os.makedirs("files")


    if not os.path.exists("files/" + firstLetter):
        if (firstLetter.isalpha):
            os.makedirs("files/" + firstLetter)

    if not os.path.exists("files/" + firstLetter + "/" + artistName):
        os.makedirs("files/" + firstLetter + "/" + artistName)

    tracks = data['TralbumData']['trackinfo']

    albumPath = albumTitle.replace(" ", "").replace("/", "").replace(".", "")

    albumPath = "files/" + firstLetter + "/" + artistName + "/" + albumPath
    if not os.path.exists("files/zips"):
        os.makedirs("files/zips")

    if not os.path.exists(albumPath):
        os.makedirs(albumPath)

    for each in tracks:
        songTitle = each['title'].replace(" ", "").replace(".", "")
        songURL = each['file']['mp3-128']

        print "Now Downloading: " + each['title'], each['file']['mp3-128']
        urllib.urlretrieve(songURL, albumPath + "/" + songTitle + ".mp3")

        print "Encoding . . . "
        audio = MP3(albumPath + "/" + songTitle + ".mp3")
        audio["TIT2"] = TIT2(encoding=3, text=["title"])
        audio.save()
        audio = EasyID3(albumPath + "/" + songTitle + ".mp3")
        audio["title"] = each['title']
        audio["artist"] = artistName
        audio["album"] = albumTitle
        audio.save()

        print "Done downloading " + songTitle


url = raw_input("Please enter the url of the album or song you wish to download: ")
parse_file(url)
