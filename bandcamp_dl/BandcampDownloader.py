import wgetter

from mutagen.mp3 import MP3
from mutagen.id3 import TIT2
from mutagen.easyid3 import EasyID3
import os
from slugify import slugify

class BandcampDownloader():

    def __init__(self, urls=None, template=None, directory=None, overwrite=False):
        if type(urls) is str:
            self.urls = [urls]

        if directory:
            directory = os.path.expanduser(directory)

            if os.path.isdir(directory):
                self.directory = directory

        self.urls = urls
        self.template = template
        self.overwrite = overwrite

    def start(self, album):
        print "Starting download process."
        self.download_album(album)

    def template_to_path(self, track):
        path = self.template
        path = path.replace("%{artist}", slugify(track['artist']))
        path = path.replace("%{album}", slugify(track['album']))
        path = path.replace("%{track}", str(track['track']).zfill(2))
        path = path.replace("%{title}", slugify(track['title']))
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

            if not self.overwrite and os.path.isfile(filename):
                print "Skipping track {} - {} as it's already downloaded, use --overwrite to overwrite existing files".format(track['track'], track['title'])
                continue

            if not track.get('url'):
                print "Skipping track {} - {} as it is not available".format(track['track'], track['title'])
                continue

            try:
                track_url = track['url']
                # Check and see if HTTP is in the track_url 
                if 'http' not in track_url:
                    track_url = 'http:%s' % track_url
                tmp_file = wgetter.download(track_url, outdir=dirname)
                os.rename(tmp_file, filename)
                self.write_id3_tags(filename, track_meta)
            except Exception as e:
                print e
                print "Downloading failed.."
                return False
        try:
            tmp_art_file = wgetter.download(album['art'], outdir=dirname)
            os.rename(tmp_art_file, dirname + "/cover.jpg")
        except Exception as e:
            print e
            print "Couldn't download album art."

        return True

    def write_id3_tags(self, filename, meta):
        print "Encoding . . . "

        audio = MP3(filename)
        audio["TIT2"] = TIT2(encoding=3, text=["title"])
        audio.save()

        audio = EasyID3(filename)
        audio["tracknumber"] = meta['track']
        audio["title"] = meta['title']
        audio["artist"] = meta['artist']
        audio["album"] = meta['album']
        audio["date"] = meta['date']
        audio.save()

        print "Done encoding . . . "
