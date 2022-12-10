#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name='org-orgzly',
    version='0.0.17',
    py_modules=['org-orgzly'],
    install_requires=[
        'orgparse',
        'art',
        'configobj',
        'dropbox',
    ],
    entry_points={
        'console_scripts': [
            'org-orgzly = org-orgzly:cli',
        ],
    },
)
