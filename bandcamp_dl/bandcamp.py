import sys
import datetime
import json
import logging

import bs4
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import create_urllib3_context
from urllib.parse import urlparse, urlunparse

from bandcamp_dl import __version__
from bandcamp_dl.bandcampjson import BandcampJSON

class SSLAdapter(HTTPAdapter):
    def __init__(self, ssl_context=None, **kwargs):
        self.ssl_context = ssl_context
        super().__init__(**kwargs)

    def init_poolmanager(self, *args, **kwargs):
        kwargs['ssl_context'] = self.ssl_context
        return super().init_poolmanager(*args, **kwargs)

    def proxy_manager_for(self, *args, **kwargs):
        kwargs['ssl_context'] = self.ssl_context
        return super().proxy_manager_for(*args, **kwargs)
    
# Create the SSL context with the custom ciphers
ctx = create_urllib3_context()
ctx.load_default_certs()

DEFAULT_CIPHERS = ":".join(
    [
        "ECDHE+AESGCM",
        "ECDHE+CHACHA20",
        "DHE+AESGCM",
        "DHE+CHACHA20",
        "ECDH+AESGCM",
        "DH+AESGCM",
        "ECDH+AES",
        "DH+AES",
        "RSA+AESGCM",
        "RSA+AES",
        "!aNULL",
        "!eNULL",
        "!MD5",
        "!DSS",
        "!AESCCM",
    ]
)
ctx.set_ciphers(DEFAULT_CIPHERS)

class Bandcamp:
    def __init__(self):
        self.headers = {'User-Agent': f'bandcamp-dl/{__version__} '
                        f'(https://github.com/iheanyi/bandcamp-dl)'}
        self.soup = None
        self.tracks = None
        self.logger = logging.getLogger("bandcamp-dl").getChild("Main")
        
        # Mount the adapter with the custom SSL context to the session
        self.session = requests.Session()
        self.adapter = SSLAdapter(ssl_context=ctx)
        self.session.mount('https://', self.adapter)

    def parse(self, url: str, art: bool = True, lyrics: bool = False, genres: bool = False,
              debugging: bool = False) -> dict or None:
        """Requests the page, cherry-picks album info

        :param url: album/track url
        :param art: if True download album art
        :param lyrics: if True fetch track lyrics
        :param genres: if True fetch track tags
        :param debugging: if True then verbose output
        :return: album metadata
        """

        try:
            response = self.session.get(url, headers=self.headers)
        except requests.exceptions.MissingSchema:
            return None

        if not response.ok:
            self.logger.debug(" Status code: %s", response.status_code)
            print(f"The Album/Track requested does not exist at: {url}")
            sys.exit(2)


        try:
            self.soup = bs4.BeautifulSoup(response.text, "lxml")
        except bs4.FeatureNotFound:
            self.soup = bs4.BeautifulSoup(response.text, "html.parser")

        self.logger.debug(" Generating BandcampJSON..")
        bandcamp_json = BandcampJSON(self.soup, debugging).generate()
        page_json = {}
        for entry in bandcamp_json:
            page_json = {**page_json, **json.loads(entry)}
        self.logger.debug(" BandcampJSON generated..")

        self.logger.debug(" Generating Album..")
        self.tracks = page_json['trackinfo']

        album_release = page_json['album_release_date']
        if album_release is None:
            album_release = page_json['current']['release_date']
            if album_release is None:
                album_release = page_json['embed_info']['item_public']

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
            "date": str(datetime.datetime.strptime(album_release, "%d %b %Y %H:%M:%S GMT").year),
            "url": url,
            "genres": ""
        }

        if "/track/" in page_json['url']:
            artist_url = page_json['url'].rpartition('/track/')[0]
        else:
            artist_url = page_json['url'].rpartition('/album/')[0]

        for track in self.tracks:
            if lyrics:
                track['lyrics'] = self.get_track_lyrics(f"{artist_url}"
                                                        f"{track['title_link']}#lyrics")

            if track['file'] is not None:
                track = self.get_track_metadata(track)
                album['tracks'].append(track)

        album['full'] = self.all_tracks_available()
        if art:
            album['art'] = self.get_album_art()
        if genres:
            album['genres'] = "; ".join(page_json['keywords'])

        self.logger.debug(" Album generated..")
        self.logger.debug(" Album URL: %s", album['url'])

        return album

    def get_track_lyrics(self, track_url):
        self.logger.debug(" Fetching track lyrics..")
        track_page = self.session.get(track_url, headers=self.headers)
        try:
            track_soup = bs4.BeautifulSoup(track_page.text, "lxml")
        except bs4.FeatureNotFound:
            track_soup = bs4.BeautifulSoup(track_page.text, "html.parser")
        track_lyrics = track_soup.find("div", {"class": "lyricsText"})
        if track_lyrics:
            self.logger.debug(" Lyrics retrieved..")
            return track_lyrics.text
        else:
            self.logger.debug(" Lyrics not found..")
            return ""

    def all_tracks_available(self) -> bool:
        """Verify that all tracks have a url

        :return: True if all urls accounted for
        """
        for track in self.tracks:
            if track['file'] is None:
                return False
        return True

    def get_track_metadata(self, track: dict or None) -> dict:
        """Extract individual track metadata

        :param track: track dict
        :return: track metadata dict
        """
        self.logger.debug(" Generating track metadata..")
        track_metadata = {
            "duration": track['duration'],
            "track": str(track['track_num']),
            "title": track['title'],
            "artist": track['artist'],
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
            if track['lyrics'] is not None:
                track_metadata['lyrics'] = track['lyrics'].replace('\\r\\n', '\n')

        self.logger.debug(" Track metadata generated..")
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

    def get_full_discography(self, artist: str, page_type: str) -> list:
        """Generate a list of album and track urls based on the artist name

        :param artist: artist name
        :param page_type: Type of page, it should be music but it's a parameter so it's not
                          hardcoded
        :return: urls as list of strs
        """
        html = self.session.get(f"https://{artist}.bandcamp.com/{page_type}").text

        try:
            soup = bs4.BeautifulSoup(html, "lxml")
        except bs4.FeatureNotFound:
            soup = bs4.BeautifulSoup(html, "html.parser")

        urls = []

        for music_grid_item in soup.find_all("li", class_="music-grid-item"):
            for a in music_grid_item.find_all("a", href=True):
                url = a['href']
                if not url.startswith('http'):
                    url = f"https://{artist}.bandcamp.com{a['href']}"
                
                parsed_url = urlparse(url)
                url = urlunparse(parsed_url._replace(query='', fragment=''))
                urls.append(url)

        data_client_items_attributes = soup.find_all(attrs={"data-client-items": True})

        data_client_items = []

        for data_client_items_attribute in data_client_items_attributes:
            data_client_items += json.loads(
                    data_client_items_attribute['data-client-items'])

        for album in data_client_items:
            if 'page_url' in album:
                page_url = album['page_url']
                url = ""

                if page_url.startswith('http'):
                    url = page_url
                else:
                    url = f"https://{artist}.bandcamp.com{page_url}"
                
                parsed_url = urlparse(url)
                url = urlunparse(parsed_url._replace(query='', fragment=''))
                urls.append(url)

        self.logger.debug(f" {len(urls)} Album URLs found for {artist}.\nURLs: \n" + "\n"
            .join(url for url in urls) + "\n")

        return urls
