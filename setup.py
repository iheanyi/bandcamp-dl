#!/usr/bin/python

from setuptools import setup, find_packages

version = '0.0.3'

setup(
    name='bandcamp-downloader',
    version=version,
    description='bandcamp-dl downloads albums and tracks from Bandcamp for you',
    long_description=open('README.md').read(),
    author='Iheanyi Ekechukwu',
    author_email='iekechukwu@gmail.com',
    license='Unlicense',
    keywords=['bandcamp', 'downloader', 'music', 'cli', 'albums', 'dl'],
    url='http://github.com/iheanyi/bandcamp-dl',
    packages=find_packages(),
    package_data={},
    install_requires=[
        'wgetter>=0.6',
        'slimit>=0.8.1',
        'ply==3.4',
        'mutagen>=1.31',
        'lxml>=3.5.0',
        'docopt>=0.6.2',
        'beautifulsoup4>=4.4.1',
        'slugify==0.0.1',
    ],
    entry_points={
        'console_scripts': [
            'bandcamp-dl=bandcamp_dl.bandcamp_dl:main',
        ],
    },
)
