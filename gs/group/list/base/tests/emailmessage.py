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
from email.mime.text import MIMEText
from email.parser import Parser
try:
    from email.parser import BytesParser
except ImportError:  # Python 2
    from email.parser import Parser as BytesParser
from email.utils import formataddr
import os
from pkg_resources import resource_filename
import sys
from unittest import TestCase
from gs.group.list.base.emailmessage import EmailMessage


class EmailMessageTest(TestCase):
    m = '''From: Me <a.member@example.com>
To: Group <group@groups.example.com>
Subject: Violence

Tonight on Ethel the Frog we look at violence.\n'''

    pngMagicNumber = b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A'
    jpegMagicNumber = b'\xFF\xD8'
    simpleEmailExpected = 'Je ne ecrit pas français.\n'

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

        if (sys.version_info < (3, )):
            expected = 'iso8859-1'
        else:  # Python 3
            expected = 'latin1'
        r = self.message.encoding
        self.assertEqual(expected, r)

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
        expected = self.m.split('\n\n')[1]
        self.assertEqual(expected, r[0]['payload'].decode('utf-8'))

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
        self.assertEqual(bodyText.get_payload(),
                         r[0]['payload'].decode('utf-8'))
        self.assertEqual('text/plain', r[1]['mimetype'])
        self.assertEqual(textAttachment.get_payload(),
                         r[1]['payload'].decode('utf-8'))

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

    def test_null_body(self):
        'Sometimes the body is null'
        rv = {'payload': None, 'filename': '', 'subtype': 'text'}
        self.message.attachments = [rv]
        r = self.message.body
        self.assertEqual('', r)

    def test_null_charset(self):
        'Sometimes the charset is null'
        rv = {'payload': b'Violence', 'filename': '', 'subtype': 'text',
              'charset': None}
        self.message.attachments = [rv]
        r = self.message.body
        self.assertEqual('Violence', r)

    def test_null_html_body(self):
        'Sometimes the HTML body is null'
        rv = {'payload': None, 'filename': '', 'subtype': 'html'}
        self.message.attachments = [rv]
        r = self.message.html_body
        self.assertEqual('', r)

    def test_null_html_charset(self):
        'Sometimes the charset is null'
        rv = {'payload': b'Violence', 'filename': '', 'subtype': 'html',
              'charset': None}
        self.message.attachments = [rv]
        r = self.message.html_body
        self.assertEqual('Violence', r)

    def test_strip_bracket_none(self):
        'Ensure the string is unaltered if there are no brackets'
        e = 'The Violence of British Gangland'
        r = self.message.strip_bracket(e)
        self.assertEqual(e, r)

    def test_strip_bracket(self):
        'Ensure the brackets are stripped from the start and end'
        e = 'The Violence of British Gangland'
        r = self.message.strip_bracket('[' + e + ']')
        self.assertEqual(e, r)

    def test_strip_bracket_start(self):
        'Ensure that brackets at the start are left as-is'
        e = '[Ethel the Frog] The Violence of British Gangland'
        r = self.message.strip_bracket(e)
        self.assertEqual(e, r)

    def test_strip_bracket_end(self):
        'Test the brackets at the end are left as-is'
        e = 'The Violence of British Gangland [Ethel the Frog]'
        r = self.message.strip_bracket(e)
        self.assertEqual(e, r)

    def test_strip_bracket_middle(self):
        'Test the brackets in the middle are left as-is'
        e = 'The Violence of [Ethel the Frog] British Gangland'
        r = self.message.strip_bracket(e)
        self.assertEqual(e, r)

    def test_strip_list_title(self):
        'Test that the list name is stripped from the subject'
        e = 'The Violence of British Gangland'
        gn = 'Ethel the Frog'
        r = self.message.strip_list_title('[{0}] {1}'.format(gn, e), gn)
        self.assertEqual(e, r)

    def test_strip_list_title_other(self):
        e = 'The Violence of British Gangland'
        gn = 'Ethel the Frog'
        odd = '[Cheese Shop] {0}'.format(e)
        r = self.message.strip_list_title(odd, gn)
        self.assertEqual(odd, r)

    def test_strip_list_title_end(self):
        e = 'The Violence of British Gangland'
        gn = 'Ethel the Frog'
        odd = '{1} [{0}]'.format(e, gn)
        r = self.message.strip_list_title(odd, gn)
        self.assertEqual(odd, r)

    def test_strip_re_fwd_none(self):
        'Ensure that we only strip Re: and Fwd if they are there'
        e = 'The Violence of British Gangland'
        r = self.message.strip_re_fwd(e)
        self.assertEqual(e, r)

    def test_strip_re_fwd_re(self):
        'Ensure we strip "Re:"'
        e = 'The Violence of British Gangland'
        o = 'Re: {0}'.format(e)
        r = self.message.strip_re_fwd(o)
        self.assertEqual(e, r)

    def test_strip_re_fwd_RE(self):
        'Ensure we strip "RE:" (ignore case)'
        e = 'The Violence of British Gangland'
        o = 'RE: {0}'.format(e)
        r = self.message.strip_re_fwd(o)
        self.assertEqual(e, r)

    def test_strip_re_fwd_fw(self):
        'Ensure we strip "Fw:"'
        e = 'The Violence of British Gangland'
        o = 'Fw: {0}'.format(e)
        r = self.message.strip_re_fwd(o)
        self.assertEqual(e, r)

    def test_strip_re_fwd_fwd(self):
        'Ensure we strip "Fwd:"'
        e = 'The Violence of British Gangland'
        o = 'Fwd: {0}'.format(e)
        r = self.message.strip_re_fwd(o)
        self.assertEqual(e, r)

    def test_strip_re_fwd_FWD(self):
        'Ensure we strip "FWD:"'
        e = 'The Violence of British Gangland'
        o = 'Fwd: {0}'.format(e)
        r = self.message.strip_re_fwd(o)
        self.assertEqual(e, r)

    def test_strip_subject(self):
        'Ensure that a normal subject is left unaltered'
        e = 'The Violence of British Gangland'
        r = self.message.strip_subject(e, 'Ethel the Frog')
        self.assertEqual(e, r)

    def test_strip_subject_group(self):
        'Test that the group name is stripped from the subject'
        r = self.message.strip_subject('[Ethel the Frog] Violence',
                                       'Ethel the Frog')
        self.assertEqual('Violence', r)

    def test_subject_stripped_other(self):
        'Ensure that the name of another group is not stripped'
        e = '[Cheese Shop] Violence'
        r = self.message.strip_subject(e, 'Ethel the Frog')
        self.assertEqual(e, r)

    def test_strip_subject_missing(self):
        r = self.message.strip_subject('', 'Ethel the Frog')
        self.assertEqual('No subject', r)

    def test_strip_subject_re(self):
        r = self.message.strip_subject('Re: [Ethel the Frog] Violence',
                                       'Ethel the Frog')
        self.assertEqual('Violence', r)

    def test_strip_subject_fwd_bracket(self):
        r = self.message.strip_subject('[Fwd: Violence]',
                                       'Ethel the Frog')
        self.assertEqual('Violence', r)

    def test_decode_header_value_tuple_none(self):
        s = 'Tonight on Ethel the Frog'
        r = self.message.decode_header_value_tuple((s.encode('utf-8'),
                                                    None))
        self.assertEqual(s, r)

    def test_decode_header_value_tuple_utf8(self):
        s = 'Tonight on Ethel the Frog'
        r = self.message.decode_header_value_tuple((s.encode('utf-8'),
                                                    'utf-8'))
        self.assertEqual(s, r)

    def test_decode_header_value_tuple_latin1(self):
        s = 'Je ne ecrit pas français.'
        r = self.message.decode_header_value_tuple((s.encode('latin1'),
                                                    'latin-1'))
        self.assertEqual(s, r)

    def test_decode_header_value_tuple_lies(self):
        'Ensure that we do something sane when lied to'
        s = 'Je ne ecrit pas français.'
        r = self.message.decode_header_value_tuple((s.encode('latin1'),
                                                    'utf-8'))
        expected = s.encode('ascii', 'ignore').decode('ascii')
        self.assertEqual(expected, r)

    def test_get(self):
        r = self.message.get('subject')
        self.assertEqual('Violence', r)

    def test_get_latin1(self):
        s = 'Je ne ecrit pas français.'
        subj = Header(s.encode('latin-1'), 'latin-1').encode()
        self.message.message.replace_header('Subject', subj)
        r = self.message.get('Subject')
        self.assertEqual(s, r)

    def test_get_utf8(self):
        s = 'Tonight on Ethel the Frog\u2026 we look at violence'
        subj = Header(s.encode('utf-8'), 'utf-8').encode()
        self.message.message.replace_header('Subject', subj)
        r = self.message.get('Subject')
        self.assertEqual(s, r)

    def test_get_windows1252(self):
        s = 'Désolé.'
        subj = Header(s.encode('windows-1252'), 'windows-1252').encode()
        self.message.message.replace_header('Subject', subj)
        r = self.message.get('Subject')
        self.assertEqual(s, r)

    def test_get_utf8_ascii_latin1_windows1252(self):
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

        # --=mpj17=-- There is a difference in behaviour between the
        # Python 2 email.header product, and the Python 3 product. The main
        # thing is we get some semblence of the header back.
        if (sys.version_info < (3, )):
            expected = ' '.join([s0, s1, s2, s3])
        else:  # Python 3
            expected = ' '.join([s0, '', s1, s2, s3])
        r = self.message.get('Subject')
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
        'Ensure we strip the name of the group from the subject'
        self.message.message.replace_header(
            'Subject', '[Ethel the Frog] The Violence of British Gangland')
        r = self.message.subject
        self.assertEqual('The Violence of British Gangland', r)

    def test_subject_stripped_utf8(self):
        'Ensure we strip the group name from UTF-8 encoded subjects'
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

    def test_i18n_name(self):
        name = "L'étrange"
        encodedName = str(Header(name, 'utf-8'))
        email = 'member@example.com'
        addr = formataddr((encodedName, email))
        self.message.message.replace_header('From', addr)

        r = self.message.name
        self.assertEqual(name, r)

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

    @staticmethod
    def load_email(filename):
        '''A useful functioning for loading a sample email file'''
        testname = os.path.join('tests', 'emails', filename)
        fullFileName = resource_filename('gs.group.list.base', testname)
        # --=mpj17=-- Because the file may contain UTF-8 or ISO 8859-1 in
        # full eight-bit glory the file is opened in **binary** mode, and
        # the BytesParser class is used to parse and decode the message.
        # Python 2.7 lacks a BytesParser, but the Parser class has been
        # imported with an alias.
        parser = BytesParser()
        with open(fullFileName, 'rb') as infile:
            retval = parser.parse(infile)
        return retval

    def test_txt_file(self):
        m = self.load_email('txt.eml')
        self.message.message = m

        r = self.message.body.strip()
        self.assertEqual('God is real, unless declared integer.', r)

    def test_txt_and_html_file(self):
        m = self.load_email('txt-html.eml')
        self.message.message = m

        testname = os.path.join('tests', 'multi-p.txt')
        filename = resource_filename('gs.group.list.base', testname)
        with codecs.open(filename, encoding='utf-8') as infile:
            expected = infile.read().strip()[:128]
        r = self.message.body[:128]
        self.maxDiff = None
        self.assertEqual(expected, r)

        self.assertIn(expected[:8], self.message.html_body)
        self.assertIn('<HTML>', self.message.html_body)

    def test_html_file(self):
        m = self.load_email('html.eml')
        self.message.message = m

        testname = os.path.join('tests', 'multi-p.txt')
        filename = resource_filename('gs.group.list.base', testname)
        with codecs.open(filename, encoding='utf-8') as infile:
            expected = infile.read().strip()[:64]
        r = self.message.body[:64]
        self.maxDiff = None
        self.assertEqual(expected, r)

        self.assertIn(expected[:8], self.message.html_body)
        self.assertIn('<HTML>', self.message.html_body)

    def test_html_latin1_7bit_utf8_borken(self):
        '''Test a message with just an HTML body, that lies about its
encoding'''
        m = self.load_email('html-latin1-7bit_utf8_borken.eml')
        self.message.message = m

        self.assertIn('<HTML>', self.message.html_body)
        expected = self.simpleEmailExpected.replace('ç', '').strip()
        self.assertEqual(expected, self.message.body.strip())

    # Real World stress tests follow

    def test_apple_mail(self):
        m = self.load_email('apple-mail.eml')
        self.message.message = m

        self.assertEqual('Test AppleMail email with photo attached',
                         self.message.subject)
        self.assertIn('Photo attached.', self.message.body)
        self.assertIn('webkit', self.message.html_body)
        image = [a for a in self.message.attachments
                 if a['filename']][0]
        self.assertEqual(self.jpegMagicNumber, image['payload'][:2])

    def test_txt_base64_attachments(self):
        'Ensure the base64 encoded text attachments is decoded correctly.'
        m = self.load_email('base64attachments.eml')
        self.message.message = m

        self.assertNotIn('Reporting-MTA: dns;', m.as_string())
        f = [f for f in self.message.attachments
             if f['filename'] == 'Delivery report.txt'][0]
        # Because some fool marked the attachment down as an octet-stream
        # there is no charset. So guess it.
        self.assertEqual('application/octet-stream', f['mimetype'])
        attachmentContent = f['payload'].decode('utf-8')
        self.assertIn('Reporting-MTA: dns;', attachmentContent)
        self.assertNotIn('UmVwb3J0aW5nLU1UQTog', attachmentContent)

    def test_attachments_with_utf8_filenames(self):
        m = self.load_email('attachments_with_utf8-filenames.eml')
        self.message.message = m

        filenames = [f['filename'] for f in self.message.attachments
                     if f['filename']]
        self.assertEqual(3, len(filenames))
        # The actual names could get munged, because they are invalid, so
        # just check the extensions.
        extns = sorted([f[-3:] for f in filenames])
        self.assertEqual(['jpg', 'svg', 'txt'], extns)

    def test_base64(self):
        m = self.load_email('base64.eml')
        self.message.message = m
        self.assertNotIn('SSBhZ3JlZSB3aXRoI', self.message.body)
        self.assertIn('I agree with you.', self.message.body)

    def test_google_gmail(self):
        m = self.load_email('google-gmail-img.eml')
        self.message.message = m
        self.assertEqual('Very strange...', self.message.subject)
        self.assertIn('Why does this happen', self.message.body)
        self.assertIn('gmail_signature', self.message.html_body)

        # Check the image
        f = [f for f in self.message.attachments
             if f['filename']][0]
        self.assertEqual('image/png', f['mimetype'])
        if (sys.version_info < (3, )):
            self.assertEqual(str, type(f['payload']))
        else:
            self.assertEqual(bytes, type(f['payload']))
        self.assertNotEqual(b'iVBORw0K', f['payload'][:8])
        self.assertEqual(self.pngMagicNumber, f['payload'][:8])

    def test_ibm_notes(self):
        m = self.load_email('ibm-notes.eml')
        self.message.message = m

        self.assertEqual('Email bounced', self.message.subject)
        self.assertIn('Hello Support,', self.message.body)
        self.assertIn('<font', self.message.html_body)

    def test_internationalistation(self):
        m = self.load_email('internationalization.eml')
        self.message.message = m
        expected = '\u0049\u00f1\u0074\u00eb\u0072\u006e\u00e2\u0074\u0069'\
                   '\u00f4\u006e\u00e0\u006c\u0069\u007a\u00e6\u0074\u0069'\
                   '\u00f8\u006e'
        self.assertIn(expected, self.message.subject)
        self.assertIn(expected, self.message.body)

    def test_k9(self):
        m = self.load_email('k9.eml')
        self.message.message = m

        self.assertEqual('GroupServer 14.11', self.message.subject)
        self.assertIn('Awesome', self.message.body)
        self.assertIn('Awesome', self.message.html_body)

    def test_k9_jpeg(self):
        m = self.load_email('k9-jpeg.eml')
        self.message.message = m

        self.assertEqual('File links message preview screenshot',
                         self.message.subject)
        self.assertIn('K-9 Mail', self.message.body)
        self.assertEqual('', self.message.html_body)
        attachments = [a for a in self.message.attachments
                       if a['filename']]
        self.assertEqual(1, len(attachments))
        self.assertEqual(self.jpegMagicNumber,
                         attachments[0]['payload'][:2])

    def test_ms_outlook(self):
        m = self.load_email('ms-outlook-01.eml')
        self.message.message = m

        expectedS = 'Order your Entertainment Book now and support '\
                    'the Obscured Foundation of New Zealand (SG)'
        self.assertEqual(expectedS, self.message.subject)
        # Quoted-printable check
        self.assertTrue(self.message.body)
        self.assertNotIn('=20', self.message.body)
        self.assertTrue(self.message.html_body)
        self.assertNotIn('=20', self.message.html_body)

        self.assertEqual(7, len(self.message.attachments))
        fileAttachments = [f for f in self.message.attachments
                           if f['filename']]
        self.assertEqual(3, len(fileAttachments))
        for f in fileAttachments:
            if f['mimetype'] == 'image/jpeg':
                m = 'Magic number issue for {0}'
                self.assertEqual(self.jpegMagicNumber, f['payload'][:2],
                                 m.format(f['filename']))

    def test_simple1(self):
        m = self.load_email('simple1.eml')
        self.message.message = m

        self.assertEqual('testing 7', self.message.subject)
        expected = 'testing testing testing'
        self.assertEqual(expected, self.message.body.strip())

    def test_simple2(self):
        m = self.load_email('simple2.eml')
        self.message.message = m

        self.assertEqual('TesTing 7', self.message.subject)
        expected = 'testing testing testing'
        self.assertEqual(expected, self.message.body.strip())

    def test_simple_latin1_base64(self):
        m = self.load_email('simple-latin1-base64.eml')
        self.message.message = m

        self.assertEqual(self.simpleEmailExpected, self.message.body)

    def test_simple_latin1_qp(self):
        m = self.load_email('simple-latin1-qp.eml')
        self.message.message = m

        self.assertEqual(self.simpleEmailExpected, self.message.body)

    def test_simple_latin1_8bit(self):
        m = self.load_email('simple-latin1-8bit.eml')
        self.message.message = m

        self.assertEqual(self.simpleEmailExpected, self.message.body)

    def test_simple_latin1_7bit_borken(self):
        '''Check that an 8bit ISO 8859-1 email can be read, even if it
claims that it is 7bit'''
        m = self.load_email('simple-latin1-7bit_borken.eml')
        self.message.message = m

        self.assertEqual(self.simpleEmailExpected, self.message.body)

    def test_simple_latin1_7bit_utf8_borken(self):
        '''Check that an 8bit ISO 8859-1 email can be read, even if it
claims that it is 7bit and UTF-8'''
        m = self.load_email('simple-latin1-7bit_utf8_borken.eml')
        self.message.message = m

        expected = self.simpleEmailExpected.replace('ç', '')
        self.assertEqual(expected, self.message.body)

    def test_simple_utf8_base64(self):
        m = self.load_email('simple-utf8-base64.eml')
        self.message.message = m

        self.assertEqual(self.simpleEmailExpected, self.message.body)

    def test_simple_utf8_qp(self):
        m = self.load_email('simple-utf8-qp.eml')
        self.message.message = m

        self.assertEqual(self.simpleEmailExpected, self.message.body)

    def test_simple_utf8_8bit(self):
        m = self.load_email('simple-utf8-8bit.eml')
        self.message.message = m

        self.assertEqual(self.simpleEmailExpected, self.message.body)

    def test_simple_utf8_7bit_borken(self):
        '''Check that an 8bit UTF-8 email can be read, even if it claims
that it is 7bit'''
        m = self.load_email('simple-utf8-7bit_borken.eml')
        self.message.message = m

        self.assertEqual(self.simpleEmailExpected, self.message.body)

    def test_simple_ascii_7bit(self):
        m = self.load_email('simple-ascii-7bit.eml')
        self.message.message = m

        expected = 'I do not write English.\n'
        self.assertEqual(expected, self.message.body)

    def test_withattachments(self):
        m = self.load_email('withattachments.eml')
        self.message.message = m

        self.assertEqual('testing attachments', self.message.subject)
        attachments = [a for a in self.message.attachments
                       if a['filename']]
        self.assertEqual(3, len(attachments))
        for a in attachments:
            self.assertEqual(self.pngMagicNumber, a['payload'][:8],
                             '{0} is not a PNG'.format(a['filename']))
