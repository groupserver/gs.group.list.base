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
#from mock import patch
import os
from unittest import TestCase
from gs.group.list.base.html2txt import (HTMLConverter, convert_to_txt,
                                         unicodeOrString)


class HTMLConverterTest(TestCase):
    def setUp(self):
        self.converter = HTMLConverter()

    def test_simple(self):
        html = '''<p>Tonight on Ethel the Frog we look at violence.</p>'''
        self.converter.feed(html)
        self.converter.close()

        expected = 'Tonight on Ethel the Frog we look at violence.'
        r = unicodeOrString(self.converter)
        self.assertEqual(expected, r)

    def test_simple_charref(self):
        html = '<p>Tonight on Ethel the Frog&#8230; we look at '\
               'violence.</p>'
        self.converter.feed(html)
        self.converter.close()

        expected = 'Tonight on Ethel the Frog\u2026 we look at violence.'
        r = unicodeOrString(self.converter)
        self.assertEqual(expected, r)

    def test_simple_entityref(self):
        html = '<p>Je ne ecrit pas fran&ccedil;ais.</p>'
        self.converter.feed(html)
        self.converter.close()

        expected = 'Je ne ecrit pas français.'
        r = unicodeOrString(self.converter)
        self.assertEqual(expected, r)

    def test_broken_entityref(self):
        html = '<p>Je ne ecrit pas fran&piranha;ais.</p>'
        self.converter.feed(html)
        self.converter.close()

        expected = 'Je ne ecrit pas franais.'
        r = unicodeOrString(self.converter)
        self.assertEqual(expected, r)

    def test_not_html(self):
        notHtml = 'On Ethel the Frog tonight we look at violence.'
        self.converter.feed(notHtml)
        self.converter.close()

        r = unicodeOrString(self.converter)
        self.assertEqual(notHtml, r)

    def test_full_multi_paragraph(self):
        n = os.path.join('gs', 'group', 'list', 'base', 'tests',
                         'multi-p.html')
        with codecs.open(n, encoding='utf-8') as infile:
            html = infile.read()
        self.converter.feed(html)
        self.converter.close()
        r = unicodeOrString(self.converter)

        n = os.path.join('gs', 'group', 'list', 'base', 'tests',
                         'multi-p.txt')
        with codecs.open(n, encoding='utf-8') as infile:
            expected = infile.read().strip()
        self.assertEqual(expected, r)


class ConvertToTextTest(TestCase):
    def test_html(self):
        n = os.path.join('gs', 'group', 'list', 'base', 'tests',
                         'multi-p.html')
        with codecs.open(n, encoding='utf-8') as infile:
            html = infile.read()

        r = convert_to_txt(html)
        n = os.path.join('gs', 'group', 'list', 'base', 'tests',
                         'multi-p.txt')
        with codecs.open(n, encoding='utf-8') as infile:
            expected = infile.read().strip()
        self.assertEqual(expected, r)

    def test_not_html(self):
        notHtml = 'On Ethel the Frog tonight we look at violence.'
        r = convert_to_txt(notHtml)
        self.assertEqual(notHtml, r)

    def test_fail(self):
        with self.assertRaises(ValueError):
            convert_to_txt(None)
