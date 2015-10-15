from bs4 import BeautifulSoup
import requests

import jsobj


class Bandcamp:

    def parse(self, url):
        try:
            r = requests.get(url)
        except requests.exceptions.MissingSchema:
            return None

        if r.status_code is not 200:
            return None

        self.soup = BeautifulSoup(r.text, "lxml")
        album = {
            "tracks": [],
            "title": "",
            "artist": "",
            "full": False,
            "art": "",
            "date": ""
        }

        album_meta = self.extract_album_meta_data(r)

        album['artist'] = album_meta['artist']
        album['title'] = album_meta['title']
        album['date'] = album_meta['date']

        for track in album_meta['tracks']:
            track = self.get_track_meta_data(track)
            album['tracks'].append(track)

        album['full'] = self.all_tracks_available(album)
        album['art'] = self.get_album_art()

        return album

    def all_tracks_available(self, album):
        for track in album['tracks']:
            if track['url'] is None:
                return False

        return True

    def get_track_meta_data(self, track):
        new_track = {}
        if not (isinstance(track['file'], unicode) or isinstance(track['file'], str)):
            if 'mp3-128' in track['file']:
                new_track['url'] = track['file']['mp3-128']
        else:
            new_track['url'] = None

        new_track['duration'] = track['duration']
        new_track['track'] = track['track_num']
        new_track['title'] = track['title']

        return new_track

    def extract_album_meta_data(self, request):
        album = {}

        embedData = self.get_embed_string_block(request)

        block = request.text.split("var TralbumData = ")

        stringBlock = block[1]

        stringBlock = stringBlock.split("};")[0] + "};"
        stringBlock = jsobj.read_js_object("var TralbumData = %s" % stringBlock)

        album['title'] = embedData['EmbedData']['album_title']
        album['artist'] = stringBlock['TralbumData']['artist']
        album['tracks'] = stringBlock['TralbumData']['trackinfo']
        album['date'] = stringBlock['TralbumData']['album_release_date'].split()[2]

        return album

    @staticmethod
    def generate_album_url(artist, album):
        return "http://{0}.bandcamp.com/album/{1}".format(artist, album)

    def get_album_art(self):
        try:
            url = self.soup.find(id='tralbumArt').find_all('img')[0]['src']
            return url
        except:
            pass


    def get_embed_string_block(self, request):
        embedBlock = request.text.split("var EmbedData = ")

        embedStringBlock = embedBlock[1]
        embedStringBlock = embedStringBlock.split("};")[0] + "};"
        embedStringBlock = jsobj.read_js_object("var EmbedData = %s" % embedStringBlock)

        return embedStringBlock
