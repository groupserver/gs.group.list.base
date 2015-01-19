# -*- coding: utf-8 -*-
############################################################################
#
# Copyright © 2015 OnlineGroups.net and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
############################################################################
from __future__ import absolute_import, unicode_literals
import re
try:  # Python 3
    from html.entities import name2codepoint
    from html.parser import HTMLParser
    unicodeOrString = str
    unichrOrChr = chr
except:  # Python 2
    from HTMLParser import HTMLParser
    from htmlentitydefs import name2codepoint
    unicodeOrString = unicode
    unichrOrChr = unichr
from textwrap import TextWrapper
from gs.core import to_ascii, to_unicode_or_bust


class HTMLConverter(HTMLParser):
    '''Convert HTML to plain text

    This class, which extends the standard HTMLParser, converts HTML to
    plain text. It does this by getting all the data in the HTML
    elements, simplifying the whitespace, and then removing duplicate
    newlines. In addition it puts the value of the ``href`` attributes
    of the anchor elements in angle-brackets after the anchor-text.'''

    dupeNewlineRE = re.compile('\s+\n\n+')
    dupeSpaceRE = re.compile('\s+')

    # See Ticket 596 <https://projects.iopen.net/groupserver/ticket/596>

    def __init__(self):
        HTMLParser.__init__(self)  # Old-style class
        self.textWrapper = TextWrapper(
            width=74, replace_whitespace=True, drop_whitespace=True)
        self.outText = ''
        self.lastHREF = []
        self.lastData = ''
        self.outP = None

    def __unicode__(self):
        text = self.dupeNewlineRE.sub('\n\n', self.outText)
        retval = to_unicode_or_bust(text).strip()
        return retval

    def __str__(self):
        if (unicodeOrString == str):  # Python 3
            retval = self.__unicode__()
        else:  # Python 2
            u = unicodeOrString(self)
            retval = to_ascii(u)
        return retval

    def handle_starttag(self, tag, attrs):
        # Remember the href attribute of the anchor, because it will
        #   be displayed *after* the data. The attribute may not be
        #   set because some crack smoking madman may have added anchor
        #   *targets* to the message.
        if tag == 'a':
            attrsDict = dict(attrs)
            self.lastHREF.append(attrsDict.get('href', ''))
        elif tag == 'p':
            self.outP = ''

    def handle_endtag(self, tag):
        # Display the value of the href attribute of the anchor, if set.
        #   Do not display the attribute value if it is the same as the
        #   link-text.
        if tag == 'a' and self.lastHREF:
            href = self.lastHREF.pop()
            if href and (href != self.lastData):
                self.emit(' <{0}> '.format(href))
        elif tag == 'p':
            t = self.dupeSpaceRE.sub(' ', self.outP)
            wrappedTxt = self.textWrapper.fill(t).lstrip() + '\n\n'
            self.outP = None
            self.emit(wrappedTxt)

    def emit(self, c):
        if self.outP is None:
            self.outText = self.outText + c
        else:
            self.outP = self.outP + c

    def handle_charref(self, name):
        i = int(name)
        c = unichrOrChr(i)
        self.emit(c)

    def handle_entityref(self, name):
        i = name2codepoint.get(name, None)
        if i is not None:
            c = unichrOrChr(i)
            self.emit(c)

    def handle_data(self, data):
        data = to_unicode_or_bust(data)
        d = data if data.strip() else '\n'
        self.lastData = d
        self.emit(d)


def convert_to_txt(html):
    if not html:
        raise ValueError('html argument not set.')
    converter = HTMLConverter()

    converter.feed(html)
    converter.close()

    retval = unicodeOrString(converter)
    return retval
