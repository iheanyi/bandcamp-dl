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
import argparse
import logging
import pathlib
import sys

from bandcamp_dl import __version__
from bandcamp_dl.bandcamp import Bandcamp
from bandcamp_dl.bandcampdownloader import BandcampDownloader
from bandcamp_dl import config


def main():
    # parse config if found, else create it
    conf = config.Config()

    parser = argparse.ArgumentParser()
    parser.add_argument('URL', help="Bandcamp album/track URL", nargs="*")
    parser.add_argument('-v', '--version', action='store_true', help='Show version')
    parser.add_argument('-d', '--debug', action='store_true', help='Verbose logging', default=conf.debug)
    parser.add_argument('--artist', help="The artist's slug (from the URL)")
    parser.add_argument('--track', help="The track's slug (from the URL, for use with --artist)")
    parser.add_argument('--album', help="The album's slug (from the URL, for use with --artist)")
    parser.add_argument('--template', help=f"Output filename template, default: "
                        f"{conf.template.replace('%', '%%')}", default=conf.template)
    parser.add_argument('--base-dir', help='Base location of which all files are downloaded',
                        default=conf.base_dir)
    parser.add_argument('-f', '--full-album', help='Download only if all tracks are available',
                        action='store_true')
    parser.add_argument('-o', '--overwrite', action='store_true',
                        help=f'Overwrite tracks that already exist. Default is {conf.overwrite}.',
                        default=conf.overwrite)
    parser.add_argument('-n', '--no-art', help='Skip grabbing album art', action='store_true',
                        default=conf.no_art)
    parser.add_argument('-e', '--embed-lyrics', help='Embed track lyrics (If available)',
                        action='store_true', default=conf.embed_lyrics)
    parser.add_argument('-g', '--group', help='Use album/track Label as iTunes grouping',
                        action='store_true', default=conf.group)
    parser.add_argument('-r', '--embed-art', help='Embed album art (If available)',
                        action='store_true', default=conf.embed_art)
    parser.add_argument('-y', '--no-slugify', action='store_true', default=conf.no_slugify,
                        help='Disable slugification of track, album, and artist names')
    parser.add_argument('-c', '--ok-chars', default=conf.ok_chars,
                        help=f'Specify allowed chars in slugify, default: {conf.ok_chars}')
    parser.add_argument('-s', '--space-char', help=f'Specify the char to use in place of spaces, '
                        f'default: {conf.space_char}', default=conf.space_char)
    parser.add_argument('-a', '--ascii-only', help='Only allow ASCII chars (北京 (capital of '
                        'china) -> bei-jing-capital-of-china)', action='store_true',
                        default=conf.ascii_only)
    parser.add_argument('-k', '--keep-spaces', help='Retain whitespace in filenames',
                        action='store_true', default=conf.keep_spaces)
    parser.add_argument('-u', '--keep-upper', help='Retain uppercase letters in filenames',
                        action='store_true', default=conf.keep_upper)
    parser.add_argument('--no-confirm', help='Override confirmation prompts. Use with caution',
                        action='store_true', default=conf.no_confirm)
    parser.add_argument('--embed-genres', help='Embed album/track genres',
                        action='store_true', default=conf.embed_genres)

    arguments = parser.parse_args()
    if arguments.version:
        sys.stdout.write(f"bandcamp-dl {__version__}\n")
        return

    if arguments.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig()
    logging_handle = "bandcamp-dl"
    logger = logging.getLogger(logging_handle)

    # TODO: Its possible to break bandcamp-dl temporarily by simply erasing a line in the config, catch this and warn.
    logger.debug(f"Config/Args: {arguments}")
    if not arguments.URL:
        parser.print_usage()
        sys.stderr.write(f"{pathlib.Path(sys.argv[0]).name}: error: the following arguments are "
                         f"required: URL\n")
        sys.exit(2)

    for arg, val in [('base_dir', config.USER_HOME), ('template', config.TEMPLATE),
                     ('ok_chars', config.OK_CHARS), ('space_char', config.SPACE_CHAR)]:
        if not getattr(arguments, arg):
            setattr(arguments, arg, val)
    bandcamp = Bandcamp()

    if arguments.artist and arguments.album:
        urls = Bandcamp.generate_album_url(arguments.artist, arguments.album, "album")
    elif arguments.artist and arguments.track:
        urls = Bandcamp.generate_album_url(arguments.artist, arguments.track, "track")
    elif arguments.artist:
        urls = Bandcamp.get_full_discography(bandcamp, arguments.artist, "music")
    else:
        urls = arguments.URL

    album_list = []

    for url in urls:
        if "/album/" not in url and "/track/" not in url:
            continue
        logger.debug("\n\tURL: %s", url)
        album_list.append(bandcamp.parse(url, not arguments.no_art, arguments.embed_lyrics, arguments.embed_genres,
                                         arguments.debug))

    for album in album_list:
        logger.debug(f" Album data:\n\t{album}")
        if arguments.full_album and not album['full']:
            print("Full album not available. Skipping ", album['title'], " ...")
            # Remove not-full albums BUT continue with the rest of the albums.
            album_list.remove(album)

    if arguments.URL or arguments.artist:
        logger.debug("Preparing download process..")
        for album in album_list:
            bandcamp_downloader = BandcampDownloader(arguments, album['url'])
            logger.debug("Initiating download process..")
            bandcamp_downloader.start(album)
            # Add a newline to stop prompt mangling
            print("")
    else:
        logger.debug(r" /!\ Something went horribly wrong /!\ ")


if __name__ == '__main__':
    main()
