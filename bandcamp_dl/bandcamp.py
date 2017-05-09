from datetime import datetime as dt
import json

import requests
from bs4 import BeautifulSoup
from bs4 import FeatureNotFound

from bandcamp_dl.bandcampjson import BandcampJSON


class Bandcamp:
    def __init__(self):
        self.headers = {'User-Agent': 'bandcamp-dl/0.0.8-02 (https://github.com/iheanyi/bandcamp-dl)'}

    def parse(self, url: str, art: bool=True) -> dict or None:
        """Requests the page, cherry picks album info

        :param url: album/track url
        :param art: if True download album art
        :return: album metadata
        """
        try:
            response = requests.get(url, headers=self.headers)
        except requests.exceptions.MissingSchema:
            return None

        try:
            self.soup = BeautifulSoup(response.text, "lxml")
        except FeatureNotFound:
            self.soup = BeautifulSoup(response.text, "html.parser")

        bandcamp_json = BandcampJSON(self.soup).generate()
        album_json = json.loads(bandcamp_json[0])
        embed_json = json.loads(bandcamp_json[1])
        page_json = json.loads(bandcamp_json[2])

        self.tracks = album_json['trackinfo']

        album_release = album_json['album_release_date']
        if album_release is None:
            album_release = album_json['current']['release_date']

        try:
            album_title = embed_json['album_title']
        except KeyError:
            album_title = album_json['trackinfo'][0]['title']

        try:
            label = page_json['item_sellers']['{}'.format(album_json['current']['selling_band_id'])]['name']
        except KeyError:
            label = None

        album = {
            "tracks": [],
            "title": album_title,
            "artist": embed_json['artist'],
            "label": label,
            "full": False,
            "art": "",
            "date": str(dt.strptime(album_release, "%d %b %Y %H:%M:%S GMT").year)
        }

        for track in self.tracks:
            if track['file'] is not None:
                track = self.get_track_metadata(track)
                album['tracks'].append(track)

        album['full'] = self.all_tracks_available()
        if art:
            album['art'] = self.get_album_art()

        return album

    def all_tracks_available(self) -> bool:
        """Verify that all tracks have a url

        :return: True if all urls accounted for
        """
        for track in self.tracks:
            if track['file'] is None:
                return False
        return True

    @staticmethod
    def get_track_metadata(track: dict or None) -> dict:
        """Extract individual track metadata

        :param track: track dict
        :return: track metadata dict
        """
        track_metadata = {
            "duration": track['duration'],
            "track": str(track['track_num']),
            "title": track['title'],
            "url": None
        }

        if 'mp3-128' in track['file']:
            track_metadata['url'] = "http:" + track['file']['mp3-128']
        else:
            track_metadata['url'] = None

        if track['has_lyrics'] is not False:
            if track['lyrics'] is None:
                track['lyrics'] = "lyrics unavailable"
            track_metadata['lyrics'] = track['lyrics'].replace('\\r\\n', '\n')

        return track_metadata

    @staticmethod
    def generate_album_url(artist: str, slug: str, page_type: str) -> str:
        """Generate an album url based on the artist and album name

        :param artist: artist name
        :param slug: Slug of album/track
        :param page_type: Type of page album/track
        :return: url as str
        """
        return "http://{0}.bandcamp.com/{1}/{2}".format(artist, page_type, slug)

    def get_album_art(self) -> str:
        """Find and retrieve album art url from page

        :return: url as str
        """
        try:
            url = self.soup.find(id='tralbumArt').find_all('img')[0]['src']
            return url
        except None:
            pass
