"""Naval Fate.
Usage:
  bandcamp-dl.py download [<url> | --artist=<artist> --album=<album>]
  bandcamp-dl.py (-h | --help)
  bandcamp-dl.py --version

Options:
  -h --help     Show this screen.
  --version     Show version.
  --artist=<artist>  Speed in knots
  --album=<album>  Speed in knots

"""

from docopt import docopt
from Bandcamp import Bandcamp

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


if __name__ == '__main__':
    arguments = docopt(__doc__, version='bandcamp-dl 1.0')
    bandcamp = Bandcamp()

    print arguments

    if (arguments['download']):
        if (arguments['--artist'] and arguments['--album']):
            url = Bandcamp.generate_album_url(arguments['--artist'], arguments['--album']) 
            bandcamp.parse_album_page(url)

        elif (arguments['<url>']):
            bandcamp.parse_album_page(arguments['<url>'])
