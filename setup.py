from setuptools import setup, find_packages
from codecs import open
from os import path
import sys

appversion = "0.0.8-11"

here = path.abspath(path.dirname(__file__))

with open(here + '/bandcamp_dl/__init__.py', 'w') as initpy:
    initpy.write('__version__ = "{}"'.format(appversion))

setup(
    name='bandcamp-downloader',
    version=appversion,
    description='bandcamp-dl downloads albums and tracks from Bandcamp for you',
    long_description=open('README.rst').read(),
    url='https://github.com/iheanyi/bandcamp-dl',
    author='Iheanyi Ekechukwu',
    author_email='iekechukwu@gmail.com',
    license='Unlicense',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Multimedia :: Sound/Audio',
        'License :: Public Domain',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords=['bandcamp', 'downloader', 'music', 'cli', 'albums', 'dl'],
    packages=find_packages(exclude=['tests']),
    python_requires='~=3.4',
    install_requires=[
        'beautifulsoup4',
        'demjson',
        'docopt',
        'mutagen',
        'requests',
        'unicode-slugify',
        'mock',
        'chardet',
    ],
    extras_require={
        'dev': [
            'requests-cache',
            'pytest'
        ]
    },
    entry_points={
        'console_scripts': [
            'bandcamp-dl=bandcamp_dl.__main__:main',
        ],
    },
)
