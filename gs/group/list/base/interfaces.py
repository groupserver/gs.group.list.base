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
from zope.interface import Interface, Attribute


class IEmailMessage(Interface):
    """ A representation of an email message.

    """
    post_id = Attribute("The unique ID for the post, based on attributes "
                        "of the message")
    topic_id = Attribute("The unique ID for the topic, based on attributes "
                         "of the message")

    encoding = Attribute("The encoding of the email and headers.")
    attachments = Attribute(
        "A list of attachment payloads, each structured as a dictionary, "
        "from the email (both body and attachments).")
    body = Attribute("The plain text body of the email message.")
    html_body = Attribute("The html body of the email message, if one "
                          "exists")
    subject = Attribute("Get the subject of the email message, stripped of "
                        "additional details (such as re:, and list title)")
    compressed_subject = Attribute(
        "Get the compressed subject of the email message, with all "
        "whitespace removed.")

    sender_id = Attribute("The user ID of the message sender")
    headers = Attribute("A flattened version of the email headers")
    language = Attribute(
        "The language in which the email has been composed")
    inreplyto = Attribute("The value of the inreplyto header if it exists")
    date = Attribute("The date on which the email was sent")
    md5_body = Attribute(
        "An md5 checksum of the plain text body of the email")

    to = Attribute("The email address the message was sent to")
    sender = Attribute("The email address the message was sent from")
    name = Attribute("The name of the sender, from the header. This is not "
                     "related to their name as set in GroupServer")
    title = Attribute("An attempt at a title for the email")
    tags = Attribute("A list of tags that describe the email")

    attachment_count = Attribute("A count of attachments which have a"
                                 "filename")

    def get(name, default):
        """ Get the value of a header, changed to unicode using the
            encoding of the email.

        @param name: identifier of header, eg. 'subject'
        @param default: default value, if header does not exist. Defaults to
            '' if left unspecified
        """
