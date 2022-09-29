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
# https://codeburst.io/building-beautiful-command-line-interfaces-with-python-26c7e1bb54df?gi=fc1f4289663e
# https://click.palletsprojects.com/en/8.1.x/

# --------------------------------------------------------
# Imports
# --------------------------------------------------------
import orgparse
import datetime
from datetime import date
import click
import re
import pathlib
import sys

# --------------------------------------------------------
# Variables
# --------------------------------------------------------
sys.path.append(pathlib.posixpath.expanduser("~/.local/lib/python3.9"))
# org_file = pathlib.posixpath.expanduser("~/org/TODO.org")
dones = ['DONE', 'CANCELED']

# ---------------------------------------------------------
# The Beans
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
    d = d + days
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


@click.command()
@click.option("--org_file", default=pathlib.posixpath.expanduser("~/org/TODO.org"), help="File to process")
@click.option("--orgzly_file", default=pathlib.posixpath.expanduser("~/orgzly/tasks.org"), help="Full path to orgzly file to write to")
@click.option("--days", default=int(7), help="integer for number of days you want to process for your file.")
def gen_file(org_file, orgzly_file, days):
    file = orgparse.load(org_file)
    entries = list(file.children)
    ent_num = len(entries)
    print("Number of entries is: " + str(ent_num))
    dr = list(range(1, ent_num))
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
                    to_write = []
                    if entry not in to_write:
                        to_write.append(entry)
                        print("Entry added to list")
                    for x in to_write:
                        w = open(orgzly_file, "a", encoding="utf-8", newline="\n")
                        w.writelines(str(entry))
                        w.write("\n")
                        w.close()
                        print("Entry added to file")
                else:
                    if future_date <= date_org:
                        print("Dates do not fall within acceptable parameters. Due to: " + str(future_date) + " is less than " + str(date_org))
                    elif future_date >= date_org:
                        print("Dates do not meet parameters for some unknown reason or due to: " + str(date_today))
                    else:
                        print("There appears to be something wrong with: " + date_org)
        except IndexError:
            print("none found")

if __name__ == '__main__':
    gen_file()
