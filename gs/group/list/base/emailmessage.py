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
import codecs
from email.parser import Parser
from email.header import Header
try:  # Python 2
    from hashlib import md5
    INT = long
except:  # Python 3
    from md5 import md5  # lint:ok
    INT = int
import re
from rfc822 import AddressList
import string
from zope.cachedescriptors.property import Lazy
from gs.core import to_unicode_or_bust, convert_int2b62
from .html2txt import convert_to_txt

reRegexp = re.compile('re:', re.IGNORECASE)
fwRegexp = re.compile('fw:', re.IGNORECASE)
fwdRegexp = re.compile('fwd:', re.IGNORECASE)
# See <http://www.w3.org/TR/unicode-xml/#Suitable>
uParaRegexep = re.compile('[\u2028\u2029]+')
annoyingChars = string.whitespace + '\uFFF9\uFFFA\uFFFB\uFFFC\uFEFF'
annoyingCharsL = annoyingChars + '\u202A\u202D'
annoyingCharsR = annoyingChars + '\u202B\u202E'


class EmailMessage(object):

    def __init__(self, messageString, list_title='', group_id='',
                 site_id='', sender_id_cb=None):
        self._list_title = list_title
        self.group_id = group_id
        self.site_id = site_id
        self.sender_id_cb = sender_id_cb
        # --=mpj17=-- self.message is not @Lazy, because it is mutable.
        parser = Parser()
        self.message = parser.parsestr(messageString)

    @staticmethod
    def check_encoding(encoding):
        # A slightly wierd encoding that isn't in the standard encoding
        # table
        if encoding.lower() == 'macintosh':
            encoding = 'mac_roman'
        try:
            codecs.lookup(encoding)
        except:
            # play it pretty safe ... we're going to be ignoring errors in
            # the encoding anyway, and UTF-8 is going to be right more of
            # the time in the very, very rare case that we have to force
            # this!
            encoding = 'utf-8'
        return encoding

    def get(self, name, default=''):
        value = self.message.get(name, default)
        header_parts = []
        for value, encoding in Header.decode_header(value):
            encoding = self.check_encoding(encoding) if encoding else \
                self.encoding
            part = to_unicode_or_bust(value, encoding)
            header_parts.append(part)

        return ' '.join(header_parts)

    @Lazy
    def sender_id(self):
        # FIXME: rewrite into a query.
        retval = ''
        if self.sender_id_cb:
            retval = self.sender_id_cb(self.sender)

        return retval

    @Lazy
    def encoding(self):
        encoding = self.check_encoding(self.message.get_param('charset',
                                                              'utf-8'))
        return encoding

    @staticmethod
    def parse_disposition(s):
        matchObj = re.search('(?i)filename="*(?P<filename>[^"]*)"*', s)
        name = ''
        if matchObj:
            name = matchObj.group('filename')
        return name

    @property
    def headers(self):
        # --=mpj17=-- Not @Lazy because self.message. changes.
        # return a flattened version of the headers
        header_string = '\n'.join(['%s: %s' % (x[0], x[1])
                                   for x in self.message._headers])
        retval = to_unicode_or_bust(header_string, self.encoding)
        return retval

    @Lazy
    def body(self):
        retval = ''
        for item in self.attachments:
            if item['filename'] == '' and item['subtype'] != 'html':
                retval = to_unicode_or_bust(item['payload'], self.encoding)
                break
        html_body = self.html_body
        if html_body and (not retval):
            h = html_body.encode(self.encoding, 'xmlcharrefreplace')
            retval = convert_to_txt(h)
        assert retval is not None
        return retval

    @staticmethod
    def strip_subject(subject, list_title, remove_re=True):
        """ A helper function for tidying the subject line.

        """
        # remove the list title from the subject, if it isn't just an
        # empty string
        if list_title:
            subject = re.sub('\[%s\]' % re.escape(list_title), '',
                             subject).strip()

        subject = uParaRegexep.sub(' ', subject)
        # compress up the whitespace into a single space
        subject = re.sub('\s+', ' ', subject).strip()
        if remove_re:
            # remove the "re:" from the subject line. There are probably
            # other variants we don't yet handle.
            subject = reRegexp.sub('', subject)
            subject = fwRegexp.sub('', subject)
            subject = fwdRegexp.sub('', subject)
            subject = subject.lstrip(annoyingCharsL + '[')
            subject = subject.rstrip(annoyingCharsR + ']')
        else:
            subject = subject.lstrip(annoyingCharsL)
            subject = subject.rstrip(annoyingCharsR)
        if len(subject) == 0:
            subject = 'No Subject'
        return subject

    @Lazy
    def subject(self):
        retval = self.strip_subject(self.get('subject'), self._list_title)
        return retval

    @staticmethod
    def normalise_subject(subject):
        """Compress whitespace and lower-case subject"""
        return re.sub('\s+', '', subject).lower()

    @Lazy
    def compressed_subject(self):
        return self.normalise_subject(self.subject)

    @Lazy
    def sender(self):
        sender = self.get('from')
        if sender:
            name, sender = AddressList(sender)[0]
            sender = sender.lower()
        return sender

    @Lazy
    def name(self):
        sender = self.get('from')
        retval = ''
        if sender:
            retval, sender = AddressList(sender)[0]
        return retval

    @Lazy
    def to(self):
        to = self.get('to')
        if to:
            name, to = AddressList(to)[0]
            to = to.lower()
        # --=mpj17=-- TODO: Add the group name.
        return to

    @Lazy
    def title(self):
        return '%s / %s' % (self.subject, self.sender)

    @Lazy
    def inreplyto(self):
        return self.get('in-reply-to')

    @Lazy
    def md5_body(self):
        retval = md5(self.body.encode('utf-8')).hexdigest()
        return retval

    @Lazy
    def topic_id(self):
        # this is calculated from what we have/know

        # A topic_id for two posts will clash if
        #   - The compressedsubject, group ID and site ID are all identical
        items = self.compressed_subject + ':' + self.group_id + ':' + \
            self.site_id
        tid = md5(items.encode('utf-8')).hexdigest()

        retval = to_unicode_or_bust(convert_int2b62(INT(tid, 16)))
        return retval

    @Lazy
    def post_id(self):
        # this is calculated from what we have/know
        len_payloads = sum([x['length'] for x in self.attachments])

        # A post_id for two posts will clash if
        #    - The topic IDs are the same, and
        #    - The subject is the same (this may not be the same as
        #      compressed subject used in topic id)
        #    - The body of the posts are the same, and
        #    - The posts are from the same author, and
        #    - The posts respond to the same message, and
        #    - The posts have the same length of attachments.
        items = (self.topic_id + ':' + self.subject + ':' +
                 self.md5_body + ':' + self.sender + ':' +
                 self.inreplyto + ':' + str(len_payloads))
        pid = md5(items.encode('utf-8')).hexdigest()
        retval = to_unicode_or_bust(convert_int2b62(INT(pid, 16)))
        return retval
