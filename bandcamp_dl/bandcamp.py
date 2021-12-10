from datetime import datetime as dt
import json
import logging

import requests
from bs4 import BeautifulSoup
from bs4 import FeatureNotFound

from bandcamp_dl.bandcampjson import BandcampJSON
from bandcamp_dl.__init__ import __version__


class Bandcamp:
    def __init__(self):
        self.headers = {'User-Agent': f'bandcamp-dl/{__version__} (https://github.com/iheanyi/bandcamp-dl)'}
        self.soup = None
        self.tracks = None

    def parse(self, url: str, art: bool = True, lyrics: bool = False, debugging: bool = False) -> dict or None:
        """Requests the page, cherry-picks album info

        :param url: album/track url
        :param art: if True download album art
        :param lyrics: if True fetch track lyrics
        :param debugging: if True then verbose output
        :return: album metadata
        """
        if debugging:
            logging.basicConfig(level=logging.DEBUG)

        try:
            response = requests.get(url, headers=self.headers)
        except requests.exceptions.MissingSchema:
            return None

        try:
            self.soup = BeautifulSoup(response.text, "lxml")
        except FeatureNotFound:
            self.soup = BeautifulSoup(response.text, "html.parser")

        logging.debug(" Generating BandcampJSON..")
        bandcamp_json = BandcampJSON(self.soup, debugging).generate()
        page_json = {}
        for entry in bandcamp_json:
            page_json = {**page_json, **json.loads(entry)}
        logging.debug(" BandcampJSON generated..")

        logging.debug(" Generating Album..")
        self.tracks = page_json['trackinfo']

        album_release = page_json['album_release_date']
        if album_release is None:
            album_release = page_json['current']['release_date']
            if album_release is None:
                album_release = page_json['current']['publish_date']
        try:
            album_title = page_json['current']['title']
        except KeyError:
            album_title = page_json['trackinfo'][0]['title']

        try:
            label = page_json['item_sellers'][f'{page_json["current"]["selling_band_id"]}']['name']
        except KeyError:
            label = None

        album = {
            "tracks": [],
            "title": album_title,
            "artist": page_json['artist'],
            "label": label,
            "full": False,
            "art": "",
            "date": str(dt.strptime(album_release, "%d %b %Y %H:%M:%S GMT").year),
            "url": url
        }

        if "track" in page_json['url']:
            artist_url = page_json['url'].rpartition('/track/')[0]
        else:
            artist_url = page_json['url'].rpartition('/album/')[0]

        for track in self.tracks:
            if lyrics:
                track['lyrics'] = self.get_track_lyrics(f"{artist_url}{track['title_link']}#lyrics")
            if track['file'] is not None:
                track = self.get_track_metadata(track)
                album['tracks'].append(track)

        album['full'] = self.all_tracks_available()
        if art:
            album['art'] = self.get_album_art()

        logging.debug(" Album generated..")
        logging.debug(f" Album URL: {album['url']}")

        return album

    def get_track_lyrics(self, track_url):
        logging.debug(" Fetching track lyrics..")
        track_page = requests.get(track_url, headers=self.headers)
        try:
            track_soup = BeautifulSoup(track_page.text, "lxml")
        except FeatureNotFound:
            track_soup = BeautifulSoup(track_page.text, "html.parser")
        track_lyrics = track_soup.find("div", {"class": "lyricsText"})
        if track_lyrics:
            logging.debug(" Lyrics retrieved..")
            return track_lyrics.text
        else:
            logging.debug(" Lyrics not found..")
            return "lyrics unavailable"

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
        logging.debug(" Generating track metadata..")
        track_metadata = {
            "duration": track['duration'],
            "track": str(track['track_num']),
            "title": track['title'],
            "url": None
        }

        if 'mp3-128' in track['file']:
            if 'https' in track['file']['mp3-128']:
                track_metadata['url'] = track['file']['mp3-128']
            else:
                track_metadata['url'] = "http:" + track['file']['mp3-128']
        else:
            track_metadata['url'] = None

        if track['has_lyrics'] is not False:
            if track['lyrics'] is None:
                track['lyrics'] = "lyrics unavailable"
            track_metadata['lyrics'] = track['lyrics'].replace('\\r\\n', '\n')

        logging.debug(" Track metadata generated..")
        return track_metadata

    @staticmethod
    def generate_album_url(artist: str, slug: str, page_type: str) -> str:
        """Generate an album url based on the artist and album name

        :param artist: artist name
        :param slug: Slug of album/track
        :param page_type: Type of page album/track
        :return: url as str
        """
        return f"http://{artist}.bandcamp.com/{page_type}/{slug}"

    def get_album_art(self) -> str:
        """Find and retrieve album art url from page

        :return: url as str
        """
        try:
            url = self.soup.find(id='tralbumArt').find_all('a')[0]['href']
            return url
        except None:
            pass
