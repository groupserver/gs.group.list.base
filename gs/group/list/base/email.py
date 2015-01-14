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
from datetime import datetime
from email import Parser, Header
try:
    from hashlib import md5
except:
    from md5 import md5  # lint:ok
import re
from rfc822 import AddressList
import string
from zope.cachedescriptors.property import Lazy
from zope.datetime import parseDatetimetz
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

    def __init__(self, message, list_title='', group_id='', site_id='',
                 sender_id_cb=None, replace_mail_date=True):
        self._list_title = list_title
        self.group_id = group_id
        self.site_id = site_id
        self.sender_id_cb = sender_id_cb
        self.replace_mail_date = replace_mail_date
        # --=mpj17=-- self.message is not @Lazy, because it is mutable.
        parser = Parser.Parser()
        self.message = parser.parsestr(message)

    @Lazy
    def _date(self):
        retval = datetime.now()
        return retval

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

    @staticmethod
    def calculate_file_id(file_body, mime_type):
        #
        # Two files will have the same ID if
        # - They have the same MD5 Sum, and
        # - They have the same length, and
        # - They have the same MIME-type.
        #
        length = len(file_body)
        md5_sum = md5()
        for c in file_body:
            md5_sum.update(c)
        file_md5 = md5_sum.hexdigest()
        md5_sum.update(':' + str(length) + ':' + mime_type)
        vNum = convert_int2b62(long(md5_sum.hexdigest(), 16))
        retval = (to_unicode_or_bust(vNum), length, file_md5)
        return retval

    @Lazy
    def attachments(self):
        def split_multipart(msg, pl):
            if msg.is_multipart():
                for b in msg.get_payload():
                    pl = split_multipart(b, pl)
            else:
                pl.append(msg)

            return pl

        retval = []
        payload = self.message.get_payload()
        if isinstance(payload, list):
            outmessages = []
            for i in payload:
                outmessages = split_multipart(i, outmessages)

            for msg in outmessages:
                actual_payload = msg.get_payload(decode=True)
                encoding = msg.get_param('charset', self.encoding)
                pd = self.parse_disposition(msg.get('content-disposition',
                                                    ''))
                filename = to_unicode_or_bust(pd, encoding) if pd else ''
                fileid, length, md5_sum = self.calculate_file_id(
                    actual_payload, msg.get_content_type())
                retval.append({
                    'payload': actual_payload,
                    'fileid': fileid,
                    'filename': filename,
                    'length': length,
                    'md5': md5_sum,
                    'charset': encoding,  # --=mpj17=-- Issues?
                    'maintype': msg.get_content_maintype(),
                    'subtype': msg.get_content_subtype(),
                    'mimetype': msg.get_content_type(),
                    'contentid': msg.get('content-id', '')})
        else:
            # Since we aren't a bunch of attachments, actually decode the
            #   body
            payload = self.message.get_payload(decode=True)
            cd = self.message.get('content-disposition', '')
            pd = self.parse_disposition(cd)
            filename = to_unicode_or_bust(pd, self.encoding) if pd else ''

            fileid, length, md5_sum = self.calculate_file_id(
                payload, self.message.get_content_type())
            retval = [{
                      'payload': payload,
                      'md5': md5_sum,
                      'fileid': fileid,
                      'filename': filename,
                      'length': length,
                      'charset': self.message.get_charset(),
                      'maintype': self.message.get_content_maintype(),
                      'subtype': self.message.get_content_subtype(),
                      'mimetype': self.message.get_content_type(),
                      'contentid': self.message.get('content-id', '')}]
        assert retval is not None
        assert type(retval) == list
        return retval

    @property
    def headers(self):
        # --=mpj17=-- Not @Lazy because self.message. changes.
        # return a flattened version of the headers
        header_string = '\n'.join(['%s: %s' % (x[0], x[1])
                                   for x in self.message._headers])
        retval = to_unicode_or_bust(header_string, self.encoding)
        return retval

    @Lazy
    def attachment_count(self):
        count = 0
        for item in self.attachments:
            if item['filename']:
                count += 1
        return count

    @Lazy
    def language(self):
        # one day we might want to detect languages, primarily this
        # will be used for stemming, stopwords and search
        return 'en'

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

    @Lazy
    def html_body(self):
        for item in self.attachments:
            if item['filename'] == '' and item['subtype'] == 'html':
                return to_unicode_or_bust(item['payload'], self.encoding)
        return ''

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
    def date(self):
        if self.replace_mail_date:
            return self._date
        d = self.get('date', '').strip()
        if d:
            # if we have the format Sat, 10 Mar 2007 22:47:20 +1300 (NZDT)
            # strip the (NZDT) bit before parsing, otherwise we break the
            # parser
            d = re.sub(' \(.*?\)', '', d)
            return parseDatetimetz(d)
        return self._date

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

        retval = to_unicode_or_bust(convert_int2b62(long(tid, 16)))
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
        retval = to_unicode_or_bust(convert_int2b62(long(pid, 16)))
        return retval
