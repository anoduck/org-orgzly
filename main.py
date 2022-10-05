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
import datetime
from datetime import date
import configobj
from configobj import ConfigObj
import validate
from validate import Validator
# from configobj.validate import Validator
import argparse
import re
import pathlib
import os
import sys

# --------------------------------------------------------
# Variables
# --------------------------------------------------------
sys.path.append(pathlib.posixpath.expanduser("~/.local/lib/python3.9"))

HOME = os.path.expanduser('~')
XDG_CONFIG_HOME = os.getenv('XDG_CONFIG_HOME', os.path.join(HOME, '.config'))
CONFIG_FILE = os.path.join(XDG_CONFIG_HOME, 'org-orgzly', 'config.ini')
CONFIGSPEC = os.path.join(XDG_CONFIG_HOME, 'org-orgzly', 'configspec.ini')
ORG_HOME = os.path.join(HOME, 'org')
ORGZLY_HOME = os.path.join(HOME, 'orgzly')

# -----------------------------------------------------------------------
# Config File Spec
# -----------------------------------------------------------------------
cfg = """
org_files = list(min=1, max=15, default=list('~/org/todo.org', '~/org/inbox.org'))
orgzly_files = list(min=1, max=10, default=list('~/orgzly/todo.org',))
org_inbox = string(default='~/org/inbox.org')
orgzly_inbox = string(default='~/orgzly/inbox.org')
days = integer(min=1, max=360, default=7)
sync = boolean(default=False)
"""


# ---------------------------------------------------------
# Date Functions
# ---------------------------------------------------------

def date_test(entry):
    ndate = ""
    if bool(entry.deadline):
        ndate = str(entry.deadline)
    elif bool(entry.scheduled) and not bool(entry.deadline):
        ndate = str(entry.scheduled)
    return ndate

def extract_date(ndate):
    t = re.findall(r'\d+', ndate)
    rd = list(map(int, t))
    bdate = str(rd[0]) + '-' + str(rd[1]) + '-' + str(rd[2])
    return str(bdate)

    # An year is a leap year if it is a multiple of 4,
    # multiple of 400 and not a multiple of 100.
    # return int(years / 4) - int(years / 100) + int(years / 400)

def get_future(tdate, days):
    y, m, d = [int(x) for x in str(tdate).split('-')]
    d = d + int(days)
    monthDays = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if y%4==0 or y%400==0 and not y%100==0:
        monthDays[1]=29
    if d > monthDays[m] and m < 12:
        m = m + 1
        d = d - monthDays[m]
    elif d > monthDays[m] and m >= 12:
        m = m - 12
        y = y + 1
        d = d - monthDays[m]
    print(d)
    future_date = datetime.date(y, m, d)
    return future_date

# ----------------------------------------------------------
# Sync Back
# TODO Rewrite to sync from orgzly FILES to org inbox
# ----------------------------------------------------------
def sync_back(org_files, orgzly_files, org_inbox):
    to_sync = []
    for k in orgzly_files:
        f1 = orgparse.load(os.path.expanduser(org_inbox))
        f2 = orgparse.load(os.path.expanduser(k))
        ent1 = list(f1.env.nodes)
        ent2 = list(f2.env.nodes)
        dr = list(range(0, len(f2.env.nodes)))
        for q in dr:
            for x in ent2[q]:
                if x not in ent1:
                    to_sync.append(x)
    for n in to_sync:
        w = open(os.path.expanduser(org_inbox), "a", encoding="utf-8", newline="\n")
        w.writelines(str(n))
        w.write("\n")
        w.close()
        print("Added new entries to org file.")
    print("New entries added to inbox")

# ---------------------------------------------------------------------
# The main function
# ---------------------------------------------------------------------
def gen_file(org_files, orgzly_inbox, days):
    to_write = []
    for a in org_files:
        org_file = a
        file = orgparse.load(os.path.expanduser(org_file))
        entries = list(file.children)
        ent_num = len(entries)
        print("Number of entries is: " + str(ent_num))
        dr = list(range(0, ent_num))
        for y in dr:
            print("Selected: " + str(y))
            try:
                entry = file.children[y]
                if bool(entry.todo):
                    print("It has a todo")
                    ndate = date_test(entry)
                    print("Meets Date Requirements!")
                    newdate = extract_date(ndate) # < ---- Change this to orgdate and use context to extract what is needed.
                    print("Deadline date is" + str(newdate))
                    tdate = date.today()
                    y1, m1, d1 = [int(x) for x in newdate.split('-')]
                    date_org = datetime.date(y1, m1, d1)
                    y2, m2, d2 = [int(x) for x in str(tdate).split('-')]
                    date_today = datetime.date(y2, m2, d2)
                    print("Generating future_date")
                    future_date = get_future(tdate, days)
                    print("Future date is now Generated!")
                    if date_today >= date_org and future_date >= date_org:
                        print("Entry meets all requirements")
                        if entry not in to_write:
                            to_write.append(entry)
                            print("Entry added to list")
                    else:
                        if future_date <= date_org:
                            print("Dates do not fall within acceptable parameters. Due to: " + str(future_date) + " is less than " + str(date_org))
                        elif future_date >= date_org:
                            print("Dates do not meet parameters for some unknown reason or due to: " + str(date_today))
                        else:
                            print("There appears to be something wrong with: " + str(date_org))
            except IndexError:
                print("none found")
        print(orgzly_inbox[0])
        inbox = os.path.expanduser(orgzly_inbox[0])
        for x in to_write:
            w = open(inbox, "a", encoding="utf-8", newline="\n")
            w.writelines(str(entry))
            w.write("\n")
            w.close()
            print("Entry added to file")
                    
            
# -------------------------------------------------------------------------------------------------------------------
# Define Args
# -------------------------------------------------------------------------------------------------------------------
def get_parser():
    parser = argparse.ArgumentParser(
        description='Filters org entries and prepares them for sync with orgzly',
        epilog='This would be nice if it were something meaningful')

    parser.add_argument('-i', '--org_files', dest='org-files', action='append', help='an org file to parse for entries')
    parser.add_argument('-o', '--orgzly_files', dest='orgzly_files', action='append', help='orgzly file to push entries to')
    parser.add_argument('-n', '--org_inbox', dest='org_inbox', action='store', help='The org file you desire to push entries from orgzly to')
    parser.add_argument('-p', '--orgzly_inbox', dest='orgzly_inbox', action='store', help='The orgzly file you desire to push entries from orgzly to')
    parser.add_argument('-d', '--days', dest='days', metavar='Days', const=int, action='store_const', help='Number of days you want parsed for orgzly')
    parser.add_argument('-s', '--sync', action='store_false', help='Enables pulling entries from orgzly to org')
    return parser
                
# --------------------------------------------------------------------------------------------------------------------
# The startup command
# https://pyquestions.com/lists-in-configparser
# --------------------------------------------------------------------------------------------------------------------
def main(**args):
    parser = get_parser()
    args = parser.parse_args()
    # Set filename
    filename = None
    if filename is None:
        filename = CONFIG_FILE
    # Initiate config obj and spec
    spec = cfg.split("\n")
    config = ConfigObj(filename, configspec=spec)
    if os.path.isfile(filename):
        configspec = ConfigObj(CONFIGSPEC, encoding='UTF8', list_values=False)
        config = ConfigObj(filename, configspec=configspec)
    else:
        config.filename = filename
        validator = validate.Validator()
        config.validate(validator, copy=True)
        config.write()
    # add a default
    config.setdefault('sync', default=False)
    # Parse config file
    org_files = config['org_files']
    orgzly_files = config['orgzly_files']
    org_inbox = config['org_inbox']
    orgzly_inbox = config['orgzly_inbox']
    days = config['days']
    sync = config['sync']
    # Run Functions
    gen_file(org_files, orgzly_files, days)
    if sync == True:
        sync_back(org_files, orgzly_files, org_inbox)
        print("Sync Done.")

if __name__ == '__main__':
    main()
