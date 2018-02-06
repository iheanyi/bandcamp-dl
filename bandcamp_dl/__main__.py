"""bandcamp-dl

Usage:
    bandcamp-dl [options] [URL]

Arguments:
    URL         Bandcamp album/track URL

Options:
    -h --help               Show this screen.
    -v --version            Show version.
    -d --debug              Verbose logging.
    --artist=<artist>       The artist's slug (from the URL, --track or --album is required)
    --track=<track>         The track's slug (from the URL, for use with --artist)
    --album=<album>         The album's slug (from the URL, for use with --artist)
    --template=<template>   Output filename template.
                            [default: %{artist}/%{album}/%{track} - %{title}]
    --base-dir=<dir>        Base location of which all files are downloaded.
    -f --full-album         Download only if all tracks are available.
    -o --overwrite          Overwrite tracks that already exist. Default is False.
    -n --no-art             Skip grabbing album art.
    -e --embed-lyrics       Embed track lyrics (If available)
    -g --group              Use album/track Label as iTunes grouping.
    -r --embed-art          Embed album art (If available)
    -y --no-slugify         Disable slugification of track, album, and artist names.
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
import logging

from docopt import docopt

from bandcamp_dl.bandcamp import Bandcamp
from bandcamp_dl.bandcampdownloader import BandcampDownloader
from bandcamp_dl.__init__ import __version__


def main():
    arguments = docopt(__doc__, version='bandcamp-dl {}'.format(__version__))

    if arguments['--debug']:
        logging.basicConfig(level=logging.DEBUG)

    bandcamp = Bandcamp()

    basedir = arguments['--base-dir'] or os.getcwd()
    session_file = "{}/{}.not.finished".format(basedir, __version__)

    if os.path.isfile(session_file) and arguments['URL'] is None:
        with open(session_file, "r") as f:
            arguments = ast.literal_eval(f.readline())
    else:
        with open(session_file, "w") as f:
            f.write("".join(str(arguments).split('\n')))

    if arguments['--artist'] and arguments['--album']:
        url = Bandcamp.generate_album_url(arguments['--artist'], arguments['--album'], "album")
    elif arguments['--artist'] and arguments['--track']:
        url = Bandcamp.generate_album_url(arguments['--artist'], arguments['--track'], "track")
    elif arguments['--artist']:
        print(__doc__)
        os.remove(session_file)
        exit()
    else:
        url = arguments['URL']

    logging.debug("\n\tURL: {}".format(url))

    if arguments['--no-art']:
        album = bandcamp.parse(url, False, arguments['--embed-lyrics'], arguments['--debug'])
    else:
        album = bandcamp.parse(url, True, arguments['--embed-lyrics'], arguments['--debug'])

    logging.debug(" Album data:\n\t{}".format(album))

    if arguments['--full-album'] and not album['full']:
        print("Full album not available. Skipping...")
    elif arguments['URL'] or arguments['--artist']:
        logging.debug("Preparing download process..")
        bandcamp_downloader = BandcampDownloader(arguments['--template'], basedir, arguments['--overwrite'],
                                                 arguments['--embed-lyrics'], arguments['--group'],
                                                 arguments['--embed-art'], arguments['--no-slugify'],
                                                 arguments['--debug'], url)
        logging.debug("Initiating download process..")
        bandcamp_downloader.start(album)
        # Add a newline to stop prompt mangling
        print("")
    else:
        logging.debug(" /!\ Something went horribly wrong /!\ ")


if __name__ == '__main__':
    main()
