#!/usr/bin/env python3
import subprocess
import os
import re
from configparser import ConfigParser
from distutils.command.install import install
from distutils.core import setup

dirname = os.path.dirname(__file__)
if dirname != '':
    os.chdir(os.path.dirname(__file__))

config = ConfigParser()
config.read('etc/szotar_net/config.ini')
version = config.get('core', 'version')


def md_to_rest(f):
    '''Very hacky.'''

    s = ''
    for line in f:
        line = re.sub(r'!\[[^]]*\]\((.*)\)', r'\1', line)
        s += line

    s = s.replace(":\n\n", "::\n\n")
    return s


with open('README.md', 'r') as f:
    longdesc = md_to_rest(f)

setup(name='szotar_net',
      version=version,
      description='Terminal-based client for Chinese/Hungarian dictionary',
      long_description=longdesc,
      author='Janos Litkei',
      author_email='janos.litkei@gmail.com',
      url='https://github.com/jnsltk/szotar_net/',
      packages=['szotar_net'],
      scripts=['bin/szotar_net'],
      data_files=[('etc/szotar_net/', ['etc/szotar_net/config.ini'])],
      license='GPLv3',
      install_requires=[
          'pypinyin',
          'termcolor',
          'chinese_converter',
          'dragonmapper',
          'requests',
          'beautifulsoup4'
      ],
      python_requires='>=3',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: Education',
          'Intended Audience :: End Users/Desktop',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Natural Language :: English',
          'Natural Language :: Hungarian',
          'Natural Language :: Chinese',
          'Operating System :: POSIX',
          'Programming Language :: Python :: 3',
          'Topic :: Education',
          'Topic :: Text Processing :: Linguistic',
      ]
      )
