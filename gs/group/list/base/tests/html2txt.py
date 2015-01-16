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
from gs.group.list.base.html2txt import HTMLConverter


class HTMLConverterTest(TestCase):
    def setUp(self):
        self.converter = HTMLConverter()

    def test_simple(self):
        html = '''<p>Tonight on Ethyl the Frog we look at violence.</p>'''
        self.converter.feed(html)
        self.converter.close()

        expected = 'Tonight on Ethyl the Frog we look at violence.'
        r = unicode(self.converter)
        self.assertEqual(expected, r)

    def test_simple_charref(self):
        html = '<p>Tonight on Ethyl the Frog&#8230; we look at '\
               'violence.</p>'
        self.converter.feed(html)
        self.converter.close()

        expected = 'Tonight on Ethyl the Frog\u2026 we look at violence.'
        r = unicode(self.converter)
        self.assertEqual(expected, r)

    def test_simple_entityref(self):
        html = '<p>Je ne ecrit pas fran&ccedil;ais.</p>'
        self.converter.feed(html)
        self.converter.close()

        expected = 'Je ne ecrit pas français.'
        r = unicode(self.converter)
        self.assertEqual(expected, r)

    def test_broken_entityref(self):
        html = '<p>Je ne ecrit pas fran&piranha;ais.</p>'
        self.converter.feed(html)
        self.converter.close()

        expected = 'Je ne ecrit pas franais.'
        r = unicode(self.converter)
        self.assertEqual(expected, r)

class ConvertToTextTest(TestCase):
    def setUp(self):
        pass

    def test_nothing(self):
        self.assertTrue(True)
