import os
import sys


def print_clean(msg):
    terminal_size = os.get_terminal_size()
    msg_length = len(msg)
    sys.stdout.write("{}{}".format(msg, " " * (int(terminal_size[0]) - msg_length)))