import logging
import os
import ast
import json
from bandcamp_dl.__init__ import __version__

user_home = os.path.expanduser('~')

if os.name == "posix":
    # Reasoning: https://www.freedesktop.org/wiki/Software/xdg-user-dirs/
    config_dir = ".config"
else:
    # .appname is fine in Windows and MacOS
    config_dir = ".bandcamp-dl"

config_path = f"{user_home}/{config_dir}/bandcamp-dl.json"


def init_config(arguments) -> json or dict:
    """Create and populate a default config, otherwise load it"""
    if os.path.isfile(config_path):
        logging.debug("Config exists, loading...")
        with open(config_path, "r") as config_file:
            config = json.load(config_file)
            first_run = False
    else:
        if os.path.exists(f"{user_home}/{config_dir}") is False:
            logging.debug("Config dir doesn't exist, creating...")
            os.mkdir(f"{user_home}/{config_dir}")
            first_run = True
        with open(config_path, "w") as config_file:
            # Where config defaults are set/added
            config = {
                "basedir": user_home,
                "template": "%{artist}/%{album}/%{track} - %{title}",
                "overwrite": False,
                "no_art": False,
                "embed_art": False,
                "embed_lyrics": False,
                "group": False,
                "no_slugify": False,
                "allowed_chars": "-_~",
                "space_char": "-",
                "ascii_only": False,
                "keep_spaces": False,
                "keep_upper": False,
                "confirmation_skip": False,
                "debug": False
            }
            config_json = json.dumps(config, indent=4)
            logging.debug("Creating config file...")
            config_file.write(config_json)

    # TODO: Session file should override config, as its essentially replaying manually set args
    session_file = f"{config['basedir']}/{__version__}.not.finished"

    if os.path.isfile(session_file) and arguments['URL'] is None:
        with open(session_file, "r") as f:
            arguments = ast.literal_eval(f.readline())
    elif first_run is False:
        with open(session_file, "w") as f:
            f.write("".join(str(arguments).split('\n')))

    if arguments['--base-dir'] is not None:
        config['basedir'] = arguments['--base-dir']

    if arguments['--template'] != config['template']:
        config['template'] = arguments['--template']

    if arguments['--overwrite'] != config['overwrite']:
        config['overwrite'] = arguments['--overwrite']

    if arguments['--no-art'] != config['no_art']:
        config['no_art'] = arguments['--no-art']

    if arguments['--embed-art'] != config['embed_art']:
        config['embed_art'] = arguments['--embed-art']

    if arguments['--embed-lyrics'] != config['embed_lyrics']:
        config['embed_lyrics'] = arguments['--embed-lyrics']

    if arguments['--group'] != config['group']:
        config['group'] = arguments['--group']

    if arguments['--no-slugify'] != config['no_slugify']:
        config['no_slugify'] = arguments['--no-slugify']

    if arguments['--ok-chars'] != config['allowed_chars']:
        config['allowed_chars'] = arguments['--ok-chars']

    if arguments['--space-char'] != config['space_char']:
        config['space_char'] = arguments['--space-char']

    if arguments['--ascii-only'] != config['ascii_only']:
        config['ascii_only'] = arguments['--ascii-only']

    if arguments['--keep-spaces'] != config['keep_spaces']:
        config['keep_spaces'] = arguments['--keep-spaces']

    if arguments['--keep-upper'] != config['keep_upper']:
        config['keep_upper'] = arguments['--keep-upper']

    if arguments['--no-confirm'] != config['confirmation_skip']:
        config['confirmation_skip'] = arguments['--no-confirm']

    if arguments['--debug'] != config['debug']:
        config['debug'] = arguments['--debug']

    return config
