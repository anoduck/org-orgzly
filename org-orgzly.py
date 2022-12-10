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

import argparse
import datetime
import os
import re
import shutil
import sys
import time
from tempfile import TemporaryDirectory, mkdtemp

# --------------------------------------------------------
# Imports
# --------------------------------------------------------
import orgparse
from configobj import ConfigObj

sys.path.append(os.path.expanduser("~/.local/lib/python3.9"))
from datetime import date
import art
import dropbox
import validate
from dropbox import DropboxOAuth2FlowNoRedirect, exceptions
from orgparse import OrgEnv, load

# --------------------------------------------------------
# Variables
# --------------------------------------------------------

HOME = os.path.expanduser('~')
XDG_CONFIG_HOME = os.getenv('XDG_CONFIG_DIR', os.path.join(HOME, '.config'))
CONFIG_FILE = os.path.join(XDG_CONFIG_HOME, 'org-orgzly', 'config.ini')
DBX_CONFIG_FILE = os.path.join(XDG_CONFIG_HOME, 'org-orgzly', '.dbx.ini')
CONFIGSPEC = os.path.join(XDG_CONFIG_HOME, 'org-orgzly', 'configspec.ini')
CWD = os.path.curdir
PROG = os.path.basename(__file__)
# -----------------------------------------------------------------------
# Versioning
# -----------------------------------------------------------------------
VERSION = '0.0.17'
# -----------------------------------------------------------------------
# Config File Spec
# -----------------------------------------------------------------------
cfg = """
app_key = string(default='Replace with your dropbox app key')
app_secret = string(default='Replace with your dropbox app secret')
create_missing = boolean(default=True)
backup = boolean(default=True)
split_events = boolean(default=True)
dropbox_folder = string(default='orgzly')
resources_folder = string(default='~/orgzly/Resources')
org_files = list(default=list('~/org/todo.org'))
orgzly_files = list(default=list('~/orgzly/todo.org'))
org_inbox = string(default='~/org/inbox.org')
orgzly_inbox = string(default='~/orgzly/inbox.org')
org_events = string(default='~/org/events.org')
orgzly_events = string(default='~/orgzly/events.org')
days = integer(default=7)
todos = list(default=list('TODO', 'LATERS', 'HOLD', 'OPEN'))
dones = list(default=list('DONE', 'CLOSED', 'CANCELED'))
"""

dbx_cfg = """
refresh_token = string(default=REFRESH_TOKEN)
"""

# ---------------------------------------------------------
# for mkstemp
# ---------------------------------------------------------
mode = 0o666
flags = os.O_RDWR | os.O_CREAT
# ---------------------------------------------------------
# Date Functions
# ---------------------------------------------------------


def org_date(entry):
    ndate = ""
    if bool(entry.deadline):
        ndate = str(entry.deadline)
    elif bool(entry.scheduled) and not bool(entry.deadline):
        ndate = str(entry.scheduled)
    t_reg = re.findall(r'\d+', ndate)
    reg_d = list(map(int, t_reg))
    ddate = str(reg_d[0]) + '-' + str(reg_d[1]) + '-' + str(reg_d[2])
    bdate = str(ddate)
    return bdate

    # An year is a leap year if it is a multiple of 4,
    # multiple of 400 and not a multiple of 100.
    # return int(years / 4) - int(years / 100) + int(years / 400)


def get_future(tdate, days):
    y, m, d = [int(x) for x in str(tdate).split('-')]
    d = d + int(days)
    monthDays = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if y % 4 == 0 or y % 400 == 0 and not y % 100 == 0:
        monthDays[2] = 29
    if d > monthDays[m] and m < 12:
        m = m + 1
        d = d - monthDays[m]
    if d > monthDays[m] and m >= 12:
        m = m - 12
        y = y + 1
        d = d - monthDays[m]
    future_date = datetime.date(y, m, d)
    return future_date


# ---------------------------------------------------------------------
# Dedupe
# ---------------------------------------------------------------------
def dedupe_files(test, control):
    tfile = get_parser(os.path.expanduser(test))
    cfile = get_parser(os.path.expanduser(control))
    uniq = set()
    con_set = set()
    test_set = set()
    for t_node in tfile[1:]:
        if t_node.todo:
            if t_node not in test_set:
                test_set.add(t_node)
    for c_node in cfile[1:]:
        if c_node.todo:
            if c_node not in con_set:
                con_set.add(c_node)
    for m_node in test_set:
        if m_node not in con_set:
            uniq.add(m_node)
    return uniq


# ---------------------------------------------------------------------
# Process Entries
# ---------------------------------------------------------------------
def process_entries(orgfile, days):
    to_write = []
    event_list = []
    for node in orgfile[1:]:
        if node.todo:
            ndate = False
            if node.deadline:
                ndate = str(node.deadline)
            elif node.scheduled and not node.deadline:
                ndate = str(node.scheduled)
            else:
                pass
            if ndate:
                t_ndate = re.findall(r'\d+', ndate)
                r_d = list(map(int, t_ndate))
                newdate = str(r_d[0]) + '-' + str(r_d[1]) + '-' + str(r_d[2])
                tdate = date.today()
                y_1, m_1, d_1 = [int(x) for x in newdate.split('-')]
                date_org = datetime.date(y_1, m_1, d_1)
                y_2, m_2, d_2 = [int(x) for x in str(tdate).split('-')]
                date_today = datetime.date(y_2, m_2, d_2)
                future_date = get_future(tdate, days)
                if date_today >= date_org:
                    if future_date >= date_org:
                        if node not in to_write:
                            to_write.append(node)
                        else:
                            if future_date <= date_org:
                                print("Dates do not fall within parameters. "
                                      "Due to: " + str(future_date)
                                      + " is less than " + str(date_org))
                            elif future_date >= date_org:
                                print("Dates do not meet parameters for some "
                                      " unknown reason or due to: "
                                      + str(date_today))
                            else:
                                print("There appears to be something wrong: "
                                      + str(date_org))
        else:
            event_list.append(node)
    to_write = process_events(event_list, days)
    return to_write


# ----------------------------------------------------------------------
# Process events
# ----------------------------------------------------------------------
def process_events(event_list, days):
    write_set = set()
    for event in event_list:
        active_stamp = event.get_timestamps(active=True, inactive=False,
                                            range=True, point=True)
        if active_stamp:
            if not event.deadline and not event.scheduled:
                ndate = str(active_stamp)
            if ndate:
                t_ndate = re.findall(r'\d+', ndate)
                r_d = list(map(int, t_ndate))
                newdate = str(r_d[0]) + '-' + str(r_d[1]) + '-' + str(r_d[2])
                y_1, m_1, d_1 = [int(x) for x in newdate.split('-')]
                date_org = datetime.date(y_1, m_1, d_1)
                tdate = date.today()
                y_2, m_2, d_2 = [int(x) for x in str(tdate).split('-')]
                date_today = datetime.date(y_2, m_2, d_2)
                future_date = get_future(tdate, days)
                if date_today >= date_org:
                    if future_date >= date_org:
                        write_set.add(event)
    write_events = [*write_set]
    return write_events


# -----------------------------------------------------------------------
# Parse Events
# -----------------------------------------------------------------------
def parse_events(org_events, orgzly_events, days):
    or_epath = os.path.expanduser(org_events)
    oz_epath = os.path.expanduser(orgzly_events)
    or_ep = get_parser(or_epath)
    oz_ep = get_parser(oz_epath)
    or_ns = set(or_ep[1:])
    oz_ns = set(oz_ep[1:])
    event_list = [*set(or_ns | oz_ns)]
    if days is not None:
        write_events = process_events(event_list, days)
    else:
        write_events = event_list
    write_true = funky_chicken(oz_epath, write_events)
    if write_true:
        return True

# ---------------------------------------------------------------------
# Funky Chicken
# ---------------------------------------------------------------------
def funky_chicken(target_path, node_list):
    file_title = os.path.basename(target_path).strip('.org')
    title_label = ' '.join(['#+TITLE: ', file_title])
    date_string = date.today().strftime('%Y-%m-%d %A')
    date_label = ' '.join(['#+DATE: ', date_string])
    with open(target_path, "w+",
              encoding="utf-8", newline="\n") as w_funky:
        w_funky.seek(0)
        w_funky.write(title_label)
        w_funky.write(date_label)
        w_funky.write('# -------------------------------------')
        # w_funky.write("\n")
        for uniq_node in node_list:
            w_funky.write(str(uniq_node))
            w_funky.write("\n")
        w_funky.truncate()
        w_funky.close()
    return True


# ---------------------------------------------------------------------
# Write Event
# ---------------------------------------------------------------------
def write_event(node, event_file):
    efile_path = os.path.expanduser(event_file)
    with open(efile_path, "a") as w_ef:
        w_ef.write(node)
        w_ef.write('\n')
        w_ef.close()
    return True


# ---------------------------------------------------------------------
# The main function
# ---------------------------------------------------------------------
def gen_file(env, org_files, orgzly_inbox, days, split_events, org_events,
             orgzly_events, resources_folder):
    prime_set = set()
    uniq_set = set()
    if split_events:
        p_events = parse_events(org_events, orgzly_events, days)
        if p_events:
            print('event files processed')
    for orgfile in org_files:
        print('Processing: ' + orgfile)
        file = get_parser(os.path.expanduser(orgfile))
        all_keys = file.env.all_todo_keys
        to_write = process_entries(file, days)
        prime_set = set(to_write)
    for node in prime_set:
        timestamp = node.get_timestamps
        node_id = node.get_property('ID')
        if node.todo:
            if node.todo not in all_keys:
                evented = write_event(node, orgzly_events)
                if evented:
                    print("Event node discovered and written to event file")
            if node.todo in all_keys:
                if node_id:
                    if node_id not in {x.get_property('ID') for x in uniq_set}:
                        uniq_set.add(node)
                else:
                    if node.heading not in {x.heading for x in uniq_set}:
                        uniq_set.add(node)
        elif not node.todo and timestamp(active=True):
            evented = write_event(node, orgzly_events)
            if evented:
                print("Event node discovered and written to event file")
        else:
            org_path = os.path.expanduser(org_files[0])
            dir_path = os.path.dirname(org_path)
            handle_zombies(node, dir_path)
    print("Duplicates removed using node id and node heading.")
    uniq_list = [*uniq_set]
    # uniq_list.sort(key=lambda x: x.priority)
    inbox_path = os.path.expanduser(orgzly_inbox)
    node_write = funky_chicken(inbox_path, uniq_list)
    res_dict = get_res(resources_folder, org_files, [orgzly_events])
    or_res = res_dict.get('or_res')
    for res in os.listdir(or_res):
        res_name = os.path.basename(res)
        oz_dir = res_dict.get('oz_dir')
        oz_resfile = os.path.join(oz_dir, res_name)
        if not os.path.exists(oz_resfile):
            shutil.copy2(res, oz_resfile)
    if node_write:
        prime_set.clear()
        print('Successfully pushed org nodes to orgzly!')


# ----------------------------------------------------------
# Sync Back
# ----------------------------------------------------------
def sync_back(orgzly_files, org_inbox, org_files, split_events, org_events,
              orgzly_events, resources_folder):
    oznode_set = set()
    ornode_set = set()
    oziq_set = set()
    if split_events:
        days = None
        p_events = parse_events(org_events, orgzly_events, days)
        if p_events:
            print('event files processed')
    for org_file in org_files:
        or_path = os.path.expanduser(org_file)
        or_parse = get_parser(or_path)
        ornode_set = ornode_set.union(set(or_parse[1:]))
    for orgzly_file in orgzly_files:
        oz_path = os.path.expanduser(orgzly_file)
        oz_parse = get_parser(oz_path)
        oznode_set = oznode_set.union(set(oz_parse[1:]))
    for oznode in oznode_set:
        timestamp = oznode.get_timestamps
        oznode_id = oznode.get_property('ID')
        all_keys = or_parse.env.all_todo_keys
        if oznode.todo:
            if oznode.todo not in all_keys:
                evented = write_event(oznode, org_events)
                if evented:
                    print("Event node discovered and written to event file")
            if oznode.todo in all_keys:
                if oznode_id:
                    if oznode_id not in {x.get_property('ID') for x in
                                         ornode_set}:
                        oziq_set.add(oznode)
                else:
                    if oznode.heading not in {x.heading for x in ornode_set}:
                        oziq_set.add(oznode)
        elif not oznode.todo and timestamp(active=True):
            evented = write_event(oznode, org_events)
            if evented:
                print("Event node discovered and written to event file")
        else:
            oz_path = os.path.expanduser(orgzly_files[0])
            oz_dir = os.path.dirname(oz_path)
            handle_zombies(oznode, oz_dir)
    oziq_list = [*oziq_set]
    # oziq_list.sort(key=lambda x: x.priority)
    pulled = False
    for oziq_node in oziq_list:
        with open(os.path.expanduser(org_inbox), "a", encoding="utf-8",
                  newline="\n") as w_file:
            w_file.writelines(str(oziq_node))
            w_file.write("\n")
            w_file.close()
            pulled = True
    if pulled:
        print("New entries added to inbox")
    res_dict = get_res(resources_folder, org_files, orgzly_files)
    oz_res = res_dict.get('oz_res')
    for res in os.listdir(oz_res):
        res_name = os.path.basename(res)
        res_folder = res_dict.get('resources')
        or_dir = res_dict.get('or_dir')
        oz_dir = res_dict.get('oz_dir')
        or_resfile = os.path.join(or_dir, res_folder, res_name)
        oz_resfile = os.path.join(oz_dir, res_folder, res_name)
        if not os.path.exists(or_resfile):
            shutil.copy2(oz_resfile, or_resfile)
    print("Processing entries back to org: Done")


# ----------------------------------------------------------------
# Dropbox's setup:
# Which can be seen as a way to discourage / mitigate api abuse.
# ----------------------------------------------------------------
    """
        Dropbox Variables Defined:

        dbx = dropbox Instance
        folder = Both name of local folder and name of remote folder
        fullname = fullpath of the file. ( fullpath + name + extension)
        name = Solely the name and extension of the file (name + extension)

    """
# ----------------------------------------------------------------------------
# https://github.com/dropbox/dropbox-sdk-python/blob/master/example/updown.py
# -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --


def dbx_list(response):
    rv = {}
    for entry in response.entries:
        rv[entry.name] = entry
    return rv


def gen_list(app_key, app_secret, dropbox_folder):
    config_dbx = ConfigObj(DBX_CONFIG_FILE)
    REFRESH_TOKEN = config_dbx['dropbox_token']
    r_v = dict()
    with dropbox.Dropbox(
            oauth2_refresh_token=str(REFRESH_TOKEN), app_key=app_key,
            app_secret=app_secret) as dbx:
        dbx_folder = os.path.join('/', dropbox_folder)
        response = dbx.files_list_folder(dbx_folder,
                                         include_mounted_folders=False)
        for entry in response.entries:
            r_v[entry.name] = entry
        resp_dir = r_v
    files_as_keys = resp_dir.keys()
    return files_as_keys


def gen_file_list(app_key, app_secret, dropbox_folder):
    of_list = []
    of_list.clear()
    files_as_keys = gen_list(app_key, app_secret, dropbox_folder)
    for key in files_as_keys:
        ofile = re.search(r'.\w+?\.org$', str(key))
    if ofile:
        oname_o = ofile.string.strip()
        if oname_o not in of_list:
            of_list.append(oname_o)
    return of_list


def list_orgzly(app_key, app_secret, dropbox_folder):
    dbx_file_list = gen_list(app_key, app_secret, dropbox_folder)
    folder = '/' + str(dropbox_folder)
    print('Files in dropbox folder ' + '"' + folder + '"' + ' are: ')
    for key in dbx_file_list:
        print('->' + key)
    print('-------------------')
    print(' ===> Done.')


# -----------------------------------------------------------------------
# Check Resource folder
# -----------------------------------------------------------------------
def dropbox_check_resources(app_key, app_secret, res_folder, dropbox_folder):
    config_dbx = ConfigObj(DBX_CONFIG_FILE)
    REFRESH_TOKEN = config_dbx['dropbox_token']
    with dropbox.Dropbox(oauth2_refresh_token=REFRESH_TOKEN, app_key=app_key,
                         app_secret=app_secret) as dbx:
        files_as_keys = gen_list(app_key, app_secret, dropbox_folder)
        create_folder = dbx.files_create_folder
        oz_path = os.path.dirname(res_folder)
        res_name = os.path.basename(res_folder)
        oz_name = os.path.basename(oz_path)
        dbx_folder = os.path.join('/', oz_name, res_name)
        if res_name not in files_as_keys:
            print('Creating Resource folder in Dropbox')
            create_folder(dbx_folder)
            if res_name in files_as_keys:
                print('Resource folder now exists')
                return True
        if res_name in files_as_keys:
            print('Resource folder already found in Dropbox')
            return True


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
    print('Dropbox refresh token acquired and saved')


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
    except Exception as e_t:
        print("f'Error: %s' % (e_t,)")
        sys.exit()
    write_refresh(oauth_result.refresh_token)


# --------------------------------------------------------------------------------
# Handle Dropbox Event files
# --------------------------------------------------------------------------------
def dbox_efiles(tmpdir, tmp2dir, orgzly_events, dbx_events):
    db_epath = os.path.join(tmpdir, dbx_events)
    oz_epath = os.path.expanduser(orgzly_events)
    db_ep = get_parser(db_epath)
    oz_ep = get_parser(oz_epath)
    db_ns = set(db_ep[1:])
    oz_ns = set(oz_ep[1:])
    master_elist = [*set(db_ns | oz_ns)]
    db2_path = os.path.join(tmp2dir, dbx_events)
    tots = funky_chicken(db2_path, master_elist)
    if tots:
        taters = dbx_events
    return taters


# --------------------------------------------------------------------------------
# Down to tmp
# --------------------------------------------------------------------------------
def down_to_tmp(app_key, app_secret, dropbox_folder, tmpdir):
    files_as_keys = gen_file_list(app_key, app_secret, dropbox_folder)
    for k_file in files_as_keys:
        k_path = os.path.expanduser(k_file)
        k_name = os.path.basename(k_path)
        tmp_path = os.path.join(tmpdir, k_name)
        dbx_path = os.path.join('/', dropbox_folder, k_name)
        config_dbx = ConfigObj(DBX_CONFIG_FILE)
        REFRESH_TOKEN = config_dbx['dropbox_token']
        with dropbox.Dropbox(oauth2_refresh_token=REFRESH_TOKEN,
                             app_key=app_key,
                             app_secret=app_secret) as dbx:
            dbx.files_download_to_file(download_path=tmp_path,
                                       path=dbx_path)
    print('Successfully Downloaded orgfiles to ' + tmpdir)
    file_list = os.listdir(tmpdir)
    return file_list


# ------------------------------------------------------------------------------
# Gen Load
# ------------------------------------------------------------------------------
def gen_load(t_file, tmpdir, orgzly_files):
    t_path = os.path.join(tmpdir, t_file)
    path = os.path.expanduser(orgzly_files[0])
    orgzly_fname = str(os.path.basename(path))
    orgzly_dirpath = str(os.path.realpath(path)).strip(orgzly_fname)
    orgzly_fpath = os.path.join(orgzly_dirpath, t_file)
    temp_load = get_parser(t_path)
    oz_load = get_parser(orgzly_fpath)
    return temp_load, oz_load


# -------------------------------------------------------------------------------------
# Dropbox Put
# -------------------------------------------------------------------------------------
# Make sure all variables satisfy the code "Borrowed" from Dropbox.
def dropbox_put(app_key, app_secret, dropbox_folder, orgzly_files,
                orgzly_events, resources_folder):
    config_dbx = ConfigObj(DBX_CONFIG_FILE)
    REFRESH_TOKEN = config_dbx['dropbox_token']
    dbx_mode = dropbox.files.WriteMode.overwrite
    with TemporaryDirectory(suffix='_dir', prefix='oroz_') as tmpdir:
        with TemporaryDirectory(suffix='_dir2', prefix='oroz_') as tmp2dir:
            file_list = down_to_tmp(app_key, app_secret, dropbox_folder,
                                    tmpdir)
            for t_file in file_list:
                if t_file == "events.org":
                    dbx_events = t_file
                    taters = dbox_efiles(tmpdir, tmp2dir, orgzly_events,
                                         dbx_events)
                    if taters is not None:
                        upt_file = taters
                else:
                    node_set = set()
                    node_set.clear()
                    temp_load, oz_load = gen_load(t_file, tmpdir, orgzly_files)
                    for node in oz_load[1:]:
                        if node not in temp_load[1:]:
                            node_set.add(node)
                    path_to_write = os.path.join(tmp2dir, t_file)
                    with open(path_to_write, 'w+', encoding='utf-8') as w_f:
                        for node in node_set:
                            w_f.write(str(node))
                            w_f.write('\n')
                    upt_file = t_file
                dbx_file_path = os.path.join('/', dropbox_folder, upt_file)
                path_to_write = os.path.join(tmp2dir, upt_file)
                mtime = os.path.getmtime(path_to_write)
                client_modified = datetime.datetime(*time.gmtime(mtime)[:6])
                with dropbox.Dropbox(oauth2_refresh_token=REFRESH_TOKEN,
                                     app_key=app_key,
                                     app_secret=app_secret) as dbx:
                    file_upload = dbx.files_upload
                    with open(path_to_write, 'rb') as f_u:
                        data = f_u.read()
                    try:
                        dbx.files_upload(data, dbx_file_path, dbx_mode,
                                         client_modified=client_modified,
                                         mute=True)
                    except exceptions.ApiError as err:
                        print('*** API error', err)
    res_folder = os.path.expanduser(resources_folder)
    dbx_folder = '/' + str(os.path.basename(res_folder))
    oz_path = os.path.dirname(res_folder)
    res_name = os.path.basename(res_folder)
    oz_name = os.path.basename(oz_path)
    dbx_folder = os.path.join('/', oz_name, res_name)
    to_res = dropbox_check_resources(app_key, app_secret, res_folder,
                                     dropbox_folder)
    if to_res:
        with dropbox.Dropbox(oauth2_refresh_token=REFRESH_TOKEN,
                             app_key=app_key, app_secret=app_secret) as dbx:
            file_upload = dbx.files_upload
            for res_file in os.listdir(res_folder):
                file_path = os.path.join(res_folder, res_file)
                dbx_path = os.path.join(dbx_folder, res_file)
                mtime = os.path.getmtime(file_path)
                client_modified = datetime.datetime(*time.gmtime(mtime)[:6])
                with open(file_path, 'rb') as f_file:
                    data = f_file.read()
                try:
                    file_upload(data, dbx_path, dbx_mode,
                                client_modified=client_modified, mute=True)
                except exceptions.ApiError as err:
                    print('*** API error', err)
                    return None
            print('Uploaded file from resources')
    print('Upload to Dropbox was successful!')


def write_to_orgzly(orgzly_files, t_file, node):
    ono_path = os.path.expanduser(orgzly_files[0])
    orgzly_fname = str(os.path.basename(ono_path))
    orgzly_dirpath = str(os.path.realpath(ono_path)).strip(orgzly_fname)
    path_to_write = os.path.join(orgzly_dirpath,
                                 os.path.basename(t_file))
    with open(path_to_write, 'w+', encoding='utf-8') as w_f:
        w_f.write(str(node))
        w_f.write('\n')
    return True


def dropbox_get(app_key, app_secret, dropbox_folder, orgzly_files,
                orgzly_events, resources_folder):
    with TemporaryDirectory(suffix='_dir', prefix='oroz_') as tmpdir:
        file_list = down_to_tmp(app_key, app_secret, dropbox_folder, tmpdir)
        ev_car = False
        for t_file in file_list:
            if t_file == 'events.org':
                db_path = os.path.join(tmpdir, t_file)
                oz_path = os.path.expanduser(orgzly_events)
                db_parse = get_parser(db_path)
                db_nodes = set(db_parse[1:])
                oz_parse = get_parser(oz_path)
                oz_nodes = set(oz_parse[1:])
                get_nodes = set(db_nodes | oz_nodes)
                events_list = [*(get_nodes)]
                for node in events_list:
                    ev_car = write_to_orgzly(orgzly_files, t_file, node)
            else:
                node_set = set()
                node_set.clear()
                temp_load, oz_load = gen_load(t_file, tmpdir, orgzly_files)
                for node in temp_load[1:]:
                    active_stamp = node.get_timestamps(active=True,
                                                       range=True, point=True)
                    if active_stamp:
                        heading = node.heading
                        if heading not in oz_load[1:]:
                            if heading not in node_set:
                                node_set.add(node)
                for node in node_set:
                    ev_car = write_to_orgzly(orgzly_files, t_file, node)
            if ev_car:
                print('Dropbox download of org files was successful')
        print('Downloading Resources folder directly')
        res_base = os.path.basename(resources_folder)
        res_dbox_folder = os.path.join(dropbox_folder, res_base)
        oz_path = os.path.expanduser(orgzly_files[0])
        oz_dir = os.path.dirname(oz_path)
        tmp_resources = os.path.join(tmpdir, oz_dir, res_base)
        tipy_tip = down_to_tmp(app_key, app_secret, res_dbox_folder,
                               tmp_resources)
        if tipy_tip:
            oz_path = os.path.expanduser(orgzly_files[0])
            oz_dir = os.path.dirname(oz_path)
            res_dir = os.path.join(oz_dir, res_base)
            ozdir_list = os.listdir(res_dir)
            new_files = set(tipy_tip) ^ set(ozdir_list)
            for r_file in new_files:
                rf_src = os.path.join(tmp_resources, r_file)
                rf_dest = os.path.join(res_dir, r_file)
                shutil.copy(rf_src, rf_dest)
    print('Dropbox download and processing: Done')


# --------------------------------------------------------------------------------
# Backup Files
# --------------------------------------------------------------------------------
def backup_files(org_files, orgzly_files, org_events, orgzly_events, days):
    flist = org_files + orgzly_files
    events_files = [org_events, orgzly_events]
    for e_file in events_files:
        if e_file not in events_files:
            flist.append(e_file)
    bdirname = os.path.dirname(os.path.expanduser(orgzly_files[0]))
    BACKUP_HOME = os.path.join(bdirname, '.backup')
    if not os.path.isdir(BACKUP_HOME):
        os.mkdir(BACKUP_HOME)
    dir_list = os.listdir(BACKUP_HOME)
    for dir_file in dir_list:
        dstring = str(dir_file).split('_', maxsplit=1)[0]
        y, m, d = [int(x) for x in dstring.split('-')]
        exp_date = date(y, m, d)
        expiration = exp_date.strftime('%Y-%m-%d')
        today = date.today()
        cur_date = today.strftime('%Y-%m-%d')
        if cur_date >= expiration:
            ffull_path = os.path.join(BACKUP_HOME, dir_file)
            os.remove(os.path.realpath(ffull_path))
            print('Old backup file removed: ' + dir_file)
    for flist_file in flist:
        userdef_path = os.path.expanduser(flist_file)
        f_split = os.path.split(userdef_path)
        f_dirname = os.path.basename(f_split[0])
        f_basename = os.path.basename(userdef_path)
        fdate = get_future(date.today(), days)
        back_name = str(fdate) + '_' + f_dirname + '_' + f_basename
        partial_path = os.path.join(BACKUP_HOME, back_name)
        back_fullpath = os.path.expanduser(partial_path)
        shutil.copy2(userdef_path, back_fullpath, follow_symlinks=False)
        if not os.path.isfile(back_fullpath):
            print('Error occurred in the creation of a backup file.')
    print('File backup successful!')


# --------------------------------------------------------------
# get resouces folder
# --------------------------------------------------------------
def get_res(resources_folder, org_files, orgzly_files):
    res_dict = {}
    resources_path = os.path.expanduser(resources_folder)
    or_file = os.path.expanduser(org_files[0])
    oz_file = os.path.expanduser(orgzly_files[0])
    res_name = os.path.basename(resources_path)
    res_dict['resources'] = res_name
    or_dir = os.path.dirname(or_file)
    res_dict['or_dir'] = or_dir
    oz_dir = os.path.dirname(oz_file)
    res_dict['oz_dir'] = oz_dir
    or_res = os.path.join(or_dir, res_name)
    res_dict['or_res'] = or_res
    oz_res = os.path.join(oz_dir, res_name)
    res_dict['oz_res'] = oz_res
    return res_dict


# -------------------------------------------------------------------------------------
# File Check
# -------------------------------------------------------------------------------------
def file_check(create_missing, org_files, orgzly_files, org_events,
               orgzly_events, resources_folder):
    res_dict = get_res(resources_folder, org_files, orgzly_files)
    or_res = res_dict.get("or_res")
    oz_res = res_dict.get("oz_res")
    resck = [or_res, oz_res]
    for res in resck:
        if not os.path.exists(res):
            shutil.posix.mkdir(str(res))
    events = [org_events, orgzly_events]
    flist = org_files + orgzly_files + events
    for file in flist:
        user_path = os.path.expanduser(file)
        file_title = os.path.basename(user_path).strip('.org')
        title_label = ' '.join(['#+TITLE: ', file_title])
        date_string = date.today().strftime('%Y-%m-%d %A')
        date_label = ' '.join(['#+DATE: ', date_string])
        if not os.path.isfile(user_path):
            if create_missing:
                with open(user_path, 'a', encoding='utf-8') as c_f:
                    c_f.write(title_label)
                    c_f.write('\n')
                    c_f.write(date_label)
                    c_f.write('\n')
                    c_f.write('#Created by org-orgzly')
                    c_f.write('\n')
                    c_f.write('#----------------------')
                    c_f.write('\n')
                    c_f.close()
                print('File Created: ' + user_path)
            else:
                print('File path does not exist, and creation of missing files'
                      ' has been disabled.')
                print('Missing file is: ' + user_path)
                print('Creation of missing files is set to: ' + create_missing)
                print('Please review your file paths in the config file,'
                      ' or enable creation of missing files with "True", '
                      'an then try again.')
                return False
    return True


# ---------------------------------------------------------------------------------------
def handle_zombies(zombie, working_dir):
    working_path = os.path.realpath(working_dir)
    zombie_path = os.path.join(working_path, 'zombie.org')
    with open(zombie_path, 'a', encoding='utf-8') as z_f:
        z_f.write(str(zombie))
        z_f.write('\n')
        z_f.close()
    return True


# ---------------------------------------------------------------------------------------
# get parser
# ---------------------------------------------------------------------------------------
def get_parser(parse_file):
    config = ConfigObj(CONFIG_FILE)
    parser = orgparse.load(parse_file)
    add_keys = parser.env.add_todo_keys
    add_keys(config['todos'], config['dones'])
    parser.tags.add('@org-orgzly')
    return parser


# ---------------------------------------------------------------------------------------
# The startup command
# ---------------------------------------------------------------------------------------
def main():
    # Setup of ConfigObj
    config = ConfigObj()
    spec = cfg.split("\n")

    # ArgParse Setup
    p_arg = argparse.ArgumentParser(
            prog='org-orgzly',
            usage='%(prog)s.py [ --up | --down ] or [ --push |'
                  ' --pull || --put | --get ] '
                  ' or --list '
            ' or --dropbox_token',
            description='Makes managing mobile org '
            'easier, by controling what you take with you.',
            epilog='Dedicated to karlicoss, who made it possible.',
            conflict_handler='resolve')
    # Arguments for argparse
    p_arg.add_argument('--version', action='version',
                       version='org-orgzly ' + VERSION)
    p_arg.add_argument('--dropbox_token', action='store_true',
                       help='Fetch initial Access Token')
    p_arg.add_argument('--config', help='path to configuration file'),
    p_arg.add_argument('--list', action='store_true',
                       help='list files in orgzly directory in dropbox')
    p_arg.add_argument('--up', action='store_true',
                       help='push to orgzly and up to dropbox')
    p_arg.add_argument('--down', action='store_true',
                       help='down from dropbox and pull from orgzly')
    p_arg.add_argument('--push', action='store_true',
                       help='Parse files and push them to orgzly')
    p_arg.add_argument('--pull', action='store_true',
                       help='Pull new entries from orgzly to org inbox')
    p_arg.add_argument('--put', action='store_true',
                       help='Upload orgzly files to dropbox')
    p_arg.add_argument('--get', action='store_true',
                       help='Download orgzly files from dropbox')
    ##################
    # parse the args #
    ##################
    args = p_arg.parse_args()

    # -------------------------------
    # Print title
    # -------------------------------
    art.tprint('Org-Orgzly', font='rnd-small')

    # ----------------------------------
    # # Now Process configObj #
    # ----------------------------------
    if args.config is not None:
        filename = args.config
    else:
        filename = CONFIG_FILE
    if not os.path.isfile(filename):
        config = ConfigObj(filename, configspec=spec)
        config.filename = filename
        validator = validate.Validator()
        config.validate(validator, copy=True)
        config.write()
        print("Configuration file written to "
              "$XDG_CONFIG_HOME/orgzly/config.ini")
        sys.exit()
    else:
        config = ConfigObj(filename, configspec=spec)
    ########################
    # Load org todo values #
    ########################
    env = OrgEnv()
    addkeys = env.add_todo_keys
    addkeys(todos=config['todos'], dones=config['dones'])


    ##########################
    # Add inbox to org_files #
    ##########################
    org_files = config['org_files']
    orgzly_files = config['orgzly_files']
    conf_orin = config['org_inbox']
    conf_ozin = config['orgzly_inbox']
    org_files.append(conf_orin)
    orgzly_files.append(conf_ozin)
    if config['split_events']:
        split_events = True


    # check that files exist and create if missing:
    fcheck = file_check(config['create_missing'], org_files,
                        orgzly_files, config['org_events'],
                        config['orgzly_events'], config['resources_folder'])

    # OK, I admit. The following is a bit of a mess.

    # Run the gambit of args vs config
    if fcheck:
        # First the two meta commands: up and down
        if args.up:
            if config['backup']:
                backup_files(org_files, orgzly_files, config['orgzly_events'],
                             config['org_events'], config['days'])
            gen_file(env, org_files, config['orgzly_inbox'],
                     config['days'], split_events,
                     config['org_events'], config['orgzly_events'],
                     config['resources_folder'])
            dropbox_put(config['app_key'], config['app_secret'],
                        config['dropbox_folder'], orgzly_files,
                        config['orgzly_events'], config['resources_folder'])
        if args.down:
            dropbox_get(config['app_key'], config['app_secret'],
                        config['dropbox_folder'], orgzly_files,
                        config['orgzly_events'], config['resources_folder'])
            sync_back(orgzly_files, config['org_inbox'],
                      org_files, split_events,
                      config['org_events'], config['orgzly_events'],
                      config['resources_folder'])
        if args.push:
            if config['backup']:
                backup_files(org_files, orgzly_files, config['orgzly_events'],
                             config['org_events'], config['days'])
            gen_file(env, org_files, config['orgzly_inbox'],
                     config['days'], split_events,
                     config['org_events'], config['orgzly_events'],
                     config['resources_folder'])
        if args.pull:
            sync_back(orgzly_files, config['org_inbox'],
                      org_files, split_events,
                      config['org_events'], config['orgzly_events'],
                      config['resources_folder'])
        if args.put:
            dropbox_put(config['app_key'], config['app_secret'],
                        config['dropbox_folder'], orgzly_files,
                        config['orgzly_events'], config['resources_folder'])
        if args.get:
            dropbox_get(config['app_key'], config['app_secret'],
                        config['dropbox_folder'], orgzly_files,
                        config['orgzly_events'], config['resources_folder'])

    if not fcheck:
        print('Error occured in creation of necessarily files, '
              'or file creation has been disabled.\n'
              ' Please check your config and try again.')
        sys.exit()
    # Last the two "auxilliary commands"
    if args.dropbox_token:
        get_access_token(config['app_key'], config['app_secret'])
    if args.list:
        list_orgzly(config['app_key'], config['app_secret'],
                    config['dropbox_folder'])


if __name__ == '__main__':
    main()
