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
from enum import Enum
'''Replies to a message from a list can go to one of three places: the author,
the group, or both. This module provides both the :func:`replyto` function for
determining the reply-to setting, and the :class:`ReplyTo` enumeration for
representing it.

:todo: Move the mailing-list info to this product and add reply-to to it.'''


class ReplyTo(Enum):
    '''An enumeration of the different reply-to settings.'''
    # __order__ is only needed in 2.x
    __order__ = 'author group both'

    #: The replies go to the author
    author = 0

    #: The replies go to the group
    group = 1

    #: The replies go to the author and the group
    both = 2


def replyto(listInfo):
    '''Get the reply-to setting for a list

:param listInfo: The list to examine for the reply-to
:type listInfo: :class:`Products.GSGroup.interfaces.IGSMailingListInfo`
:returns: The reply-to setting for the group, defaulting to :attr:`ReplyTo.group`
:rtype: A member of the :class:`ReplyTo` enumeration.'''
    r = listInfo.get_property('replyto', 'group')
    if r == 'sender':
        retval = ReplyTo.author
    elif r == 'both':
        retval = ReplyTo.both
    else:
        retval = ReplyTo.group
    return retval
