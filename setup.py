#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name='org-orgzly',
    version='0.0.1b',
    py_modules=['org-orgzly'],
    install_requires=[
        'click',
        'orgparse',
        'configobj',
        'validate',
    ],
    entry_points={
        'console_scripts': [
            'org-orgzly = org-orgzly:cli',
        ],
    },
)
