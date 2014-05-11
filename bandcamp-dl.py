""" Coded by Iheanyi Ekechukwu

http://www.twitter.com/kwuchu
http://www.github.com/iheanyi

Feel free to use this in any way you wish. I made this just for fun.

Shout out to darkf for writing a helper function for parsing the JavaScript! """

import unicodedata
import os
import urllib2

from mutagen.mp3 import MP3
from mutagen.id3 import TIT2
from mutagen.easyid3 import EasyID3
from bs4 import BeautifulSoup
import requests
import sys

import jsobj

#####################################

DOWNLOAD_DIR = "/Users/simonwjackson/music"

#####################################


def get_embed_string_block(request):
    embedBlock = request.text.split("var EmbedData = ")

    embedStringBlock = embedBlock[1]
    embedStringBlock = unicodedata.normalize('NFKD', embedStringBlock).encode('ascii', 'ignore')
    embedStringBlock = embedStringBlock.split("};")[0] + "};"
    embedStringBlock = jsobj.read_js_object("var EmbedData = %s" % str(embedStringBlock))

    return embedStringBlock


def sanatize_text(text, space=False, slash=False, period=False):
    result = text

    if not space:
        result = result.replace(" ", "")
    if not slash:
        result = result.replace("/", "")
    if not period:
        result = result.replace(".", "")

    return result

def download_track(track, url, title, album_path, artist, album):
    print "Now Downloading: " + track['title'], track['file']['mp3-128'] 

    req = urllib2.Request(url, headers={'User-Agent': "Magic Browser"})
    u = urllib2.urlopen(req)
    f = open(album_path + '/' + track['title'] + '.mp3', 'wb')
    meta = u.info()
    file_size = int(meta.getheaders("Content-Length")[0])
    file_size_dl = 0
    block_sz = 8192

    while True:
        buffer = u.read(block_sz)
        if not buffer:
            break

        file_size_dl += len(buffer)
        f.write(buffer)
        p = float(file_size_dl) / file_size
        status = r"[{1:.2%}]".format(file_size_dl, p)
        status = status + chr(8) * (len(status) + 1)
        sys.stdout.write("Download progress: %s%%   \r" % (status))
        sys.stdout.flush()

    f.close()
    print "Done downloading " + title

    write_id3_tags(track, title, album_path, artist, album)


def write_id3_tags(track, title, album_path, artist, album):
    print "Encoding . . . "

    audio = MP3(album_path + '/' + track['title'] + '.mp3')
    audio["TIT2"] = TIT2(encoding=3, text=["title"])
    audio.save()

    audio = EasyID3(album_path + '/' + track['title'] + '.mp3')
    audio["title"] = track['title']
    audio["artist"] = artist
    audio["album"] = album
    audio.save()

    print "Done encoding . . . "


def create_directories(artist, album):
    album_path = DOWNLOAD_DIR + "/" + artist + "/" + sanatize_text(album)

    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)

    if not os.path.exists(DOWNLOAD_DIR + "/zips"):
        os.makedirs(DOWNLOAD_DIR + "/zips")

    if not os.path.exists(album_path):
        os.makedirs(album_path)

    return album_path


def extract_album_meta_data(request):
    album = {}

    embedData = get_embed_string_block(request)

    block = request.text.split("var TralbumData = ")

    stringBlock = block[1]
    stringBlock = unicodedata.normalize('NFKD', stringBlock).encode('ascii', 'ignore')
    stringBlock = stringBlock.split("};")[0] + "};"
    stringBlock = jsobj.read_js_object("var TralbumData = %s" % str(stringBlock))

    album['title'] = embedData['EmbedData']['album_title']
    album['artist'] = stringBlock['TralbumData']['artist']
    album['tracks'] = stringBlock['TralbumData']['trackinfo']

    return album


def parse_file(url):
    print "Starting the parsing for: " + url

    r = requests.get(url)
    soup = BeautifulSoup(r.text)

    album = extract_album_meta_data(r)
    album['path'] = create_directories(album['artist'], album['title'])

    for track in album['tracks']:
        title = sanatize_text(track['title'], space=True)
        url = track['file']['mp3-128']

        download_track(track, url, title, album['path'], album['artist'], album['title'])


url = raw_input("Please enter the url of the album or song you wish to download: ")
parse_file(url)
