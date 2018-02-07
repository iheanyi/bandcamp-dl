import os
import sys
import logging

import requests
from mutagen.mp3 import MP3, EasyMP3
from mutagen.id3._frames import TIT1
from mutagen.id3._frames import TIT2
from mutagen.id3._frames import USLT
from mutagen.id3._frames import APIC
from slugify import slugify

if not sys.version_info[:2] == (3, 6):
    import mock
    from bandcamp_dl.utils import requests_patch

from bandcamp_dl.__init__ import __version__

from bandcamp_dl.utils.clean_print import print_clean


class BandcampDownloader:
    def __init__(self, template, directory, overwrite, embed_lyrics, grouping, embed_art, no_slugify, debugging, urls=None):
        """Initialize variables we will need throughout the Class

        :param urls: list of urls
        :param template: filename template
        :param directory: download location
        :param overwrite: if True overwrite existing files
        """
        self.headers = {'User-Agent': 'bandcamp-dl/{} (https://github.com/iheanyi/bandcamp-dl)'.format(__version__)}
        self.session = requests.Session()

        if type(urls) is str:
            self.urls = [urls]

        self.urls = urls
        self.template = template
        self.directory = directory
        self.overwrite = overwrite
        self.grouping = grouping
        self.embed_art = embed_art
        self.embed_lyrics = embed_lyrics
        self.no_slugify = no_slugify
        self.debugging = debugging

    def start(self, album: dict):
        """Start album download process

        :param album: album dict
        """
        if self.debugging:
            logging.basicConfig(level=logging.DEBUG)

        if album['full'] is not True:
            choice = input("Track list incomplete, some tracks may be private, download anyway? (yes/no): ").lower()
            if choice == "yes" or choice == "y":
                print("Starting download process.")
                self.download_album(album)
            else:
                print("Cancelling download process.")
                return None
        else:
            self.download_album(album)

    def template_to_path(self, track: dict) -> str:
        """Create valid filepath based on template

        :param track: track metadata
        :return: filepath
        """
        logging.debug(" Generating filepath/trackname..")
        path = self.template

        if self.no_slugify:
            path = path.replace("%{artist}", track['artist'])
            path = path.replace("%{album}", track['album'])
            path = path.replace("%{title}", track['title'])
        else:
            path = path.replace("%{artist}", slugify(track['artist']))
            path = path.replace("%{album}", slugify(track['album']))
            path = path.replace("%{title}", slugify(track['title']))

        if track['track'] == "None":
            path = path.replace("%{track}", "Single")
        else:
            path = path.replace("%{track}", str(track['track']).zfill(2))

        path = u"{0}/{1}.{2}".format(self.directory, path, "mp3")

        logging.debug(" filepath/trackname generated..")
        logging.debug("\n\tPath: {}".format(path))
        return path

    @staticmethod
    def create_directory(filename: str) -> str:
        """Create directory based on filename if it doesn't exist

        :param filename: full filename
        :return: directory path
        """
        directory = os.path.dirname(filename)
        logging.debug(" Directory:\n\t{}".format(directory))
        logging.debug(" Directory doesn't exist, creating..")
        if not os.path.exists(directory):
            os.makedirs(directory)

        return directory

    def download_album(self, album: dict) -> bool:
        """Download all MP3 files in the album

        :param album: album dict
        :return: True if successful
        """
        for track_index, track in enumerate(album['tracks']):
            track_meta = {
                "artist": album['artist'],
                "label": album['label'],
                "album": album['title'],
                "title": track['title'],
                "track": track['track'],
                # TODO: Find out why the 'lyrics' key seems to vanish.
                "lyrics": track.get('lyrics', "lyrics unavailable"),
                "date": album['date']
            }

            self.num_tracks = len(album['tracks'])
            self.track_num = track_index + 1

            filepath = self.template_to_path(track_meta) + ".tmp"
            filename = filepath.rsplit('/', 1)[1]
            dirname = self.create_directory(filepath)

            logging.debug(" Current file:\n\t{}".format(filepath))

            if album['art'] and not os.path.exists(dirname + "/cover.jpg"):
                try:
                    with open(dirname + "/cover.jpg", "wb") as f:
                        r = self.session.get(album['art'], headers=self.headers)
                        f.write(r.content)
                    self.album_art = dirname + "/cover.jpg"
                except Exception as e:
                    print(e)
                    print("Couldn't download album art.")

            attempts = 0
            skip = False

            while True:
                try:
                    if not sys.version_info[:2] == (3, 6):
                        with mock.patch('http.client.parse_headers', requests_patch.parse_headers):
                            r = self.session.get(track['url'], headers=self.headers, stream=True)
                    else:
                        r = self.session.get(track['url'], headers=self.headers, stream=True)
                    file_length = int(r.headers.get('content-length', 0))
                    total = int(file_length / 100)
                    # If file exists and is still a tmp file skip downloading and encode
                    if os.path.exists(filepath):
                        self.write_id3_tags(filepath, track_meta)
                        # Set skip to True so that we don't try encoding again
                        skip = True
                        # break out of the try/except and move on to the next file
                        break
                    elif os.path.exists(filepath[:-4]) and self.overwrite is not True:
                        print("File: {} already exists and is complete, skipping..".format(filename[:-4]))
                        skip = True
                        break
                    with open(filepath, "wb") as f:
                        if file_length is None:
                            f.write(r.content)
                        else:
                            dl = 0
                            for data in r.iter_content(chunk_size=total):
                                dl += len(data)
                                f.write(data)
                                if not self.debugging:
                                    done = int(50 * dl / file_length)
                                    print_clean(
                                        "\r({}/{}) [{}{}] :: Downloading: {}".format(self.track_num, self.num_tracks,
                                                                                     "=" * done, " " * (50 - done),
                                                                                     filename[:-8]))
                    local_size = os.path.getsize(filepath)
                    # if the local filesize before encoding doesn't match the remote filesize redownload
                    if local_size != file_length and attempts != 3:
                        print("{} is incomplete, retrying..".format(filename))
                        continue
                    # if the maximum number of retry attempts is reached give up and move on
                    elif attempts == 3:
                        print("Maximum retries reached.. skipping.")
                        # Clean up incomplete file
                        os.remove(filepath)
                        break
                    # if all is well continue the download process for the rest of the tracks
                    else:
                        break
                except Exception as e:
                    print(e)
                    print("Downloading failed..")
                    return False
            if skip is False:
                self.write_id3_tags(filepath, track_meta)

        if os.path.isfile("{}/{}.not.finished".format(self.directory, __version__)):
            os.remove("{}/{}.not.finished".format(self.directory, __version__))

        # Remove album art image as it is embedded
        if self.embed_art:
            os.remove(self.album_art)

        return True

    def write_id3_tags(self, filepath: str, meta: dict):
        """Write metadata to the MP3 file

        :param filepath: name of mp3 file
        :param meta: dict of track metadata
        """
        logging.debug(" Encoding process starting..")

        filename = filepath.rsplit('/', 1)[1][:-8]

        if not self.debugging:
            print_clean("\r({}/{}) [{}] :: Encoding: {}".format(self.track_num, self.num_tracks, "=" * 50, filename))

        audio = MP3(filepath)
        audio.delete()
        audio["TIT2"] = TIT2(encoding=3, text=["title"])
        audio.save(filename=None, v1=2)

        audio = MP3(filepath)
        if self.grouping and 'label' in meta:
            audio["TIT1"] = TIT1(encoding=3, text=meta["label"])

        if self.embed_lyrics:
            audio["USLT"] = USLT(encoding=3, lang='eng', desc='', text=meta['lyrics'])

        if self.embed_art:
            with open(self.album_art, 'rb') as cover_img:
                cover_bytes = cover_img.read()
                audio["APIC"] = APIC(encoding=3, mime='image/jpeg', type=3, desc='Cover', data=cover_bytes)
        audio.save()

        audio = EasyMP3(filepath)
        audio["tracknumber"] = meta['track']
        audio["title"] = meta["title"]
        audio["artist"] = meta['artist']
        audio["album"] = meta['album']
        audio["date"] = meta["date"]
        audio.save()

        logging.debug(" Encoding process finished..")
        logging.debug(" Renaming:\n\t{} -to-> {}".format(filepath, filepath[:-4]))

        try:
            os.rename(filepath, filepath[:-4])
        except WindowsError:
            os.remove(filepath[:-4])
            os.rename(filepath, filepath[:-4])

        if not self.debugging:
            print_clean("\r({}/{}) [{}] :: Finished: {}".format(self.track_num, self.num_tracks, "=" * 50, filename))
