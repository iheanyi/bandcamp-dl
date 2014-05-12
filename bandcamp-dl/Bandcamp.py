import unicodedata
import os
import urllib2

from mutagen.mp3 import MP3
from mutagen.id3 import TIT2
from mutagen.easyid3 import EasyID3
from bs4 import BeautifulSoup
import requests
import sys
import Bandcamp
from os.path import expanduser

import jsobj


class Bandcamp:
    DOWNLOAD_DIR = expanduser("~/Music")


    def get_embed_string_block(self, request):
        embedBlock = request.text.split("var EmbedData = ")

        embedStringBlock = embedBlock[1]
        embedStringBlock = unicodedata.normalize('NFKD', embedStringBlock).encode('ascii', 'ignore')
        embedStringBlock = embedStringBlock.split("};")[0] + "};"
        embedStringBlock = jsobj.read_js_object("var EmbedData = %s" % str(embedStringBlock))

        return embedStringBlock


    def sanatize_text(self, text, space=False, slash=False, period=False):
        result = text

        if not space:
            result = result.replace(" ", "")
        if not slash:
            result = result.replace("/", "")
        if not period:
            result = result.replace(".", "")

        return result


    def download(self, request=None, destination=None, show_progress=False, url=None):
        if not request:
            request = urllib2.Request(url)

        remote_file = urllib2.urlopen(request)
        meta = remote_file.info()
        file_size = int(meta.getheaders("Content-Length")[0])
        file_size_dl = 0
        block_sz = 8192

        local_file = open(destination, 'wb')

        while True:
            buffer = remote_file.read(block_sz)
            if not buffer:
                break

            file_size_dl += len(buffer)
            local_file.write(buffer)

            if show_progress:
                self.display_progress(file_size_dl, file_size)

        local_file.close()
        print "Done downloading: " + destination


    def display_progress(self, current, total):
        factor = float(current) / total
        percent = factor * 100
        status = str( int(round(percent)) )

        sys.stdout.write("Download progress: %s%%   \r" % (status))
        sys.stdout.flush()


    def download_track(self, track, url, title, album_path, artist, album):
        print "Now Downloading: " + track['title'], track['file']['mp3-128'] 

        req = urllib2.Request(url, headers={'User-Agent': "Magic Browser"})
        destination = album_path + '/' + self.sanatize_text(track['title'], space=True) + '.mp3'

        self.download(req, destination, show_progress = True)


    def write_id3_tags(self, track, title, album_path, artist, album):
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


    def create_directories(self, artist, album):
        album_path = self.DOWNLOAD_DIR + "/" + artist + "/" + self.sanatize_text(album)

        if not os.path.exists(self.DOWNLOAD_DIR):
            os.makedirs(self.DOWNLOAD_DIR)

        if not os.path.exists(self.DOWNLOAD_DIR + "/zips"):
            os.makedirs(self.DOWNLOAD_DIR + "/zips")

        if not os.path.exists(album_path):
            os.makedirs(album_path)

        return album_path

        def get_embed_string_block(self, request):
            embedBlock = request.text.split("var EmbedData = ")

            embedStringBlock = embedBlock[1]
            embedStringBlock = unicodedata.normalize('NFKD', embedStringBlock).encode('ascii', 'ignore')
            embedStringBlock = embedStringBlock.split("};")[0] + "};"
            embedStringBlock = jsobj.read_js_object("var EmbedData = %s" % str(embedStringBlock))

            return embedStringBlock


    def extract_album_meta_data(self, request):
        album = {}

        embedData = self.get_embed_string_block(request)

        block = request.text.split("var TralbumData = ")

        stringBlock = block[1]
        stringBlock = unicodedata.normalize('NFKD', stringBlock).encode('ascii', 'ignore')
        stringBlock = stringBlock.split("};")[0] + "};"
        stringBlock = jsobj.read_js_object("var TralbumData = %s" % str(stringBlock))

        album['title'] = embedData['EmbedData']['album_title']
        album['artist'] = stringBlock['TralbumData']['artist']
        album['tracks'] = stringBlock['TralbumData']['trackinfo']

        return album


    @staticmethod
    def generate_album_url(artist, album):
        return "http://{0}.bandcamp.com/album/{1}".format(artist, album)


    def download_album_art(self):
        url = self.soup.find(id='tralbumArt').find_all('img')[0]['src']
        filename = self.album['path'] + "/" + "cover.jpg"
        self.download(destination=filename, url=url)

    def parse_album_page(self, url):
        print "Starting the parsing for: " + url

        r = requests.get(url)
        self.soup = BeautifulSoup(r.text)

        self.album = self.extract_album_meta_data(r)
        self.album['path'] = self.create_directories(self.album['artist'], self.album['title'])
        self.download_album_art()

        for track in self.album['tracks']:
            title = self.sanatize_text(track['title'], space=True)
            url = track['file']['mp3-128']

            self.download_track(track, url, title, self.album['path'], self.album['artist'], self.album['title'])
            self.write_id3_tags(track, title, self.album['path'], self.album['artist'], self.album['title'])
