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
from email.header import Header, decode_header
from email.parser import Parser
from email.utils import parseaddr
try:  # Python 2
    from hashlib import md5
    INT = long
except:  # Python 3
    from md5 import md5  # lint:ok
    INT = int
import re
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

    @property
    def headers(self):
        'Return a flattened version of the headers in the message'
        # --=mpj17=-- Not @Lazy because self.message. changes.
        headers = [': '.join(x) for x in self.message.items()]
        header_string = '\n'.join(headers)
        retval = to_unicode_or_bust(header_string, self.encoding)
        return retval

    @staticmethod
    def parse_disposition(s):
        '''Get the filename from the content disposition header'''
        matchObj = re.search('(?i)filename="*(?P<filename>[^"]*)"*', s)
        retval = ''
        if matchObj:
            retval = matchObj.group('filename')
        return retval

    @staticmethod
    def calculate_file_id(file_body, mime_type):
        '''Generate a new identifer for a file
:param bytes file_body: The body of the file
:param string mime_type: The MIME-type of the file
:returns: A 3-tuple of ``(identifier, length, fileMD5)

Two files will have the same ID if

* They have the same MD5 Sum, *and*
* They have the same length, *and*
* They have the same MIME-type.'''
        length = len(file_body)
        md5_sum = md5()
        for c in file_body:
            if type(c) == unicode:
                md5_sum.update(c.encode('ascii', 'xmlcharrefreplace'))
            else:
                md5_sum.update(c)
        file_md5 = md5_sum.hexdigest()
        md5_sum.update(':' + str(length) + ':' + mime_type)
        vNum = convert_int2b62(INT(md5_sum.hexdigest(), 16))
        retval = (to_unicode_or_bust(vNum), length, file_md5)
        return retval

    @Lazy
    def attachments(self):
        'Get the attachments, including the body'
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
                      'charset': str(self.message.get_charset()),
                      'maintype': self.message.get_content_maintype(),
                      'subtype': self.message.get_content_subtype(),
                      'mimetype': self.message.get_content_type(),
                      'contentid': self.message.get('content-id', '')}]
        assert retval is not None
        assert type(retval) == list
        return retval

    @Lazy
    def html_body(self):
        retval = ''
        for item in self.attachments:
            if item['filename'] == '' and item['subtype'] == 'html':
                retval = to_unicode_or_bust(item['payload'],
                                            item['charset'])
        return retval

    @Lazy
    def body(self):
        retval = ''
        for item in self.attachments:
            if item['filename'] == '' and item['subtype'] != 'html':
                retval = to_unicode_or_bust(item['payload'], self.encoding)
                break
        if self.html_body and (not retval):
            retval = convert_to_txt(self.html_body).strip()
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
            subject = 'No subject'
        return subject

    @Lazy
    def decodedSubject(self):
        # A subject can be a series of words, each with a different
        # encoding. First, get a list of (word, encoding) 2-tuples.
        subjectTuples = decode_header(self.message['Subject'])
        # Next, decode each onto Unicode. Tradition assumes ASCII, but I
        # (mpj17) will assume UTF-8.
        subjectWords = [t[0].decode(t[1] or 'utf-8') for t in subjectTuples]
        # Finally, join them all together.
        retval = ''.join(subjectWords)
        return retval

    @Lazy
    def subject(self):
        retval = self.strip_subject(self.decodedSubject, self._list_title)
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
        sender = self.message.get('From')
        if sender:
            name, addr = parseaddr(sender)
            retval = addr.lower()
        return retval

    @Lazy
    def name(self):
        sender = self.message.get('From')
        retval = ''
        if sender:
            retval, sender = parseaddr(sender)
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
        md5Body = md5(self.body.encode('utf-8')).hexdigest()
        items = (self.topic_id + ':' + self.subject + ':' +
                 md5Body + ':' + self.sender + ':' +
                 self.message.get('in-reply-to', '') +
                 ':' + str(len_payloads))
        pid = md5(items.encode('utf-8')).hexdigest()
        retval = to_unicode_or_bust(convert_int2b62(INT(pid, 16)))
        return retval
