import wgetter

import unicodedata
import os
import urllib2

from mutagen.mp3 import MP3
from mutagen.id3 import TIT2
from mutagen.easyid3 import EasyID3
from bs4 import BeautifulSoup
import requests
import sys
import os
import jsobj

class BandcampDownloader():

    def __init__(self, urls=None, template=None, directory=None):
        if type(urls) is str:
            self.urls = [urls]

        if directory:
            directory = os.path.expanduser(directory)

            if os.path.isdir(directory):
                self.directory = directory

        self.urls = urls
        self.template = template


    def start(self, album):
        self.download_album(album)


    def template_to_path(self, track):
        path = self.template
        path = path.replace("%{artist}", track['artist'])
        path = path.replace("%{album}", track['album'])
        path = path.replace("%{track}", track['track'])
        path = path.replace("%{title}", track['title'])
        path = u"{0}/{1}.{2}".format(self.directory, path, "mp3")

        return path


    def create_directory(self, filename):
        directory = os.path.dirname(filename)
        if not os.path.exists(directory):
            os.makedirs(directory)

        return directory


    def download_album(self, album):

        for track in album['tracks']:
            track_meta = {
                "artist": album['artist'],
                "album": album['title'],
                "title": track['title'],
                "track": track['track'],
                "date": album['date']
            }

            filename = self.template_to_path(track_meta)
            dirname = self.create_directory(filename)
            
            try:
                tmp_file = wgetter.download(track['url'], outdir=dirname)
                os.rename(tmp_file, filename)
                self.write_id3_tags(filename, track_meta)
            except Exception as e:
                print e
                print "Downloading failed.."
                return False

        return True


    def write_id3_tags(self, filename, meta):
        print "Encoding . . . "

        audio = MP3(filename)
        audio["TIT2"] = TIT2(encoding=3, text=["title"])
        audio.save()

        audio = EasyID3(filename)
        audio["title"] = meta['title']
        audio["artist"] = meta['artist']
        audio["album"] = meta['album']
        audio["date"] = meta['date']
        audio.save()

        print "Done encoding . . . "
