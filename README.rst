bandcamp-dl
===========

download audio from BandCamp.com

Synopsis
--------

bandcamp-dl URL

Installation
------------

From PyPI
~~~~~~~~~

``pip3 install bandcamp-downloader``


Some linux distros may require that python3-pip is installed first.

From Wheel
~~~~~~~~~~

1. Download the wheel (``.whl``) from PyPI or the Releases page
2. ``cd`` to the directory containing the ``.whl`` file
3. ``pip install <filename>.whl``

[OSX] From Homebrew
~~~~~~~~~~~~~~~~~~~

``brew install bandcamp-dl``

From Source
~~~~~~~~~~~

1. Clone the project or `download and extract the zip <https://github.com/iheanyi/bandcamp-dl/archive/master.zip>`_
2. ``cd`` to the project directory containing the ``setup.py``
3. ``python setup.py install``

Description
-----------

bandcamp-dl is a small command-line app to download audio from
BandCamp.com. It requires the Python interpreter, version 3.4 (or higher) and is
not platform specific. It is released to the public domain, which means
you can modify it, redistribute it or use it how ever you like.

Details
-------

::

    Usage:
        bandcamp-dl [options] [URL]

    Arguments:
        URL         Bandcamp album/track URL

Options
-------

::

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
        -c --ok-chars=<chars>   Specify allowed chars in slugify.
                                [default: -_~]
        -s --space-char=<char>  Specify the char to use in place of spaces.
                                [default: -]
        -a --ascii-only         Only allow ASCII chars (北京 (capital of china) -> bei-jing-capital-of-china)
        -k --keep-spaces        Retain whitespace in filenames
        -u --keep-upper         Retain uppercase letters in filenames

Filename Template
-----------------

The ``--template`` option allows users to indicate a template for the
output file names and directories. Templates can be built using special
tokens with the format of ``%{artist}``. Here is a list of allowed
tokens:

-  ``artist``: The artist name.
-  ``album``: The album name.
-  ``track``: The track number.
-  ``title``: The track title.
-  ``date``: The album date.
-  ``label``: The album label.

The default template is: ``%{artist}/%{album}/%{track} - %{title}``.

Bugs
----

Bugs should be reported `here <https://github.com/iheanyi/bandcamp-dl/issues>`_.
Please include the URL and/or options used as well as the output when using the `--debug` option.

For discussions, join us in `Discord <https://discord.gg/nwdT4MP>`_.

When you submit a request, please re-read it once to avoid a couple of
mistakes (you can and should use this as a checklist):

Are you using the latest version?
---------------------------------

This should report that you're up-to-date. About 20% of the reports we
receive are already fixed, but people are using outdated versions. This
goes for feature requests as well.

Is the issue already documented?
--------------------------------

Make sure that someone has not already opened the issue you're trying to
open. Search at the top of the window or at
`Issues <https://github.com/iheanyi/bandcamp-dl/search?type=Issues>`_.
If there is an issue, feel free to write something along the lines of
"This affects me as well, with version 2015.01.01. Here is some more
information on the issue: ...". While some issues may be old, a new post
into them often spurs rapid activity.

Why are existing options not enough?
------------------------------------

Before requesting a new feature, please have a quick peek at `the list
of supported
options <https://github.com/iheanyi/bandcamp-dl/blob/master/README.rst#synopsis>`_.
Many feature requests are for features that actually exist already!
Please, absolutely do show off your work in the issue report and detail
how the existing similar options do *not* solve your problem.

Does the issue involve one problem, and one problem only?
---------------------------------------------------------

Some of our users seem to think there is a limit of issues they can or
should open. There is no limit of issues they can or should open. While
it may seem appealing to be able to dump all your issues into one
ticket, that means that someone who solves one of your issues cannot
mark the issue as closed. Typically, reporting a bunch of issues leads
to the ticket lingering since nobody wants to attack that behemoth,
until someone mercifully splits the issue into multiple ones.

Is anyone going to need the feature?
------------------------------------

Only post features that you (or an incapable friend you can
personally talk to) require. Do not post features because they seem like
a good idea. If they are really useful, they will be requested by
someone who requires them.

Is your question about bandcamp-dl?
-----------------------------------

It may sound strange, but some bug reports we receive are completely
unrelated to bandcamp-dl and relate to a different or even the
reporter's own application. Please make sure that you are actually using
bandcamp-dl. If you are using a UI for bandcamp-dl, report the bug to
the maintainer of the actual application providing the UI. On the other
hand, if your UI for bandcamp-dl fails in some way you believe is
related to bandcamp-dl, by all means, go ahead and report the bug.

Dependencies
------------

-  `BeautifulSoup4 <https://pypi.python.org/pypi/beautifulsoup4>`_ - HTML Parsing
-  `Demjson <https://pypi.python.org/pypi/demjson>`_- JavaScript dict to JSON conversion
-  `Mutagen <https://pypi.python.org/pypi/mutagen>`_ - ID3 Encoding
-  `Requests <https://pypi.python.org/pypi/requests>`_ - for retrieving the HTML
-  `Unicode-Slugify <https://pypi.python.org/pypi/unicode-slugify>`_ - A slug generator that turns strings into unicode slugs.
-  `Chardet <https://pypi.python.org/pypi/chardet>`_ - Character encoding detection
-  `Docopt <https://pypi.python.org/pypi/docopt>`_ - CLI help
-  `Six <https://pypi.python.org/pypi/six>`_ - Python 2-3 compatibility
-  `Unidecode <https://pypi.python.org/pypi/unidecode>`_ - ASCII representation of Unicode text
-  `Mock <https://pypi.python.org/pypi/mock>`_ - Library for Python unit testing
-  `PBR <https://pypi.python.org/pypi/pbr>`_ - Setuptools injection library required by Mock

Copyright
---------

bandcamp-dl is released into the public domain by the copyright holders

This README file was inspired by the
`youtube-dl <https://github.com/rg3/youtube-dl/blob/master/README.md>`_
docs and is likewise released into the public domain.
