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
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
#from mock import patch
from unittest import TestCase
from gs.group.list.base.emailmessage import EmailMessage


class EmailMessageTest(TestCase):
    m = '''From: Me <a.member@example.com>
To: Group <group@groups.example.com>
Subject: Violence

Tonight on Ethyl the Frog we look at violence.\n'''

    def setUp(self):
        self.message = EmailMessage(self.m, list_title='Ethyl the Frog',
                                    group_id='ethyl')

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

    def test_headers(self):
        r = self.message.headers
        self.assertEqual(self.m.split('\n\n')[0], r)

    def test_parse_disposition_no_match(self):
        r = self.message.parse_disposition('Putting the boot in')
        self.assertEqual('', r)

    def test_parse_disposition(self):
        d = '''Content-disposition: attachment; filename="IMG.pdf"'''
        r = self.message.parse_disposition(d)
        self.assertEqual('IMG.pdf', r)

    def test_calculate_file_id(self):
        # --=mpj17=-- Using self.m as the file body because it is convinient
        r = self.message.calculate_file_id(self.m, 'text/plain')
        self.assertEqual('1gQzS4P7jPaZmJ9m51zQlY', r[0])
        self.assertEqual(135, r[1])

    def test_attachments_none(self):
        'Test the body "attachment".'
        r = self.message.attachments
        self.assertEqual(1, len(r))
        self.assertEqual('text/plain', r[0]['mimetype'])
        self.assertEqual(self.m.split('\n\n')[1], r[0]['payload'])

    def test_attachments_text(self):
        'Test a plain-text attachment to a plain-text message'
        # Create the message
        mm = MIMEMultipart()
        bodyText = MIMEText(
            'Tonight on Ethyl the Frog we look at violence.\n')
        mm.attach(bodyText)
        textAttachment = MIMEText(
            'When he grew up he took to putting the boot in.')
        textAttachment.add_header('Content-Disposition', 'attachment',
                                  filename='script.txt')
        mm.attach(textAttachment)
        for h, v in self.message.message.items():
            mm.add_header(h, v)
        self.message.message = mm

        r = self.message.attachments
        self.assertEqual(2, len(r))
        self.assertEqual('text/plain', r[0]['mimetype'])
        self.assertEqual(bodyText.get_payload(), r[0]['payload'])
        self.assertEqual('text/plain', r[1]['mimetype'])
        self.assertEqual(textAttachment.get_payload(), r[1]['payload'])

    def test_html_body(self):
        a = MIMEMultipart('alternative')
        tt = MIMEText(
            'Tonight on Ethyl the Frog\u2026 we look at violence.\n',
            'plain', 'UTF-8')
        a.attach(tt)
        th = MIMEText(
            '<p>Tonight on Ethyl the Frog&#8230; we look at '
            'violence.\n</p>', 'html', 'us-ascii')
        a.attach(th)
        for h, v in self.message.message.items():
            a.add_header(h, v)
        self.message.message = a

        r = self.message.html_body
        self.assertEqual(th.get_payload(), r)

    def test_html_body_utf8(self):
        a = MIMEMultipart('alternative')
        tt = MIMEText(
            'Tonight on Ethyl the Frog\u2026 we look at violence.\n',
            'plain', 'UTF-8')
        a.attach(tt)
        th = MIMEText(
            '<p>Tonight on Ethyl the Frog\u2026 we look at '
            'violence.\n</p>', 'html', 'utf-8')
        a.attach(th)
        for h, v in self.message.message.items():
            a.add_header(h, v)
        self.message.message = a

        expected = th.get_payload(decode=True).decode('utf-8')
        r = self.message.html_body
        self.assertEqual(expected, r)

    def test_html_body_latin1(self):
        a = MIMEMultipart('alternative')
        tt = MIMEText(
            'Tonight on Ethyl the Frog\u2026 we look at violence.\n',
            'plain', 'UTF-8')
        a.attach(tt)
        th = MIMEText(
            '<p>Je ne ecrit pas français.\n</p>', 'html', 'latin-1')
        a.attach(th)
        for h, v in self.message.message.items():
            a.add_header(h, v)
        self.message.message = a

        expected = th.get_payload(decode=True).decode('latin-1')
        r = self.message.html_body
        self.assertEqual(expected, r)

    def test_body(self):
        'Test the simple case where there is only a plain-text body'
        r = self.message.body
        self.assertEqual('Tonight on Ethyl the Frog we look at violence.\n',
                         r)

    def test_body_utf8(self):
        tt = MIMEText(
            'Tonight on Ethyl the Frog\u2026 we look at violence.\n',
            'plain', 'UTF-8')
        for h, v in self.message.message.items():
            tt.add_header(h, v)
        self.message.message = tt

        expected = tt.get_payload(decode=True).decode('utf-8')
        r = self.message.body
        self.assertEqual(expected, r)

    def test_body_latin1(self):
        tt = MIMEText(
            "Je ne ecrit pas français.",
            'plain', 'iso8859-1')
        for h, v in self.message.message.items():
            tt.add_header(h, v)
        self.message.message = tt

        expected = tt.get_payload(decode=True).decode('iso8859-1')
        r = self.message.body
        self.assertEqual(expected, r)

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

    def test_subject(self):
        r = self.message.subject
        self.assertEqual('Violence', r)

    def test_subject_stripped(self):
        self.message.message.replace_header(
            'Subject', '[Ethyl the Frog] The Violence of British Gangland')
        r = self.message.subject
        self.assertEqual('The Violence of British Gangland', r)

    def test_normalise_subject_empty(self):
        r = self.message.normalise_subject('')
        self.assertEqual('', r)

    def test_normalise_lower(self):
        r = self.message.normalise_subject('Violence')
        self.assertEqual('violence', r)

    def test_normalise_lower_whitespace(self):
        r = self.message.normalise_subject('The Violence of British '
                                           'Gangland')
        self.assertEqual('theviolenceofbritishgangland', r)

    def test_compressed_subject(self):
        r = self.message.compressed_subject
        self.assertEqual('violence', r)

    def test_compressed_subject_whitespace(self):
        self.message.message.replace_header(
            'Subject', '[Ethyl the Frog] The Violence of British Gangland')
        r = self.message.compressed_subject
        self.assertEqual('theviolenceofbritishgangland', r)

    def test_sender(self):
        r = self.message.sender
        self.assertEqual('a.member@example.com', r)

    def test_name(self):
        r = self.message.name
        self.assertEqual('Me', r)
