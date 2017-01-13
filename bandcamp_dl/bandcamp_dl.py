"""bandcamp-dl

Usage:
    bandcamp-dl [url]
    bandcamp-dl [--template=<template>] [--base-dir=<dir>]
                [--full-album]
                (<url> | --artist=<artist> --album=<album>)
                [--overwrite]
                [--no-art]
    bandcamp-dl (-h | --help)
    bandcamp-dl (--version)

Options:
    -h --help                   Show this screen.
    -v --version                Show version.
    -a --artist=<artist>        The artist's slug (from the URL)
    -b --album=<album>          The album's slug (from the URL)
    -t --template=<template>    Output filename template.
                                [default: %{artist}/%{album}/%{track} - %{title}]
    -d --base-dir=<dir>         Base location of which all files are downloaded.
    -f --full-album             Download only if all tracks are available.
    -o --overwrite              Overwrite tracks that already exist. Default is False.
    -n --no-art                 Skip grabbing album art
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
from .bandcamp import Bandcamp
from .bandcampdownloader import BandcampDownloader


def main():
    arguments = docopt(__doc__, version='bandcamp-dl 0.0.7-02')
    bandcamp = Bandcamp()

    basedir = arguments['--base-dir'] or os.getcwd()
    session_file = basedir + "/not.finished"

    if os.path.isfile(session_file):
        with open(session_file, "r") as f:
            arguments = ast.literal_eval(f.readline())
    elif arguments['<url>'] is None:
        print(__doc__)
    else:
        with open(session_file, "w") as f:
            f.write("".join(str(arguments).split('\n')))

    if arguments['--artist'] and arguments['--album']:
        url = Bandcamp.generate_album_url(arguments['--artist'], arguments['--album'])
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
        bandcamp_downloader = BandcampDownloader(url, arguments['--template'], basedir, arguments['--overwrite'])
        bandcamp_downloader.start(album)

if __name__ == '__main__':
    main()
