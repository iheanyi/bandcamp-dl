import argparse
import ast
import json
import logging
import os

from bandcamp_dl import __version__

TEMPLATE = '%{artist}/%{album}/%{track} - %{title}'
OK_CHARS = '-_~'
SPACE_CHAR = '-'
USER_HOME = os.path.expanduser('~')
DEFAULT_CONFIG = {
    "base_dir": USER_HOME,
    "template": TEMPLATE,
    "overwrite": False,
    "no_art": False,
    "embed_art": False,
    "embed_lyrics": False,
    "group": False,
    "no_slugify": False,
    "ok_chars": OK_CHARS,
    "space_char": SPACE_CHAR,
    "ascii_only": False,
    "keep_spaces": False,
    "keep_upper": False,
    "no_confirm": False,
    "debug": False
}

if os.name == "posix":
    # Reasoning: https://www.freedesktop.org/wiki/Software/xdg-user-dirs/
    config_dir = ".config"
else:
    # .appname is fine in Windows and MacOS
    config_dir = ".bandcamp-dl"

config_path = f"{USER_HOME}/{config_dir}/bandcamp-dl.json"

logger = logging.getLogger("bandcamp-dl").getChild("Config")


def init_config(parser) -> json or dict:
    """Create and populate a default config, otherwise load it"""
    if os.path.isfile(config_path):
        logger.debug("Config exists, loading...")
        with open(config_path, "r") as config_file:
            config_json = json.load(config_file)
            parser.set_defaults(**config_json)
            config = arguments = parser.parse_args()
            first_run = False
    else:
        first_run = True
        if os.path.exists(f"{USER_HOME}/{config_dir}") is False:
            logger.debug("Config dir doesn't exist, creating...")
            os.mkdir(f"{USER_HOME}/{config_dir}")
        with open(config_path, "w") as config_file:
            # Where config defaults are set/added
            config = dict(DEFAULT_CONFIG)
            config_json = json.dumps(config, indent=4)
            logger.debug("Creating config file...")
            config_file.write(config_json)
            parser.set_defaults(**config)
            config = arguments = parser.parse_args()

    # TODO: Session file should override config, as its essentially replaying manually set args
    session_file = f"{arguments.base_dir}/{__version__}.not.finished"

    if os.path.isfile(session_file) and arguments.URL is None:
        with open(session_file, "r") as f:
            parser.set_defaults(**json.load(f))
            # We don't call parse_args here as we want the session file to overwrite everything
    elif first_run is False:
        with open(session_file, "w") as f:
            f.write("".join(str(vars(arguments))))

    return config
