#!/usr/bin/python

"""bandcamp-dl
Usage:
  bandcamp-dl.py [--template=<template>] [--base-dir=<dir>]
                 [--full-album]
                 (<url> | --artist=<artist> --discography)
                 [--overwrite]
  bandcamp-dl.py [--template=<template>] [--base-dir=<dir>]
                 [--full-album]
                 (<url> | --artist=<artist> --album=<album>)
                 [--overwrite]
  bandcamp-dl.py (-h | --help)
  bandcamp-dl.py (--version)

Options:
  -h --help                 Show this screen.
  -v --version              Show version.
  -a --artist=<artist>      The artist's slug (from the URL)
  -b --album=<album>        The album's slug (from the URL)
  -t --template=<template>  Output filename template.
                            [default: %{artist}/%{album}/%{track} - %{title}]
  -d --base-dir=<dir>       Base location of which all files are downloaded.
  -f --full-album           Download only if all tracks are availiable.
  -o --overwrite           Overwrite tracks that already exist. Default is False.
  -d  --discography           Download the available songs from the artists discography.
"""

""" Coded by:

Iheanyi Ekechukwu
    http://twitter.com/kwuchu
    http://github.com/iheanyi

Simon W. Jackson
    http://miniarray.com
    http://twitter.com/miniarray
    http://github.com/miniarray

Joseph Kahn
    http://twitter.com/JosephBKahn
    http://github.com/JBKahn
    http://jbkahn.github.io/

Iheanyi:
    Feel free to use this in any way you wish. I made this just for fun. """


from docopt import docopt
from Bandcamp import Bandcamp
from BandcampDownloader import BandcampDownloader
import os


if __name__ == '__main__':
    arguments = docopt(__doc__, version='bandcamp-dl 1.0')
    bandcamp = Bandcamp(discography=arguments.get('--discography'), artist=arguments['--artist'], album=arguments['--album'])
    albums_info, artist_info = bandcamp.get_album_and_artist_info_from_query()
    basedir = arguments['--base-dir'] or os.path.dirname(os.path.realpath(__file__))
    if not albums_info:
        print "No album by that name could be found by that artist"
    else:
        bandcamp_downloader = BandcampDownloader(arguments['--template'], basedir, arguments['--overwrite'])
        for album in albums_info:
            if arguments['--full-album'] and not albums_info['full']:
                print "Full {} album not availiable. Skipping..".format(album.get('title'))
            else:
                print "Downloading album {}".format(album.get('title'))
                bandcamp_downloader.start(album, artist_info)
