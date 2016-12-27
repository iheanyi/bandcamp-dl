import os
import sys
import requests
from mutagen.mp3 import MP3
from mutagen.id3._id3v1 import TIT2
from mutagen.id3 import ID3
from mutagen.id3._frames import USLT
from mutagen.easyid3 import EasyID3
from slugify import slugify


class BandcampDownloader:
    def __init__(self, urls=None, template=None, directory=None, overwrite=False):
        if type(urls) is str:
            self.urls = [urls]

        self.urls = urls
        self.template = template
        self.directory = directory
        self.overwrite = overwrite

    def start(self, album):
        print("Starting download process.")
        self.download_album(album)

    def template_to_path(self, track):
        path = self.template
        path = path.replace("%{artist}", slugify(track['artist']))
        path = path.replace("%{album}", slugify(track['album']))
        path = path.replace("%{track}", str(track['track']).zfill(2))
        path = path.replace("%{title}", slugify(track['title']))
        path = "{0}/{1}.{2}".format(self.directory, path, "mp3")

        return path

    def create_directory(self, filename):
        directory = os.path.dirname(filename)
        if not os.path.exists(directory):
            os.makedirs(directory)

        return directory

    def download_album(self, album):

        for track_index, track in enumerate(album['tracks']):
            track_meta = {
                "artist": album['artist'],
                "album": album['title'],
                "title": track['title'],
                "track": track['track'],
                "date": album['date']
            }
            if 'lyrics' in track.keys():
                track_meta['lyrics'] = track['lyrics']

            print("Accessing track " + str(track_index + 1) + " of " + str(len(album['tracks'])))

            filename = self.template_to_path(track_meta)
            dirname = self.create_directory(filename)

            if not track.get('url'):
                print("Skipping track {0} - {1} as it is not available"
                      .format(track['track'], track['title']))
                continue

            try:
                track_url = track['url']
                # Check and see if HTTP is in the track_url
                if 'http' not in track_url:
                    track_url = 'http:{}'.format(track_url)

                r = requests.get(track_url, stream=True)
                file_length = r.headers.get('content-length')

                if not self.overwrite and os.path.isfile(filename):
                    file_size = os.path.getsize(filename) - 128
                    if int(file_size) != int(file_length):
                        print(filename + " is incomplete, redownloading.")
                        os.remove(filename)
                    else:
                        print("Skipping track {0} - {1} as it's already downloaded, use --overwrite to overwrite existing files"
                            .format(track['track'], track['title']))
                        continue

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
        try:
            with open(dirname + "/cover.jpg", "wb") as f:
                r = requests.get(album['art'], stream=True)
                f.write(r.content)
        except Exception as e:
            print(e)
            print("Couldn't download album art.")

        return True

    def write_id3_tags(self, filename, meta):
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

        if 'lyrics' in meta.keys():
            audio = ID3(filename)
            audio[u"USLT::'eng'"] = (USLT(encoding=3, lang=u'eng', desc=u'', text=meta['lyrics']))
            audio.save(filename)

        print("Done encoding . . .")
