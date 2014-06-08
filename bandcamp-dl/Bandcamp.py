from datetime import datetime
import requests


class Bandcamp:

    def __init__(self, discography=False, artist="", album=""):
        self.get_discography = discography
        self.artist_query = artist or ""
        self.album_query = album or ""

    def get_artist_information(self):
        artist_request = requests.get("http://api.bandcamp.com/api/band/3/search?key=vatnajokull&name={}".format(self.artist_query.replace(" ", "%20")))
        return artist_request.json().get('results')[0]

    def get_artist_discography(self, band_id):
        discography_request = requests.get("http://api.bandcamp.com/api/band/3/discography?key=vatnajokull&band_id={}".format(band_id))
        # Createa a dictionary out of the results dictionary where each album's dictionary is the value and the album name is the key
        albums = dict((d['title'].lower(), dict(d, index=index)) for (index, d) in enumerate(discography_request.json().get('discography')))
        # The cool thing we can do here is to download all available albums since we know all the IDs
        return albums

    def get_album(self, full_discography):
        if self.get_discography:
            albums_to_download = full_discography.values()
        else:
            albums_to_download = [full_discography.get(self.album_query.lower())]

        albums_info = []

        for album in albums_to_download:
            # import ipdb; ipdb.set_trace();
            if not album:
                print "The album does not exist"
                continue
            if not album.get('downloadable'):
                print "The {} album is not downloadable".format(album.get('title'))
                continue
            album_request = requests.get("http://api.bandcamp.com/api/album/2/info?key=vatnajokull&album_id={}".format(album.get('album_id')))
                # keys: [u'small_art_url', u'about', u'album_id', u'url', u'band_id', u'release_date', u'title', u'credits', u'tracks', u'downloadable', u'large_art_url']
                # example:
                # {
                #   "url": "http://music.biggiantcircles.com/album/the-glory-days?pk=564",
                #   "about": "Shoutouts to my Kickstarter backers, my many many Twitch and Youtube friends (including but not limited to Sevadus, MANvsGAME, Bacon Donut, wolv21, IAMSp00n, Coestar, ZombiUnicorn, WelshPixie, iHasCupquake, and many many many more), to OverClocked ReMix, to my followers on Twitter and Facebook, and the thousands of people out there working hard to create memorable game experiences for all of us.  This album is for you!",
                #   "large_art_url": "http://f0.bcbits.com/img/a2358396975_2.jpg",
                #   "downloadable": 2,
                #   "credits": "All songs written and produced by Jimmy Hinson\r\nhttp://twitter.com/biggiantcircles\r\nhttp://facebook.com/biggiantcircles\r\nhttp://youtube.com/biggiantcircles\r\n\r\nMastering by Dave Shumway and Jimmy Hinson\r\nhttp://twitter.com/mediaeaters\r\n\r\nAlbum Cover by Ian Wilding\r\nhttp://twitter.com/iwilding\r\n\r\nAdditional album artwork by Ian Wilding, Jessie Lam, Paul Hubans, Ian Wexler, and Junkboy\r\nhttp://twitter.com/axl99\r\nhttp://twitter.com/phubans\r\nhttp://twitter.com/ianwexl0rz\r\nhttp://twitter.com/jnkboy\r\n\r\nKickstarter consultation by zircon\r\nhttp://twitter.com/zirconst",
                #   "album_id": 2667222639,
                #   "band_id": 1018396519,
                #   "tracks": [...],
                #   "small_art_url": "http://f0.bcbits.com/img/a2358396975_3.jpg",
                #   "title": "The Glory Days",
                #   "release_date": 1392336000
                #   }

                # example track
                # {
                #   "about": "Shoutouts to all my friends at Mojang, who somehow manage to keep getting me into all the amazing parties that Notch throws!",
                #   "url": "/track/no-party-like-a-mojang-party?pk=564",
                #   "streaming_url": "http://popplers5.bandcamp.com/download/track?enc=mp3-128&fsig=a81c2770273a26d30cda1d7427197ceb&id=595907577&stream=1&ts=1402202096.0",
                #   "album_id": 2667222639,
                #   "downloadable": 2,
                #   "band_id": 1018396519,
                #   "number": 3,
                #   "track_id": 595907577,
                #   "title": "No Party Like a Mojang Party",
                #   "duration": 349.44
                # },
            album_info = album_request.json()
            if album_info.get('error'):
                print "The {} album is could not be downloaded at this time".format(album.get('title'))
                continue

            album_info['release_date'] = datetime.fromtimestamp(album_info.get('release_date'))
            album_info['full'] = sum([track.get('downloadable') is not None for track in album_info.get('tracks')]) is len(album_info.get('tracks'))
            albums_info.append(album_info)

        return albums_info

    def get_album_and_artist_info_from_query(self):
        # this function needs a lot of work to make it prettier.
        # Using the key from the api docs right now. I don't have an api key.
        artist_info = self.get_artist_information()
        albums = self.get_artist_discography(artist_info.get('band_id'))
        albums_info = self.get_album(albums)

        return albums_info, artist_info
