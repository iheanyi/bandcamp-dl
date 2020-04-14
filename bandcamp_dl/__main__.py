"""bandcamp-dl

Usage:
    bandcamp-dl [options] [URL ...]

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
import importlib
from docopt import docopt
import bandcamp_dl.bandcamp
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
        urls = Bandcamp.generate_album_url(arguments['--artist'], arguments['--album'], "album")
    elif arguments['--artist'] and arguments['--track']:
        urls = Bandcamp.generate_album_url(arguments['--artist'], arguments['--track'], "track")
    elif arguments['--artist']:
        print(__doc__)
        os.remove(session_file)
        exit()
    else:
        urls = arguments['URL']
    for url in urls:
        logging.debug("\n\tURL: {}".format(url))
    # url is now a list of URLs. So lets make an albumList and append each parsed album to it.
    albumList = [];
    for url in urls:
        albumList.append(bandcamp.parse(url, not arguments['--no-art'], arguments['--embed-lyrics'], arguments['--debug']))
    
    for album in albumList:
        logging.debug(" Album data:\n\t{}".format(album))

    for album in albumList:
        if arguments['--full-album'] and not album['full']:
            print("Full album not available. Skipping ", album['title'], " ...")
            albumList.remove(album) #Remove not-full albums BUT continue with the rest of the albums.

    if arguments['URL'] or arguments['--artist']:
        logging.debug("Preparing download process..")
        for album in albumList:
            bandcamp_downloader = BandcampDownloader(arguments['--template'], basedir, arguments['--overwrite'],
                                                 arguments['--embed-lyrics'], arguments['--group'],
                                                 arguments['--embed-art'], arguments['--no-slugify'],
                                                 arguments['--debug'], album['url'])
            logging.debug("Initiating download process..")
            bandcamp_downloader.start(album)
            # Add a newline to stop prompt mangling
            print("")
    else:
        logging.debug(r" /!\ Something went horribly wrong /!\ ")


if __name__ == '__main__':
    main()
