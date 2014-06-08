import wgetter

from mutagen.mp3 import MP3
from mutagen.id3 import TIT2
from mutagen.easyid3 import EasyID3
import os


class BandcampDownloader():

    def __init__(self, template=None, directory=None, overwrite=False):

        if directory:
            directory = os.path.expanduser(directory)

            if os.path.isdir(directory):
                self.directory = directory

        self.template = template
        self.overwrite = overwrite

    def start(self, album_info, artist_info):
        self.download_album(album_info, artist_info)

    def template_to_path(self, track):
        path = self.template
        path = path.replace("%{artist}", track['artist'])
        path = path.replace("%{album}", track['album'])
        path = path.replace("%{track}", track['track'])
        path = path.replace("%{title}", track['title'])
        path = u"{0}/{1}.{2}".format(self.directory, path, "mp3")

        return path

    def create_directory(self, filename):
        directory = os.path.dirname(filename)
        if not os.path.exists(directory):
            os.makedirs(directory)

        return directory

    def download_album(self, album, artist):
        for track in album['tracks']:
            track_meta = {
                "artist": album.get('artist') or artist.get('name'),
                "album": album.get('title'),
                "title": track.get('title'),
                "track": str(track.get('number')),
                "date": str(album.get('release_date').year)
            }

            filename = self.template_to_path(track_meta)
            dirname = self.create_directory(filename)

            if not self.overwrite and os.path.isfile(filename):
                print "Skiping track {} - {} as it's already downloaded, use --overwrite to overwrite existing files".format(track_meta['track'], track_meta['title'])
                continue

            if not track.get('downloadable'):
                print "Skiping track {} - {} as it is not available".format(track_meta['track'], track_meta['title'])
                continue

            try:
                tmp_file = wgetter.download(track.get('streaming_url'), outdir=dirname)
                os.rename(tmp_file, filename)
                self.write_id3_tags(filename, track_meta)
            except Exception as e:
                print e
                print "Downloading failed.."
                return False
        try:
            tmp_art_file = wgetter.download(album['large_art_url'], outdir=dirname)
            os.rename(tmp_art_file, dirname + "/cover.jpg")
        except Exception as e:
            print e
            print "Couldn't download albumart."

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
