from bandcampjson import BandcampJSON
from bs4 import BeautifulSoup
from bs4 import FeatureNotFound
import requests
import json


class Bandcamp:
    def parse(self, url: str, art: bool=True) -> dict or None:
        """
        Requests the page, cherry picks album info

        :param url: album/track url
        :param art: if True download album art
        :return: album metadata
        """
        try:
            r = requests.get(url)
        except requests.exceptions.MissingSchema:
            return None

        try:
            self.soup = BeautifulSoup(r.text, "lxml")
        except FeatureNotFound:
            self.soup = BeautifulSoup(r.text, "html.parser")

        self.generate_album_json()
        self.tracks = self.tralbum_data_json['trackinfo']

        album = {
            "tracks": [],
            "title": self.embed_data_json['album_title'],
            "artist": self.embed_data_json['artist'],
            "full": False,
            "art": "",
            "date": self.tralbum_data_json['album_release_date']
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
        """
        Verify that all tracks have a url

        :return: True if all urls accounted for
        """
        for track in self.tracks:
            if track['file'] is None:
                return False
        return True

    @staticmethod
    def get_track_metadata(track: dict or None) -> dict:
        """
        Extract individual track metadata

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
        return track_metadata

    def generate_album_json(self):
        """
        Retrieve JavaScript dictionaries from page and generate JSON

        :return: True if successful
        """
        try:
            embed = BandcampJSON(self.soup, "EmbedData")
            tralbum = BandcampJSON(self.soup, "TralbumData")

            embed_data = embed.js_to_json()
            tralbum_data = tralbum.js_to_json()

            self.embed_data_json = json.loads(embed_data)
            self.tralbum_data_json = json.loads(tralbum_data)
        except Exception as e:
            print(e)
            return None
        return True

    @staticmethod
    def generate_album_url(artist: str, album: str) -> str:
        """
        Generate an album url based on the artist and album name

        :param artist: artist name
        :param album: album name
        :return: album url as str
        """
        return "http://{0}.bandcamp.com/album/{1}".format(artist, album)

    def get_album_art(self) -> str:
        """
        Find and retrieve album art url from page

        :return: url as str
        """
        try:
            url = self.soup.find(id='tralbumArt').find_all('img')[0]['src']
            return url
        except None:
            pass
