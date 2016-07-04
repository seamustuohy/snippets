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

# Spider a website and archive all the links on Internet Archive.

# https://github.com/seamustuohy/DocOps
from docops.review import Archive, MissingArchiveError, RobotAccessControlException, UnknownArchiveException
from urllib.error import HTTPError

from time import sleep

import re
import subprocess
#from subprocess import check_output, STDOUT

import argparse
import logging
logging.basicConfig(level=logging.ERROR)
log = logging.getLogger(__name__)

def main():
    args = parse_arguments()
    set_logging(args.verbose, args.debug)
    links = spider_site(args.url, args.delay)
    log.debug("{0}".format(links))
    output = archive_links(links, ".5")
    #output = archive_links(links, args.delay)
    print(output)

def spider_site(url, delay=None):
    """
    url (str): url to spider
    delay (int): number of seconds to delay between wgets
    """
    links = []
    if delay is None:
        wget_args = ['wget', '--no-check-certificate', '--spider', '-r', url]
    else:
        wget_args = ['wget', '-w', str(delay), '--no-check-certificate', '--spider', '-r', url]
    spider_stderr = subprocess.Popen(wget_args, stderr=subprocess.PIPE, stdout=subprocess.PIPE).stderr.readlines()
    for byte_line in spider_stderr:
        line = byte_line.decode('utf-8').strip('/\n')
        if re.match("^--", line) is not None:
            log.debug("{0} is a url".format(line))
            if re.search('\.(css|js|png|gif|jpg|JPG)$',
                        line):
                log.debug("{0} is an image".format(line))
                continue
            else:
                try:
                    url = re.match("^--.*?--\s{2}(.*)$",
                             line).groups(0)[0]
                    log.debug("Adding {0} to links".format(line))
                    links.append(url)
                except IndexError:
                    continue
    return links

def archive_links(links, delay=None):
    archived = {}
    for link in links:
        try:
            if delay is not None:
                sleep(float(delay))
            log.debug("Archiving {0} link".format(link))
            link_archive = Archive(link)
            log.debug("submitting link {0}".format(link))
            link_archive.submit()
            log.debug("requesting archived link {0}".format(link))
            archive = link_archive.request()
            log.debug("saving link pair {0} {1}".format(link, archive))
            archived.setdefault(link, archive)
        except (HTTPError, RobotAccessControlException,
        MissingArchiveError, UnknownArchiveException):
            continue
    return archived

# Command Line Functions below this point

def set_logging(verbose=False, debug=False):
    if debug == True:
        log.setLevel("DEBUG")
    elif verbose == True:
        log.setLevel("INFO")

def parse_arguments():
    parser = argparse.ArgumentParser("Get a summary of some text")
    parser.add_argument("--verbose", "-v",
                        help="Turn verbosity on",
                        action='store_true')
    parser.add_argument("--debug", "-d",
                        help="Turn debugging on",
                        action='store_true')
    parser.add_argument("--url", "-u",
                        help="Target Url to start archiving from")
    parser.add_argument("--delay", "-D",
                        help="Delay to use for spidering",
                        default=None)

    args = parser.parse_args()
    return args

def usage():
    print("TODO: usage needed")

if __name__ == '__main__':
    main()
