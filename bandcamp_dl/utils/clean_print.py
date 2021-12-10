import shutil


def print_clean(msg):
    terminal_size = shutil.get_terminal_size()
    print(f'{msg}{" " * (int(terminal_size[0]) - len(msg))}', end='')
