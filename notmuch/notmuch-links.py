#!/usr/bin/env python3
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

# Take a notmuch database and pull out all the URLs that are tagged "notes"
# I use this to be able to take all the e-mails that I send to myself and
# auto-tag those as notes, and scrape out all the links I have sent myself

# TODO
# INSTALL NEEDS THE FOLLOWING
# apt-get install python3-notmuch
# pip3 install rfc3987

# imports

from notmuch import Database, Query
import email
from email.iterators import typed_subpart_iterator
import re
from urllib.parse import urlparse
from urllib.request import urlopen
from bs4 import BeautifulSoup
from urllib.error import HTTPError

notes_file = "./email_note_file"
url_file = "./email_url_file"
url_toss_file = "./email_toss_url_file"

GRUBER_URLINTEXT_PAT = re.compile(r'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?\xab\xbb\u201c\u201d\u2018\u2019]))')

def main():
    db = Database(mode=Database.MODE.READ_ONLY)
    msgs = Query(db, 'tag:notes').search_messages()
    with open(notes_file, "a") as notefile:
        for msg in msgs:
            filename = msg.get_filename()
            with open(filename, 'r') as message_file:
                raw_msg = message_file.read()
                eml_msg = email.message_from_string(raw_msg)
                msg_txt = get_body(eml_msg)
                urls = [mgroups[0] for mgroups in GRUBER_URLINTEXT_PAT.findall(msg_txt)]
                for url in urls:
                    notefile.write("{0}\n".format(url))

def get_body(message):
    """Get the body of the email message"""

    if message.is_multipart():
        #get the plain text version only
        text_parts = [part
                      for part in typed_subpart_iterator(message,
                                                         'text',
                                                         'plain')]

        body = []
        for part in text_parts:
            _part = part.get_payload(decode=True)
            _part = _part.decode('utf-8', "replace")
            body.append(_part)

        return u"\n".join(body).strip()

    else: # if it is not multipart, the payload will be a string
          # representing the message body
        body = message.get_payload(decode=True)
        body = body.decode('utf-8', "replace")
        return body.strip()

def strip_lame_urls(notes_file, url_file):
    with open(url_file, "a") as url_file:
        with open(notes_file, "r") as notefile:
            for url in notefile:
                parsed = urlparse(url)
                raw_netloc = ""
                # If url does not have a scheme specified XXX://
                # then parse the netloc out of the path
                # https://docs.python.org/3.0/library/urllib.parse.html#urllib.parse.urlparse
                if parsed.netloc != "":
                    raw_netloc = parsed.netloc
                    raw_path = parsed.path
                else:
                    raw_netloc = parsed.path.split("/")[0]
                    raw_path = "/" + "/".join(parsed.path.split("/")[1:])
                if check_toss(raw_netloc, raw_path):
                    continue
                if check_unwanted(raw_netloc, raw_path):
                    continue
                recursed_url = check_recurse(raw_netloc, url)
                if recursed_url:
                    url_file.write("{0}".format(recursed_url))
                else:
                    url_file.write("{0}".format(url))


def tco_scrape(url):
    try:
        tweet = urlopen(url)
    except HTTPError:
        print("{0} failed to download".format(url))
        return False
    raw = tweet.read()
    html_obj = BeautifulSoup(raw, 'lxml')
    for link in html_obj.find_all("a"):
        if link.get("data-expanded-url"):
            return link.get("data-expanded-url")
    # Fail to the basic URL
    return False

def check_recurse(netloc, url):
    recurse_functions = {"t.co":tco_scrape}
    if netloc in recurse_functions:
        return recurse_functions[netloc](url)
    else:
        return False


def get_toss_list():
    with open(url_toss_file, 'r') as toss_file:
        toss_list = [line.strip('\n') for line in toss_file]
        toss_list = toss_file.readlines()

def check_toss(netloc, path):
    toss = get_toss_list()
    if netloc in toss:
        return True
    else:
        return False

def check_unwanted(netloc, path):
    check = {"twitter.com":["/download"]}
    if netloc in check:
        for test_path in check[netloc]:
            if test_path == path:
                return True
    return False


if __name__ == '__main__':
    main()
    strip_lame_urls(notes_file, url_file)
