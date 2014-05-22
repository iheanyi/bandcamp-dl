badcamp-dl - download audio from BandCamp.com

# Synopsis

bandcamp-dl URL

# Description

bandcamp.dl is a small command-line app to download audio from BandCamp.com.
It requires the Python interpreter, version 2.7+ and is not platform specific.
It is released to the public domain, which means you can modify it, redistribute
it or use it how ever you like.

# Details
    Usage:
      bandcamp-dl.py <url>
      bandcamp-dl.py [--template=<template>] [--base-dir=<dir>]
                     [--full-album]
                     (<url> | --artist=<artist> --album=<album>)
      bandcamp-dl.py (-h | --help)
      bandcamp-dl.py (--version)


# Options

    Options:
      -h --help              Show this screen.
      -v --version           Show version.
      --artist=<artist>      The artist's slug (from the URL)
      --album=<album>        The album's slug (from the URL)
      --template=<template>  Output filename template.
                             [default: %{artist}/%{album}/%{track} - %{title}]
      --base-dir=<dir>       Base location of which all files are downloaded

# Fiename Template

The `--template` option allows users to indicate a template for the output file
names and directories. Templates can be built using special tokens with the
format of `%{artist}`. Here is a list of allowed tokens:

* `artist`: The artist name.
* `album`: The album name.
* `track`: The track number.
* `title`: The track title.

The default template is: `%{artist}/%{album}/%{track} - %{title}`.

# Bugs

Bus should be reported at [https://github.com/iheanyi/bandcamp-dl/issues]().
Please include the full output of the command when run with `--verbose`.
The output (including the first lines) contain important debugging
information. Issues without the full output are often not reproducible and
therefore do not get solved in short order, if ever.

For discussions, join us in the irc channel [#bandcamp-dl](irc://chat.freenode.net/bandcamp) on freenode.

When you submit a request, please re-read it once to avoid a couple of mistakes (you can and should use this as a checklist):

### Is the description of the issue itself sufficient?

We often get issue reports that we cannot really decipher. While in most cases we eventually get the required information after asking back multiple times, this poses an unnecessary drain on our resources. Many contributors, including myself, are also not native speakers, so we may misread some parts.

So please elaborate on what feature you are requesting, or what bug you want to be fixed. Make sure that it's obvious

- What the problem is
- How it could be fixed
- How your proposed solution would look like

If your report is shorter than two lines, it is almost certainly missing some of these, which makes it hard for us to respond to it. We're often too polite to close the issue outright, but the missing info makes misinterpretation likely. As a commiter myself, I often get frustrated by these issues, since the only possible way for me to move forward on them is to ask for clarification over and over.

For bug reports, this means that your report should contain the *complete* output of bandcamp-dl when called with the `-v` flag. The error message you get for (most) bugs even says so, but you would not believe how many of our bug reports do not contain this information.

Site support requests **must contain an example URL**. An example URL is a URL you might want to download, like `lifeformed.bandcamp.com/album/fastfall`.

###  Are you using the latest version?

This should report that you're up-to-date. About 20% of the reports we receive are already fixed, but people are using outdated versions. This goes for feature requests as well.

###  Is the issue already documented?

Make sure that someone has not already opened the issue you're trying to open. Search at the top of the window or at [https://github.com/iheanyi/bandcamp-dl/search?type=Issues](Issues) . If there is an issue, feel free to write something along the lines of "This affects me as well, with version 2015.01.01. Here is some more information on the issue: ...". While some issues may be old, a new post into them often spurs rapid activity.

###  Why are existing options not enough?

Before requesting a new feature, please have a quick peek at [the list of supported options](https://github.com/simonwjackson/bandcamp-dl/blob/master/README.md#synopsis). Many feature requests are for features that actually exist already! Please, absolutely do show off your work in the issue report and detail how the existing similar options do *not* solve your problem.

###  Is there enough context in your bug report?

People want to solve problems, and often think they do us a favor by breaking down their larger problems (e.g. wanting to skip already downloaded files) to a specific request (e.g. requesting us to look whether the file exists before downloading the info page). However, what often happens is that they break down the problem into two steps: One simple, and one impossible (or extremely complicated one).

We are then presented with a very complicated request when the original problem could be solved far easier, e.g. by recording the downloaded video IDs in a separate file. To avoid this, you must include the greater context where it is non-obvious. In particular, every feature request that does not consist of adding support for a new site should contain a use case scenario that explains in what situation the missing feature would be useful.

###  Does the issue involve one problem, and one problem only?

Some of our users seem to think there is a limit of issues they can or should open. There is no limit of issues they can or should open. While it may seem appealing to be able to dump all your issues into one ticket, that means that someone who solves one of your issues cannot mark the issue as closed. Typically, reporting a bunch of issues leads to the ticket lingering since nobody wants to attack that behemoth, until someone mercifully splits the issue into multiple ones.

In particular, every site support request issue should only pertain to services at one site (generally under a common domain, but always using the same backend technology). Do not request support for vimeo user videos, Whitehouse podcasts, and Google Plus pages in the same issue. Also, make sure that you don't post bug reports alongside feature requests. As a rule of thumb, a feature request does not include outputs of bandcamp-dl that are not immediately related to the feature at hand. Do not post reports of a network error alongside the request for a new video service.

###  Is anyone going to need the feature?

Only post features that you (or an incapicated friend you can personally talk to) require. Do not post features because they seem like a good idea. If they are really useful, they will be requested by someone who requires them.

###  Is your question about bandcamp-dl?

It may sound strange, but some bug reports we receive are completely unrelated to bandcamp-dl and relate to a different or even the reporter's own application. Please make sure that you are actually using bandcamp-dl. If you are using a UI for bandcamp-dl, report the bug to the maintainer of the actual application providing the UI. On the other hand, if your UI for bandcamp-dl fails in some way you believe is related to bandcamp-dl, by all means, go ahead and report the bug.


# Dependencies

* [BeautifulSoup](https://pypi.python.org/pypi/beautifulsoup4) - HTML Parsing
* [Mutagen](https://pypi.python.org/pypi/mutagen) - ID3 Encoding
* [Requests](https://pypi.python.org/pypi/requests) - for retriving the HTML
* [Slimit](https://pypi.python.org/pypi/slimit) - Javascript parsing

# Copyright

bandcamp-d is released into the public domain by the copytright holders

This README file was inspired by the [youtube-dl](https://github.com/rg3/youtube-dl/blob/master/README.md) docs and is likewise released into the public domain.
