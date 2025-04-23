import argparse
import ast
import json
import os
import pathlib
import sys

from bandcamp_dl import __version__

TEMPLATE = '%{artist}/%{album}/%{track} - %{title}'
OK_CHARS = '-_~'
SPACE_CHAR = '-'
USER_HOME = pathlib.Path.home()
# For Linux/BSD https://www.freedesktop.org/wiki/Software/xdg-user-dirs/
# For Windows ans MacOS .appname is fine
CONFIG_PATH = USER_HOME / (".config" if os.name == "posix" else ".bandcamp-dl") / "bandcamp-dl.json"


class Config(dict):

    # TODO: change this to dataclass when support for Python < 3.7 is dropped
    _defaults = {"base_dir": str(USER_HOME),  # TODO: pass the Path object instead?
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
                 "debug": False,
                 "embed_genres": False}

    def __init__(self, dict_=None):
        if dict_ is None:
            super().__init__(**Config._defaults)
        else:
            super().__init__(**dict_)
        self.__dict__ = self
        self._read_write_config()

    def _read_write_config(self):
        if CONFIG_PATH.exists():
            with pathlib.Path.open(CONFIG_PATH) as fobj:
                try:
                    user_config = json.load(fobj)
                    # change hyphen with underscore
                    user_config = {k.replace('-', '_'): v for k, v in user_config.items()}
                    # overwrite defaults with user provided config
                    self._update_with_dict(user_config)
                except json.JSONDecodeError:
                    # NOTE: we don't have logger yet
                    sys.stderr.write(f"Malformed configuration file `{CONFIG_PATH}'. Check json syntax.\n")
        else:
            # No config found - populate it with the defaults
            with pathlib.Path.open(CONFIG_PATH, mode="w") as fobj:
                conf = {k.replace('_', '-'): v for k, v in self.items()}
                json.dump(conf, fobj)
            sys.stderr.write(f"Configuration has been written to `{CONFIG_PATH}'.\n")

    def _update_with_dict(self, dict_):
        for key, val in dict_.items():
            if key not in self:
                continue
            self[key] = val
