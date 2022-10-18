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
# Dedicated to karlicoss --> Who seems like a really cool person.
# ---------------------------------------------------------------------------------
# Nothing in this project could have been accomplished without the library
# written by karlicoss orgparse, and for the contribution and diligent effort
# to upkeep a viable org parser for python, this project is dedicated to.
# ---------------------------------------------------------------------------------
# https://pypi.org/project/orgparse/
# https://github.com/karlicoss/orgparse
# https://orgparse.readthedocs.io/en/latest/
# ---------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------

# --------------------------------------------------------
# Imports
# --------------------------------------------------------
from hashlib import md5
import orgparse
import datetime
from datetime import date
import argparse
from configobj import ConfigObj
import validate
import dropbox
from dropbox import DropboxOAuth2FlowNoRedirect, files, exceptions
import re
import os
import sys
import time

# --------------------------------------------------------
# Variables
# --------------------------------------------------------
sys.path.append(os.path.expanduser("~/.local/lib/python3.9"))

HOME = os.path.expanduser('~')
XDG_CONFIG_HOME = os.getenv('XDG_CONFIG_DIR', os.path.join(HOME, '.config'))
CONFIG_FILE = os.path.join(XDG_CONFIG_HOME, 'org-orgzly', 'config.ini')
DBX_CONFIG_FILE = os.path.join(XDG_CONFIG_HOME, 'org-orgzly', '.dbx.ini')
CONFIGSPEC = os.path.join(XDG_CONFIG_HOME, 'org-orgzly', 'configspec.ini')
ORG_HOME = os.path.join(HOME, 'org')
ORGZLY_HOME = os.path.join(HOME, 'orgzly')
CWD = os.path.curdir
# -----------------------------------------------------------------------
# Versioning
# -----------------------------------------------------------------------
VERSION = '0.0.3'
# -----------------------------------------------------------------------
# Config File Spec
# -----------------------------------------------------------------------
cfg = """
app_key = string(default='Replace with your dropbox app key')
app_secret = string(default='Replace with your dropbox app secret')
dropbox_folder = string(default='orgzly')
orgzly_folder = string(default='~/orgzly')
org_files = list(default=list('~/org/todo.org', '~/org/inbox.org'))
orgzly_files = list(default=list('~/orgzly/todo.org', '~/orgzly/inbox.org'))
org_inbox = string(default='~/org/inbox.org')
orgzly_inbox = string(default='~/orgzly/inbox.org')
days = integer(default=7)
todos = list(default=list('TODO', 'LATERS', 'HOLD', 'OPEN'))
dones = list(default=list('DONE', 'CLOSED', 'CANCELED'))
"""

dbx_cfg = """refresh_token = string(default=REFRESH_TOKEN)"""
# ---------------------------------------------------------
# Date Functions
# ---------------------------------------------------------

def org_date(entry):
    ndate = ""
    if bool(entry.deadline):
        ndate = str(entry.deadline)
    elif bool(entry.scheduled) and not bool(entry.deadline):
        ndate = str(entry.scheduled)
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
    if y % 4 == 0 or y % 400 == 0 and not y % 100 == 0:
        monthDays[1] = 29
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

# ---------------------------------------------------------------------
# Dedupe
# ---------------------------------------------------------------------
def get_uniq_entries(test, control):
    tfile = orgparse.load(os.path.expanduser(test))
    cfile = orgparse.load(os.path.expanduser(control))
    uniq = []
    for t in tfile.children:
        test_dict = {}
        if t.todo is not None:
            test_enc = str(t).encode()
            test_hash = md5(test_enc).hexdigest()
            if test_hash not in list(test_dict.keys()):
                test_dict.setdefault(test_hash, t)
    for c in cfile.children:
        if c.todo is not None:
            con_list = []
            c_enc = str(c).encode()
            c_hash = md5(c_enc).hexdigest()
            if c_hash not in con_list:
                con_list.append(c_hash)
    for m in list(test_dict.keys()):
        if m not in con_list:
            uniq.append(test_dict[m])
    return uniq

# ---------------------------------------------------------------------
# The main function
# ---------------------------------------------------------------------
def gen_file(env, org_files, orgzly_inbox, days):
    for orgfile in org_files:
        to_write = []
        to_write.clear
        file = orgparse.load(os.path.expanduser(orgfile))
        add_file_keys = file.env.add_todo_keys
        add_file_keys(todos=env.todo_keys, dones=env.done_keys)
        dr = list(range(0, len(file.children)))
        for y in dr:
            entry = file.children[y]
            if entry.todo is not None:
                ndate = ""
                if entry.deadline:
                    ndate = str(entry.deadline)
                elif entry.scheduled and not entry.deadline:
                    ndate = str(entry.scheduled)
                else:
                    ndate = None
                if ndate is not None:
                    t = re.findall(r'\d+', ndate)
                    rd = list(map(int, t))
                    newdate = str(rd[0]) + '-' + str(rd[1]) + '-' + str(rd[2])
                    tdate = date.today()
                    y1, m1, d1 = [int(x) for x in newdate.split('-')]
                    date_org = datetime.date(y1, m1, d1)
                    y2, m2, d2 = [int(x) for x in str(tdate).split('-')]
                    date_today = datetime.date(y2, m2, d2)
                    future_date = get_future(tdate, days)
                    if date_today >= date_org and future_date >= date_org:
                        if entry not in to_write:
                            to_write.append(entry)
                    else:
                        if future_date <= date_org:
                            print("Dates do not fall within parameters. "
                                  "Due to: " + str(future_date)
                                  + "is less than " + str(date_org))
                        elif future_date >= date_org:
                            print("Dates do not meet parameters for some "
                                  " unknown reason or due to: "
                                  + str(date_today))
                        else:
                            print("There appears to be something wrong with: "
                                  + str(date_org))
        inbox_path = os.path.expanduser(orgzly_inbox)
        for x in to_write:
            w = open(inbox_path, "a", encoding="utf-8", newline="\n")
            w.writelines(str(x))
            w.write("\n")
            w.close()

# ----------------------------------------------------------
# Sync Back
# ----------------------------------------------------------
def sync_back(orgzly_files, org_inbox):
    node_list = []
    for e in orgzly_files:
        uniq = get_uniq_entries(e, org_inbox)
        node_list.extend(uniq)
    for o in node_list:
        hash_dict = {}
        if o.todo is not None:
            o_enc = str(o).encode()
            o_hash = md5(o_enc).hexdigest()
            if o_hash not in list(hash_dict.keys()):
                hash_dict.setdefault(o_hash, o)
    for n in list(hash_dict.values()):
        w = open(os.path.expanduser(org_inbox),
                 "a", encoding="utf-8", newline="\n")
        w.writelines(str(n))
        w.write("\n")
        w.close()
    print("New entries added to inbox")

# -------------------------------------------------------------------------------------------------------------------
# Dropbox's setup:
# Which can be seen as a way to discourage / mitigate api abuse.
# -------------------------------------------------------------------------------------------------------------------
    """Dropbox Variables Defined:

        dbx = dropbox Instance
        folder = Both name of the local folder and name of the remote folder to sync betwix, no path. eg: "Dropbox"
        fullname = fullpath of the file. ( fullpath + name + extension) eg: "/home/user/Dropbox/art.txt"
        name = Solely the name and extension of the file (name + extension) eg: "art.txt"

    """
# --------------------------------------------------------------------------------------------------------------------
# https://github.com/dropbox/dropbox-sdk-python/blob/master/example/updown.py
# -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

# Dropbox upload
def dropbox_upload(app_key, app_secret, fullname, folder, name, overwrite=True):
    """Upload a file.
    Return the request response, or None in case of error.
    """
    config_dbx = ConfigObj(DBX_CONFIG_FILE)
    REFRESH_TOKEN = config_dbx['dropbox_token']
    with dropbox.Dropbox(
            oauth2_refresh_token=str(REFRESH_TOKEN), app_key=app_key,
            app_secret=app_secret) as dbx:
        path = '/%s/%s' % (folder, name)
        while '//' in path:
            path = path.replace('//', '/')
        mode = (dropbox.files.WriteMode.overwrite
                if overwrite
                else dropbox.files.WriteMode.add)
        mtime = os.path.getmtime(fullname)
        client_modified = datetime.datetime(*time.gmtime(mtime)[:6])
        with open(fullname, 'rb') as f:
            data = f.read()
        try:
            res = dbx.files_upload(
                data, path, mode, client_modified=client_modified, mute=True)
        except exceptions.ApiError as err:
            print('*** API error', err)
            return None
        return res

# Dropbox Download
def dropbox_download(app_key, app_secret, folder, name):
    """Download a file.
    Return the bytes of the file, or None if it doesn't exist.
    """
    config_dbx = ConfigObj(DBX_CONFIG_FILE)
    REFRESH_TOKEN = config_dbx['dropbox_token']
    with dropbox.Dropbox(oauth2_refresh_token=REFRESH_TOKEN,
                         app_key=app_key, app_secret=app_secret) as dbx:
        path = '/%s/%s' % (folder, name)
        while '//' in path:
            path = path.replace('//', '/')
        try:
            md, res = dbx.files_download(path)
        except exceptions.HttpError as err:
            print('*** HTTP error', err)
            return None
        data = res.content
        return data

# -------------------------------------------------------------------------------------
# Write refresh_token
# -------------------------------------------------------------------------------------
def write_refresh(REFRESH_TOKEN):
    filename = DBX_CONFIG_FILE
    if not os.path.isfile(filename):
        config = ConfigObj()
        config['dropbox_token'] = REFRESH_TOKEN
        config.filename = filename
        config.write()
    else:
        config = ConfigObj(filename, configspec=dbx_cfg)
        config['dropbox_token'] = REFRESH_TOKEN
        config.write()
    print('Dropbox refresh token acuired and saved')

# -------------------------------------------------------------------------------------
# Get the authentication token:
# -------------------------------------------------------------------------------------
def get_access_token(key, sec):
    auth_flow = DropboxOAuth2FlowNoRedirect(key, sec,
                                            token_access_type='offline')
    authorize_url = auth_flow.start
    print("1. Go to: " + str(authorize_url()))
    print("2. Click \"Allow\" (you might have to log in first).")
    print("3. Copy the authorization code.")
    auth_code = input("Enter the authorization code here: ").strip()

    try:
        oauth_result = auth_flow.finish(auth_code)
    except Exception as e:
        print('Error: %s' % (e,))
        exit(1)

    write_refresh(oauth_result.refresh_token)

# -------------------------------------------------------------------------------------
# Make sure all variables satisfy the code "Borrowed" from Dropbox.
def dropbox_put(app_key, app_secret, dropbox_folder, orgzly_folder):
    upl = []
    folder = dropbox_folder
    orgzly_path = os.path.expanduser(orgzly_folder)
    dirlist = os.listdir(orgzly_path)
    for j in dirlist:
        if j not in upl:
            upl.append(j)
        for k in upl:
            real_file = str(orgzly_path) + '/' + str(k)
            fullname = os.path.realpath(real_file)
            name = os.path.basename(real_file)
            dropbox_upload(app_key, app_secret, fullname, folder, name)

def dropbox_get(app_key, app_secret, dropbox_folder, orgzly_folder):
    dwl = []
    folder = dropbox_folder
    dirlist = os.listdir(os.path.expanduser(orgzly_folder))
    for j in dirlist:
        if j not in dwl:
            dwl.append(j)
        for k in dwl:
            real_file = os.path.join(orgzly_folder, k)
            fullname = os.path.realpath(real_file)
            name = os.path.basename(real_file)
            data = dropbox_download(app_key, app_secret, folder, name)
            stuff = str(data).rsplit("\\n")
            sr = list(range(0, len(stuff)))
            for h in sr:
                line = stuff[h]
                with open(fullname, "a", encoding="utf-8", newline="\n") as w:
                    w.write(line)
                    w.write("\n")
                    w.close()
    print('Get Complete')

# --------------------------------------------------------------------------------------------------------------------
# The startup command
# --------------------------------------------------------------------------------------------------------------------
def main():
    filename = CONFIG_FILE
    # Setup of ConfigObj
    config = ConfigObj()
    spec = cfg.split("\n")
    if not os.path.isfile(filename):
        config = ConfigObj(filename, configspec=spec)
        config.filename = filename
        validator = validate.Validator()
        config.validate(validator, copy=True)
        config.write()
        print("Configuration file written to "
              "$XDG_CONFIG_HOME/orgzly/config.ini")
        exit(0)
    else:
        config = ConfigObj(filename, configspec=spec)

    # ArgParse Setup
    p = argparse.ArgumentParser(
            prog='org-orgzly',
            usage='%(prog)s.py [ --push | --pull | --put | --get ] '
            'or --dropbox_token',
            description='Makes managing your org schedule '
            'easier for mobile, by reducing the amount of entries '
            'you take with you.',
            epilog='Dedicated to karlicoss, who made it possible.',
            conflict_handler='resolve')

    p.add_argument('--version', action='version',
                   version='org-orgzly ' + VERSION)
    p.add_argument('--dropbox_token', action='store_true',
                   help='Fetch initial Access Token')
    p.add_argument('--push', action='store_true',
                   help='Parse files and push them to orgzly')
    p.add_argument('--pull', action='store_true',
                   help='Pull new entries from orgzly to org inbox')
    p.add_argument('--put', action='store_true',
                   help='Upload orgzly files to dropbox')
    p.add_argument('--get', action='store_true',
                   help='Download orgzly files from dropbox')

    args = p.parse_args()

    env = orgparse.node.OrgEnv()
    addkeys = env.add_todo_keys
    addkeys(todos=config['todos'], dones=config['dones'])

    # Run the gambit of args vs config
    if args.push:
        org_files = config['org_files']
        orgzly_inbox = config['orgzly_inbox']
        days = config['days']
        gen_file(env, org_files, orgzly_inbox, days)
    if args.pull:
        orgzly_files = config['orgzly_files']
        org_inbox = config['org_inbox']
        sync_back(orgzly_files, org_inbox)
    if args.put:
        dropbox_put(config['app_key'], config['app_secret'],
                    config['dropbox_folder'], config['orgzly_folder'])
    if args.get:
        dropbox_get(config['app_key'], config['app_secret'],
                    config['dropbox_folder'], config['orgzly_files'])
    if args.dropbox_token:
        get_access_token(config['app_key'], config['app_secret'])

if __name__ == '__main__':
    main()
