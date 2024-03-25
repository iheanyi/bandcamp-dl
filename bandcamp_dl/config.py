import ast
import json
import logging
import os

from bandcamp_dl import __version__

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
            config = {"--base-dir": user_home,
                      "--template": "%{artist}/%{album}/%{track} - %{title}",
                      "--overwrite": False,
                      "--no-art": False,
                      "--embed-art": False,
                      "--embed-lyrics": False,
                      "--group": False,
                      "--no-slugify": False,
                      "--ok-chars": "-_~",
                      "--space-char": "-",
                      "--ascii-only": False,
                      "--keep-spaces": False,
                      "--keep-upper": False,
                      "--no-confirm": False,
                      "--debug": False}
            config_json = json.dumps(config, indent=4)
            logging.debug("Creating config file...")
            config_file.write(config_json)

    # TODO: Replace all this shuffling around values with a dict comprehension if possible !!!!
    # TODO: Session file should override config, as its essentially replaying manually set args
    session_file = f"{config['--base-dir']}/{__version__}.not.finished"

    if os.path.isfile(session_file) and arguments['URL'] is None:
        with open(session_file, "r") as f:
            arguments = ast.literal_eval(f.readline())
    elif first_run is False:
        with open(session_file, "w") as f:
            f.write("".join(str(arguments).split('\n')))

    config = {key: config[key] if arguments.get(key, config[key]) is None
              else arguments.get(key, config[key]) for key in config}

    return config
