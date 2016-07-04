#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright © 2016 seamus tuohy, <code@seamustuohy.com>
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the included LICENSE file for details.

# Get all contacts from a notmuch database and write them out as either
# an org file or a plain text list


# imports

from notmuch import Database, Query
from notmuch.errors import NullPointerError
from email.Utils import parseaddr
import re

# Globals

SPAM = ["eventbrite.com", "docs.google.com"]

# Functions
# Uses notmuch to gather all contacts.

def get_contacts():
    db = Database(mode=Database.MODE.READ_ONLY)
    msgs = Query(db, '*').search_messages()
    _all_msg_addrs = []
    for msg in msgs:
        _addr_list = []
        addr_hdr = ["to", "from", "cc", "bcc"]
        try:
            for hdr in addr_hdr:
                _addr = msg.get_header(hdr)
                _addr_list = _addr.split(",")
                for a in _addr_list:
                    # normalize
                    normalized = a.lower().strip().encode('ascii', 'ignore')
                    # get address tuple from email and remove spaces
                    tabled = [e.strip() for e in parseaddr(normalized)]
                    # Remove any of that repeated address cruft people always put in
                    tabled[0] = re.sub("\<.*\>", "", re.sub("\(.*\)", "", tabled[0]))
                    # Strip out any quotes for when we convert to org later
                    tabled = [re.sub("\"", " ", x).strip() for x in tabled]
                    tabled = [re.sub("\'", " ", x).strip() for x in tabled]
                    # I don't want no empty strings
                    tabled = [x for x in tabled if x != "" and x != " "]
                    # Check to make sure all single line items are address'
                    _address = False
                    if len(tabled) == 1:
                        if "@" in tabled[0]:
                            _address = True
                    else:
                        _address = True
                    if _address and tabled != [] and tabled not in _all_msg_addrs:
                        _all_msg_addrs.append(tabled)
        except NullPointerError:
            pass
    return _all_msg_addrs

def indexed(x, cons):
    for i in cons:
        if len(i) == 2:
            if x == i[1]:
                return True
    return False

def deduplicate(raw_contacts):
  items = [x for x in raw_contacts if not indexed(x[0], raw_contacts)]
  return items

def make_org(contacts, my_org_contacts):
      pheader = ":PROPERTIES:\n"
      pbackend = """:PHONE:
:ALIAS:
:NICKNAME:
:IGNORE:
:ICON:
:NOTE:
:ADDRESS:
:BIRTHDAY:
:END:\n"""
      with open(my_org_contacts, "w+") as cfile:
          for i in contacts:
              try:
                  if len(i) == 2:
                      # get the domain the email is coming from
                      rawtag = i[1].rsplit(".", 1)[0].rsplit("@", 1)[1]
                      tag = ":{0}:".format(''.join(e for e in rawtag if e.isalnum()))
                  else:
                      rawtag = i[0].rsplit(".", 1)[0].rsplit("@", 1)[1]
                      tag = ":{0}:".format(''.join(e for e in rawtag if e.isalnum()))

                  cfile.write("* {0} {1}\n".format(i[0], tag))
                  cfile.write(pheader)
                  if len(i) == 1:
                      cfile.write(":EMAIL: {0}\n".format(i[0]))
                  else:
                      cfile.write(":EMAIL: {0}\n".format(i[1]))
                  cfile.write(pbackend)
              except:
                  pass

def make_list(contacts, list_path):
      with open(list_path, "w+") as cfile:
          for i in contacts:
              try:
                  if len(i) == 2:
                      # get the domain the email is coming from
                      rawtag = i[1].rsplit(".", 1)[0].rsplit("@", 1)[1]
                      tag = ":{0}:".format(''.join(e for e in rawtag if e.isalnum()))
                  else:
                      rawtag = i[0].rsplit(".", 1)[0].rsplit("@", 1)[1]
                      tag = ":{0}:".format(''.join(e for e in rawtag if e.isalnum()))

                  cfile.write("{0} ".format(i[0], tag))
                  if len(i) == 1:
                      cfile.write("<{0}>\n".format(i[0]))
                  else:
                      cfile.write("<{0}>\n".format(i[1]))
              except:
                  pass

# Main

def main():
    raw_contacts = get_contacts()
    deduped = deduplicate(raw_contacts)
    #make_org(deduped, "./contacts.org")
    make_list(deduped, "./contacts.txt")

if __name__ == '__main__':
    main()
