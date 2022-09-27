#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2022  anoduck

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# ---------------------------------------------------------------------------------
# Dedicated to karlicoss
# ---------------------------------------------------------------------------------
# Nothing in this project could have been accomplished without the library written
# by karlicoss orgparse, and for the contribution and diligent effort to upkeep a
# viable org parser for python, this project is dedicated to.
# ---------------------------------------------------------------------------------
# https://pypi.org/project/orgparse/
# https://github.com/karlicoss/orgparse
# https://orgparse.readthedocs.io/en/latest/
# ---------------------------------------------------------------------------------

# --------------------------------------------------------
# Imports
# --------------------------------------------------------
import orgparse
from orgparse import *
from datetime import date
import re
import pathlib
import sys

# --------------------------------------------------------
# Variables
# --------------------------------------------------------
sys.path.append(pathlib.posixpath.expanduser("~/.local/lib/python3.9"))
org_file = pathlib.posixpath.expanduser("~/org/TODO.org")
orgzly_dir = pathlib.posixpath.expanduser("~/orgzly")
orgzly_file = orgzly_dir + "/" + "today.org"
dones = ['done', 'canceled']


# ---------------------------------------------------------
# The Beans
# ---------------------------------------------------------

def write_file(node):
    orgparse.load(org_file).env.nodes
    env = orgparse.OrgEnv()
    dk = env.done_keys
    if not bool(dk):
        w = open(orgzly_file, "a", encoding="utf-8", newline="\n")  # noqa: E501
        w.writelines(str(node))
        w.write("\n")
        w.close()

def extract_date(ndate):
    t = re.findall(r'\d+', ndate)
    rd = list(map(int, t))
    bdate = str(rd[0]) + '-' + str(rd[1]) + '-' + str(rd[2])
    return str(bdate)

def date_test(node):
    ndate = ""
    if bool(node.deadline):
        ndate = str(node.deadline)
    elif bool(node.scheduled) and not bool(node.deadline):
        ndate = str(node.scheduled)
    return ndate

def gen_file(org_file):
    dr = range(2, 200)
    for y in dr:
        if y > 2:
            try:
                file = orgparse.load(org_file)
                node = file.children[int(y)]
                if bool(node.has_date):
                    ndate = date_test(node)
                    newdate = extract_date(ndate)
                    print(newdate)
                    tdate = date.today()
                    y1, m1, d1 = [int(x) for x in newdate.split('-')]
                    date_org = date(y1, m1, d1)
                    y2, m2, d2 = [int(x) for x in str(tdate).split('-')]
                    date_today = date(y2, m2, d2)
                    if date_today >= date_org:
                        write_file(node)
            except IndexError:
                print("Index Error encountered")

if __name__ == '__main__':
    gen_file(org_file)
