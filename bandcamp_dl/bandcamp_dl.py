#!/usr/bin/python

"""bandcamp-dl
Usage:
  bandcamp-dl.py <url>
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
"""

""" Coded by:

Iheanyi Ekechukwu
    http://twitter.com/kwuchu
    http://github.com/iheanyi

Simon W. Jackson
    http://miniarray.com
    http://twitter.com/miniarray
    http://github.com/miniarray

Iheanyi:
    Feel free to use this in any way you wish. I made this just for fun.
    Shout out to darkf for writing a helper function for parsing the JavaScript! """


from docopt import docopt
from Bandcamp import Bandcamp
from BandcampDownloader import BandcampDownloader
import os

def main():
    arguments = docopt(__doc__, version='bandcamp-dl 1.0')
    bandcamp = Bandcamp()

    if (arguments['--artist'] and arguments['--album']):
        url = Bandcamp.generate_album_url(arguments['--artist'], arguments['--album'])
    else:
        url = arguments['<url>']

    album = bandcamp.parse(url)
    basedir = arguments['--base-dir'] or os.getcwd()

    if not album:
        print "The url {} is not a valid bandcamp page.".format(url)
    elif arguments['--full-album'] and not album['full']:
        print "Full album not available. Skipping..."
    else:
        bandcamp_downloader = BandcampDownloader(url, arguments['--template'], basedir, arguments['--overwrite'])
        bandcamp_downloader.start(album)

if __name__ == '__main__':
    main()
