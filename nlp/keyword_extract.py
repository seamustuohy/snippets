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

from topia.termextract import extract
import re

# get text
text = open("plain.txt", "r").read()
text = text.lower()

# create extractor
extractor = extract.TermExtractor()
extractor.filter = extract.DefaultFilter(singleStrengthMinOccur=2)

all_terms = extractor(text)
words = []

# get rid of things that are not words
for term in all_terms:
    if len(term[0].strip()) > 2: # no smaller than 2 chars
        if len(term[0].split()) < 3: #nothing larger than three words
            if re.search('[a-z]|[A-Z]', term[0]):  #has to have letters
                words.append(term)

# get top 100 words
sorted_words = sorted(words, key=lambda x: int(x[1]), reverse=True)
top = sorted_words[:100]
for i in top:
    print(i[0])
