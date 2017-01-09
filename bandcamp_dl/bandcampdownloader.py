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
        if album['full'] is not True:
            choice = input("Track list incomplete, some tracks may be private, download anyway?: ").lower()
            if choice == "yes" or choice == "y":
                print("Starting download process.")
                self.download_album(album)
            else:
                print("Cancelling download process.")
                return None
        else:
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

            self.num_tracks = len(album['tracks'])
            self.track_num = track_index + 1

            filepath = self.template_to_path(track_meta) + ".tmp"
            filename = filepath.rsplit('/', 1)[1]
            dirname = self.create_directory(filepath)

            attempts = 0
            skip = False

            while True:
                try:
                    r = requests.get(track['url'], stream=True)
                    file_length = int(r.headers['content-length'])
                    total = int(file_length/100)
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
                        dl = 0
                        for data in r.iter_content(chunk_size=total):
                            dl += len(data)
                            f.write(data)
                            done = int(50 * dl / file_length)
                            sys.stdout.write("\r({}/{}) [{}{}] :: Downloading: {}".format(self.track_num, self.num_tracks, "=" * done, " " * (50 - done), filename[:-8]))
                            sys.stdout.flush()
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
            if skip is not True:
                self.write_id3_tags(filepath, track_meta)
        if album['art']:
            try:
                with open(dirname + "/cover.jpg", "wb") as f:
                    r = requests.get(album['art'], stream=True)
                    f.write(r.content)
            except Exception as e:
                print(e)
                print("Couldn't download album art.")

        if os.path.isfile("not.finished"):
            os.remove("not.finished")
        return True

    def write_id3_tags(self, filepath: str, meta: dict):
        """
        Write metadata to the MP3 file

        :param filepath: name of mp3 file
        :param meta: dict of track metadata
        """
        filename = filepath.rsplit('/', 1)[1][:-8]

        sys.stdout.flush()
        sys.stdout.write("\r({}/{}) [{}] :: Encoding: {}".format(self.track_num, self.num_tracks, "=" * 50, filename))

        audio = MP3(filepath)
        audio["TIT2"] = TIT2(encoding=3, text=["title"])
        audio.save(filename=None, v1=2)

        audio = EasyID3(filepath)
        audio["tracknumber"] = meta['track']
        audio["title"] = meta['title']
        audio["artist"] = meta['artist']
        audio["album"] = meta['album']
        audio["date"] = meta['date']
        audio.save()

        audio.save(filepath[:-4])
        os.remove(filepath)

        sys.stdout.write("\r({}/{}) [{}] :: Finished: {}".format(self.track_num, self.num_tracks, "=" * 50, filename))
