#!/usr/bin/env python

from setuptools import setup
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.txt'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='mailusage',
    version='0.1.dev1',
    description='Calculate IMAP quota usage by adding message sizes.',
    long_description = long_description,

    # no homepage
    # url='',

    author='Jacob Morzinski',
    author_email='jmorzins@mit.edu',

    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: MIT License',
        'Topic :: Communications :: Email'
        'Environment :: Console',
        ],

    keywords='imap mail quota usage',

    #packages=['',],
    install_requires=['kerberos'],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'console_scripts': [
            'mailusage=mailusage:main',
            ],
        },

    )
