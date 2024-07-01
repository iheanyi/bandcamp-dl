import ast
import json
import logging
import os

from bandcamp_dl import __version__

TEMPLATE = '%{artist}/%{album}/%{track} - %{title}'
OK_CHARS = '-_~'
SPACE_CHAR = '-'
USER_HOME = os.path.expanduser('~')

if os.name == "posix":
    # Reasoning: https://www.freedesktop.org/wiki/Software/xdg-user-dirs/
    config_dir = ".config"
else:
    # .appname is fine in Windows and MacOS
    config_dir = ".bandcamp-dl"

config_path = f"{user_home}/{config_dir}/bandcamp-dl.json"
first_run = True


def merge(dict_1, dict_2):
    """Merge two dictionaries.

    Values that evaluate to true take priority over falsy values.
    `dict_1` takes priority over `dict_2`.

    """
    return dict(
        (str(key), dict_1.get(key) or dict_2.get(key))
        for key in set(dict_2) | set(dict_1)
    )


def init_config(arguments) -> json or dict:
    """Create and populate a default config, otherwise load it"""
    if os.path.isfile(config_path):
        logging.debug("Config exists, loading...")
        with open(config_path, "r") as config_file:
            config = json.load(config_file)
            first_run = False
    else:
        if os.path.exists(f"{USER_HOME}/{config_dir}") is False:
            logging.debug("Config dir doesn't exist, creating...")
            os.mkdir(f"{USER_HOME}/{config_dir}")
            first_run = True
        with open(config_path, "w") as config_file:
            # Where config defaults are set/added
            config = {"base-dir": USER_HOME,
                      "template": TEMPLATE,
                      "overwrite": False,
                      "no-art": False,
                      "embed-art": False,
                      "embed-lyrics": False,
                      "group": False,
                      "no-slugify": False,
                      "ok-chars": OK_CHARS,
                      "space-char": SPACE_CHAR,
                      "ascii-only": False,
                      "keep-spaces": False,
                      "keep-upper": False,
                      "no-confirm": False,
                      "debug": False}
            config_json = json.dumps(config, indent=4)
            logging.debug("Creating config file...")
            config_file.write(config_json)

    # TODO: Replace all this shuffling around values with a dict comprehension if possible !!!!
    # TODO: Session file should override config, as its essentially replaying manually set args
    session_file = f"{config['base-dir']}/{__version__}.not.finished"

    if os.path.isfile(session_file) and arguments.URL is None:
        with open(session_file, "r") as f:
            arguments = ast.literal_eval(f.readline())
    elif first_run is False:
        with open(session_file, "w") as f:
            f.write("".join(str(vars(arguments))))

    config = merge(arguments, config)

    return config
