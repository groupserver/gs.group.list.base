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
#from mock import patch
from unittest import TestCase
from gs.group.list.base.emailmessage import EmailMessage


class EmailMessageTest(TestCase):
    m = '''From: Me <a.member@example.com>
To: Group <group@groups.example.com>
Subject: Violence

Tonight on Ethyl the Frog we look at violence.\n'''

    def setUp(self):
        self.message = EmailMessage(self.m)

    def test_check_encoding_odd(self):
        r = self.message.check_encoding('wierd')
        self.assertEqual('utf-8', r)

    def test_check_encoding_macintosh(self):
        r = self.message.check_encoding('macintosh')
        self.assertEqual('mac_roman', r)

    def test_check_encoding_ascii(self):
        r = self.message.check_encoding('ascii')
        self.assertEqual('ascii', r)

    def test_check_encoding_utf8(self):
        r = self.message.check_encoding('utf-8')
        self.assertEqual('utf-8', r)

    def test_encoding_missing(self):
        r = self.message.encoding
        self.assertEqual('utf-8', r)

    def test_encoding_ascii(self):
        self.message.message.set_charset('ascii')
        r = self.message.encoding
        self.assertEqual('us-ascii', r)

    def test_encoding_latin1(self):
        self.message.message.set_charset('latin1')
        r = self.message.encoding
        self.assertEqual('iso8859-1', r)

    def test_encoding_iso8859_1(self):
        self.message.message.set_charset('ISO8859-1')
        r = self.message.encoding
        self.assertEqual('iso8859-1', r)

    def test_encoding_utf8(self):
        self.message.message.set_charset('utf-8')
        r = self.message.encoding
        self.assertEqual('utf-8', r)

    def test_normalise_subject_empty(self):
        r = self.message.normalise_subject('')
        self.assertEqual('', r)

    def test_normalise_lower(self):
        r = self.message.normalise_subject('Violence')
        self.assertEqual('violence', r)

    def test_normalise_lower_whitespace(self):
        r = self.message.normalise_subject('Ethyl the Frog')
        self.assertEqual('ethylthefrog', r)

    def test_strip_subject(self):
        r = self.message.strip_subject('[Ethyl the Frog] Violence',
                                       'Ethyl the Frog')
        self.assertEqual('Violence', r)

    def test_strip_subject_missing(self):
        r = self.message.strip_subject('', 'Ethyl the Frog')
        self.assertEqual('No subject', r)

    def test_strip_subject_re(self):
        r = self.message.strip_subject('Re: [Ethyl the Frog] Violence',
                                       'Ethyl the Frog')
        self.assertEqual('Violence', r)

    def _test_compressed_subject(self):
        r = self.message.compressed_subject
        self.assertEqual('ethylthefrog', r)
