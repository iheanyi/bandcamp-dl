from setuptools import setup, find_packages
import pathlib

appversion = "0.0.11-dev"

here = pathlib.Path(__file__).parent.resolve()

with open(f'{here}/bandcamp_dl/__init__.py', 'w') as initpy:
    initpy.write(f'__version__ = "{appversion}"')

setup(
    name='bandcamp-downloader',
    version=appversion,
    description='bandcamp-dl downloads albums and tracks from Bandcamp for you',
    long_description=open('README.rst').read(),
    long_description_content_type='text/x-rst',
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
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3 :: Only',
    ],
    keywords=['bandcamp', 'downloader', 'music', 'cli', 'albums', 'dl'],
    packages=find_packages(exclude=['tests']),
    python_requires='>=3.4',
    install_requires=[
        'beautifulsoup4',
        'lxml',
        'demjson3',
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
    project_urls={
        'Bug Reports': 'https://github.com/iheanyi/bandcamp-dl/issues',
        'Source': 'https://github.com/iheanyi/bandcamp-dl',
    },
)
