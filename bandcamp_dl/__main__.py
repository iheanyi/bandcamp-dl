"""bandcamp-dl

Usage:
    bandcamp-dl [url]
    bandcamp-dl [--template=<template>] [--base-dir=<dir>]
                [--full-album]
                (<url> | --artist=<artist> --album=<album> | --artist=<artist> --track=<track>)
                [--overwrite]
                [--no-art]
                [--embed-lyrics]
                [--group]
                [--embed-art]
                [--no-slugify]
    bandcamp-dl (-h | --help)
    bandcamp-dl (--version)

Options:
    -h --help                   Show this screen.
    -v --version                Show version.
    -a --artist=<artist>        The artist's slug (from the URL)
    -s --track=<track>          The track's slug (from the URL)
    -b --album=<album>          The album's slug (from the URL)
    -t --template=<template>    Output filename template.
                                [default: %{artist}/%{album}/%{track} - %{title}]
    -d --base-dir=<dir>         Base location of which all files are downloaded.
    -f --full-album             Download only if all tracks are available.
    -o --overwrite              Overwrite tracks that already exist. Default is False.
    -n --no-art                 Skip grabbing album art
    -e --embed-lyrics           Embed track lyrics (If available)
    -g --group                  Use album/track Label as iTunes grouping
    -r --embed-art              Embed album art (If available)
    -n --no-slugify             Disable slugification of track, album, and artist names.
"""
"""
Coded by:

Iheanyi Ekechukwu
    http://twitter.com/kwuchu
    http://github.com/iheanyi

Simon W. Jackson
    http://miniarray.com
    http://twitter.com/miniarray
    http://github.com/miniarray

Anthony Forsberg:
    http://evolution0.github.io
    http://github.com/evolution0

Iheanyi:
    Feel free to use this in any way you wish. I made this just for fun.
    Shout out to darkf for writing the previous helper function for parsing the JavaScript!
"""

import os
import ast

from docopt import docopt

from bandcamp_dl.bandcamp import Bandcamp
from bandcamp_dl.bandcampdownloader import BandcampDownloader


def main():
    arguments = docopt(__doc__, version='bandcamp-dl 0.0.8-1')

    bandcamp = Bandcamp()

    basedir = arguments['--base-dir'] or os.getcwd()
    session_file = basedir + "/not.finished"

    if os.path.isfile(session_file):
        with open(session_file, "r") as f:
            arguments = ast.literal_eval(f.readline())
    elif arguments['<url>'] is None and arguments['--artist'] is None:
        print(__doc__)
    else:
        with open(session_file, "w") as f:
            f.write("".join(str(arguments).split('\n')))

    if arguments['--artist'] and arguments['--album']:
        url = Bandcamp.generate_album_url(arguments['--artist'], arguments['--album'], "album")
    elif arguments['--artist'] and arguments['--track']:
        url = Bandcamp.generate_album_url(arguments['--artist'], arguments['--track'], "track")
    else:
        url = arguments['<url>']

    if arguments['--no-art']:
        album = bandcamp.parse(url, False)
    else:
        album = bandcamp.parse(url)

    if not album:
        print("The url {} is not a valid bandcamp page.".format(url))
    elif arguments['--full-album'] and not album['full']:
        print("Full album not available. Skipping...")
    else:
        bandcamp_downloader = BandcampDownloader(url, arguments['--template'], basedir, arguments['--overwrite'],
                                                 arguments['--embed-lyrics'], arguments['--group'],
                                                 arguments['--embed-art'], arguments['--no-slugify'])
        bandcamp_downloader.start(album)


if __name__ == '__main__':
    main()
