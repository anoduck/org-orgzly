#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name='org-orgzly',
    version='0.0.1b3a',
    py_modules=['org-orgzly'],
    install_requires=[
        'orgparse',
        'configobj',
        'validate',
        'dropbox',
    ],
    entry_points={
        'console_scripts': [
            'org-orgzly = org-orgzly:cli',
        ],
    },
)
