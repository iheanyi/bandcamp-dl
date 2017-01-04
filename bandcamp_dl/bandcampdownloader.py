import os
import sys
import requests
from mutagen.mp3 import MP3
from mutagen.id3._frames import TIT2
from mutagen.easyid3 import EasyID3
from slugify import slugify


class BandcampDownloader:
    def __init__(self, urls=None, template=None, directory=None, overwrite=False):
        """
        Initialization function

        :param urls: list of urls
        :param template: filename template
        :param directory: download location
        :param overwrite: if True overwrite existing files
        """
        if type(urls) is str:
            self.urls = [urls]

        self.urls = urls
        self.template = template
        self.directory = directory
        self.overwrite = overwrite

    def start(self, album: dict):
        """
        Start album download process

        :param album: album dict
        """
        print("Starting download process.")
        self.download_album(album)

    def template_to_path(self, track: dict) -> str:
        """
        Create valid filepath based on track metadata

        :param track: track metadata
        :return: filepath
        """
        path = self.template
        path = path.replace("%{artist}", slugify(track['artist']))
        path = path.replace("%{album}", slugify(track['album']))
        path = path.replace("%{track}", str(track['track']).zfill(2))
        path = path.replace("%{title}", slugify(track['title']))
        path = u"{0}/{1}.{2}".format(self.directory, path, "mp3")

        return path

    @staticmethod
    def create_directory(filename: str) -> str:
        """
        Create directory based on filename if it doesn't exist

        :param filename: full filename
        :return: directory path
        """
        directory = os.path.dirname(filename)
        if not os.path.exists(directory):
            os.makedirs(directory)

        return directory

    def download_album(self, album: dict) -> bool:
        """
        Download all MP3 files in the album

        :param album: album dict
        :return: True if successful
        """
        for track_index, track in enumerate(album['tracks']):
            track_meta = {
                "artist": album['artist'],
                "album": album['title'],
                "title": track['title'],
                "track": track['track'],
                "date": album['date']
            }

            print("Accessing track " + str(track_index + 1) + " of " + str(len(album['tracks'])))

            filename = self.template_to_path(track_meta)
            dirname = self.create_directory(filename)

            if not track['url']:
                print("Skipping track {0} - {1} as it is not available"
                      .format(track['track'], track['title']))
                continue

            try:
                track_url = track['url']

                r = requests.get(track_url, stream=True)
                file_length = r.headers.get('content-length')

                with open(filename, "wb") as f:
                    print("Downloading: " + filename[:-4])
                    if file_length is None:
                        f.write(r.content)
                    else:
                        dl = 0
                        total_length = int(file_length)
                        for data in r.iter_content(chunk_size=int(total_length/100)):
                            dl += len(data)
                            f.write(data)
                            done = int(50 * dl / total_length)
                            sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50 - done)))
                            sys.stdout.flush()
                self.write_id3_tags(filename, track_meta)
            except Exception as e:
                print(e)
                print("Downloading failed..")
                return False
        if album['art']:
            try:
                with open(dirname + "/cover.jpg", "wb") as f:
                    r = requests.get(album['art'], stream=True)
                    f.write(r.content)
            except Exception as e:
                print(e)
                print("Couldn't download album art.")

        return True

    @staticmethod
    def write_id3_tags(filename: str, meta: dict):
        """
        Write metadata to the MP3 file

        :param filename: name of mp3 file
        :param meta: dict of track metadata
        """
        print("\nEncoding . . .")

        audio = MP3(filename)
        audio["TIT2"] = TIT2(encoding=3, text=["title"])
        audio.save(filename=None, v1=2)

        audio = EasyID3(filename)
        audio["tracknumber"] = meta['track']
        audio["title"] = meta['title']
        audio["artist"] = meta['artist']
        audio["album"] = meta['album']
        audio["date"] = meta['date']
        audio.save()

        audio.save(filename)
        print("Done encoding . . .")
