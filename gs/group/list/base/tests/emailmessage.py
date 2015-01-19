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
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.parser import Parser
from email.mime.text import MIMEText
#from mock import patch
import os
from unittest import TestCase
from gs.group.list.base.emailmessage import EmailMessage


class EmailMessageTest(TestCase):
    m = '''From: Me <a.member@example.com>
To: Group <group@groups.example.com>
Subject: Violence

Tonight on Ethel the Frog we look at violence.\n'''

    def setUp(self):
        self.message = EmailMessage(self.m, list_title='Ethel the Frog',
                                    group_id='ethel')

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
        self.assertEqual('5vsj6HxuPcUnW9ynMnxB6h', r[0])
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
            'Tonight on Ethel the Frog we look at violence.\n')
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
            'Tonight on Ethel the Frog\u2026 we look at violence.\n',
            'plain', 'UTF-8')
        a.attach(tt)
        th = MIMEText(
            '<p>Tonight on Ethel the Frog&#8230; we look at '
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
            'Tonight on Ethel the Frog\u2026 we look at violence.\n',
            'plain', 'UTF-8')
        a.attach(tt)
        th = MIMEText(
            '<p>Tonight on Ethel the Frog\u2026 we look at '
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
            'Tonight on Ethel the Frog\u2026 we look at violence.\n',
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
        self.assertEqual('Tonight on Ethel the Frog we look at violence.\n',
                         r)

    def test_body_utf8(self):
        tt = MIMEText(
            'Tonight on Ethel the Frog\u2026 we look at violence.\n',
            'plain', 'UTF-8')
        for h, v in self.message.message.items():
            tt.add_header(h, v)
        self.message.message = tt

        expected = tt.get_payload(decode=True).decode('utf-8')
        r = self.message.body
        self.assertEqual(expected, r)

    def test_body_windows1252(self):
        tt = MIMEText("Je ne ecrit pas français.", 'plain', 'Windows-1252')
        for h, v in self.message.message.items():
            tt.add_header(h, v)
        self.message.message = tt

        expected = tt.get_payload(decode=True).decode('Windows-1252')
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

    def test_body_html_only(self):
        th = MIMEText(
            '<p>Tonight on Ethel the Frog\u2026 we look at '
            'violence.\n</p>', 'html', 'utf-8')
        for h, v in self.message.message.items():
            th.add_header(h, v)
        self.message.message = th

        expected = 'Tonight on Ethel the Frog\u2026 we look at violence.'
        r = self.message.body
        self.assertEqual(expected, r)

    def test_body_html_only_latin1(self):
        th = MIMEText(
            "<p>Je ne ecrit pas français.</p>", 'html', 'latin-1')
        for h, v in self.message.message.items():
            th.add_header(h, v)
        self.message.message = th

        expected = 'Je ne ecrit pas français.'
        r = self.message.body
        self.assertEqual(expected, r)

    def test_body_html_only_windows1252(self):
        th = MIMEText(
            "<p>Je ne ecrit pas français.</p>", 'html', 'windows-1252')
        for h, v in self.message.message.items():
            th.add_header(h, v)
        self.message.message = th

        expected = 'Je ne ecrit pas français.'
        r = self.message.body
        self.assertEqual(expected, r)

    def test_strip_subject(self):
        r = self.message.strip_subject('[Ethel the Frog] Violence',
                                       'Ethel the Frog')
        self.assertEqual('Violence', r)

    def test_strip_subject_missing(self):
        r = self.message.strip_subject('', 'Ethel the Frog')
        self.assertEqual('No subject', r)

    def test_strip_subject_re(self):
        r = self.message.strip_subject('Re: [Ethel the Frog] Violence',
                                       'Ethel the Frog')
        self.assertEqual('Violence', r)

    def test_decodedSubject(self):
        r = self.message.decodedSubject
        self.assertEqual('Violence', r)

    def test_decodedSubject_latin1(self):
        s = 'Je ne ecrit pas français.'
        subj = Header(s.encode('latin-1'), 'latin-1').encode()
        self.message.message.replace_header('Subject', subj)
        r = self.message.decodedSubject
        self.assertEqual(s, r)

    def test_decodedSubject_utf8(self):
        s = 'Tonight on Ethel the Frog\u2026 we look at violence'
        subj = Header(s.encode('utf-8'), 'utf-8').encode()
        self.message.message.replace_header('Subject', subj)
        r = self.message.decodedSubject
        self.assertEqual(s, r)

    def test_decodedSubject_windows1252(self):
        s = 'Désolé.'
        subj = Header(s.encode('windows-1252'), 'windows-1252').encode()
        self.message.message.replace_header('Subject', subj)
        r = self.message.decodedSubject
        self.assertEqual(s, r)

    def test_decodedSubject_utf8_ascii_latin1_windows1252(self):
        'Test a header that has multiple encodings'
        s0 = 'Tonight on Ethel the Frog\u2026'
        s1 = 'we look at violence.'
        s2 = 'Je ne ecrit pas fran\u00e7ais.'
        s3 = 'Désolé.'
        subj = Header(s0.encode('utf8'), 'utf8')
        subj.append(s1.encode('ascii'), 'ascii')
        subj.append(s2.encode('latin1'), 'latin1')
        subj.append(s3.encode('windows-1252'), 'windows-1252')
        self.message.message.replace_header('Subject', subj.encode())

        expected = s0 + s1 + s2 + s3
        r = self.message.decodedSubject
        self.assertEqual(expected, r)

    def test_subject(self):
        r = self.message.subject
        self.assertEqual('Violence', r)

    def test_subject_utf8(self):
        s = 'Tonight on Ethel the Frog\u2026 we look at violence'
        subj = Header(s.encode('utf-8'), 'utf-8')
        self.message.message.replace_header('Subject', subj.encode())

        self.assertNotEqual(self.message.message['Subject'], s)
        r = self.message.subject
        self.assertEqual(s, r)

    def test_subject_windows1252(self):
        s = 'Je ne ecrit pas fran\u00e7ais.'
        subj = Header(s.encode('Windows-1252'), 'Windows-1252')
        self.message.message.replace_header('Subject', subj.encode())

        self.assertNotEqual(self.message.message['Subject'], s)
        r = self.message.subject
        self.assertEqual(s, r)

    def test_subject_stripped(self):
        self.message.message.replace_header(
            'Subject', '[Ethel the Frog] The Violence of British Gangland')
        r = self.message.subject
        self.assertEqual('The Violence of British Gangland', r)

    def test_subject_stripped_utf8(self):
        s = 'Tonight on Ethel the Frog\u2026 we look at violence'
        fullS = '[Ethel the Frog] ' + s
        subj = Header(fullS.encode('utf-8'), 'utf-8')
        self.message.message.replace_header('Subject', subj.encode())
        r = self.message.subject
        self.assertEqual(s, r)

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

    def test_normalise_lower_whitespace_utf8(self):
        s = 'Tonight on Ethel the Frog\u2026 we look at violence'
        r = self.message.normalise_subject(s)
        self.assertEqual('tonightonethelthefrog\u2026welookatviolence', r)

    def test_compressed_subject(self):
        r = self.message.compressed_subject
        self.assertEqual('violence', r)

    def test_compressed_subject_whitespace(self):
        self.message.message.replace_header(
            'Subject', '[Ethel the Frog] The Violence of British Gangland')
        r = self.message.compressed_subject
        self.assertEqual('theviolenceofbritishgangland', r)

    def test_compressed_subject_whitespace_utf8(self):
        s = '[Ethel the Frog] Tonight on Ethel the Frog\u2026 we look at '\
            'violence'
        subj = Header(s.encode('utf-8'), 'utf-8')
        self.message.message.replace_header('Subject', subj.encode())
        r = self.message.compressed_subject
        self.assertEqual('tonightonethelthefrog\u2026welookatviolence', r)

    def test_sender(self):
        r = self.message.sender
        self.assertEqual('a.member@example.com', r)

    def test_name(self):
        r = self.message.name
        self.assertEqual('Me', r)

    def test_topic_id(self):
        r = self.message.topic_id
        # --=mpj17=-- This is fragile.
        self.assertEqual('2kxkamRQ35fmTJ6pTRK8yN', r)

    def test_topic_id_same_for_different_posts(self):
        parser = Parser()
        self.message.message = parser.parsestr(self.m + '.')
        r = self.message.topic_id
        # --=mpj17=-- This is fragile.
        self.assertEqual('2kxkamRQ35fmTJ6pTRK8yN', r)

    def test_post_id(self):
        r = self.message.post_id
        # --=mpj17=-- This is fragile.
        self.assertEqual('ZTcsX0Tw8Nww2LggPn78Y', r)

    def test_post_id_randomish(self):
        parser = Parser()
        self.message.message = parser.parsestr(self.m + '.')
        r = self.message.post_id
        # --=mpj17=-- This is fragile.
        self.assertNotEqual('68WJx41vQmeQ543Y1Y02VZ', r)

    def test_txt_file(self):
        filename = os.path.join('gs', 'group', 'list', 'base', 'tests',
                                'txt.mbox')
        parser = Parser()
        with codecs.open(filename, encoding='utf-8') as infile:
            m = parser.parse(infile)
        self.message.message = m

        r = self.message.body.strip()
        self.assertEqual('God is real, unless declared integer.', r)

    def test_txt_and_html_file(self):
        filename = os.path.join('gs', 'group', 'list', 'base', 'tests',
                                'txt-html.mbox')
        parser = Parser()
        with codecs.open(filename, encoding='utf-8') as infile:
            m = parser.parse(infile)
        self.message.message = m

        filename = os.path.join('gs', 'group', 'list', 'base', 'tests',
                                'multi-p.txt')
        with codecs.open(filename, encoding='utf-8') as infile:
            expected = infile.read().strip()[:128]
        r = self.message.body[:128]
        self.maxDiff = None
        self.assertEqual(expected, r)

        self.assertIn(expected[:8], self.message.html_body)
        self.assertIn('<HTML>', self.message.html_body)

    def test_html_file(self):
        filename = os.path.join('gs', 'group', 'list', 'base', 'tests',
                                'html.mbox')
        parser = Parser()
        with codecs.open(filename, encoding='utf-8') as infile:
            m = parser.parse(infile)
        self.message.message = m

        filename = os.path.join('gs', 'group', 'list', 'base', 'tests',
                                'multi-p.txt')
        with codecs.open(filename, encoding='utf-8') as infile:
            expected = infile.read().strip()[:64]
        r = self.message.body[:64]
        self.maxDiff = None
        self.assertEqual(expected, r)

        self.assertIn(expected[:8], self.message.html_body)
        self.assertIn('<HTML>', self.message.html_body)
