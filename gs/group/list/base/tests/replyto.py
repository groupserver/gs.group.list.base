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
from __future__ import absolute_import, unicode_literals, print_function
from mock import MagicMock
from unittest import TestCase
from gs.group.list.base.replyto import (ReplyTo, replyto)


class ReplyToTest(TestCase):

    def create_listInfo(self, setting):
        retval = MagicMock()
        retval.get_property.return_value = setting
        return retval

    def test_check_author(self):
        l = self.create_listInfo('sender')
        r = replyto(l)
        self.assertEqual(ReplyTo.author, r)

    def test_check_both(self):
        l = self.create_listInfo('both')
        r = replyto(l)
        self.assertEqual(ReplyTo.both, r)

    def test_check_default(self):
        l = self.create_listInfo(None)
        r = replyto(l)
        self.assertEqual(ReplyTo.group, r)

    def test_check_group(self):
        l = self.create_listInfo('group')
        r = replyto(l)
        self.assertEqual(ReplyTo.group, r)
