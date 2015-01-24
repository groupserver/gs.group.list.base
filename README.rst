======================
``gs.group.list.base``
======================
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Base code for the GroupServer mailing-list functionality
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Author: `Michael JasonSmith`_
:Contact: Michael JasonSmith <mpj17@onlinegroups.net>
:Date: 2015-01-23
:Organization: `GroupServer.org`_
:Copyright: This document is licensed under a
  `Creative Commons Attribution-Share Alike 4.0 International License`_
  by `OnlineGroups.net`_.

..  _Creative Commons Attribution-Share Alike 4.0 International License:
    http://creativecommons.org/licenses/by-sa/4.0/

Introduction
============

This product supplies the code common to all the list-products.
A surprisingly large amount of GroupServer_ functionality has
absolutely nothing to do with what people normally consider core
mailing-list functionality. However, the ``gs.group.list.*``
products do.

The main class supplied this product is the ``EmailMessage``
class. This takes an email message, with its lies about character
encodings, and produces a message with a Unicode plain-text body,
a Unicode HTML-formatted body (if present) and some headers in
Unicode.

Resources
=========

- Documentation: http://groupserver.readthedocs.org/projects/gsgrouplistbase/
- Code repository: https://github.com/groupserver/gs.group.list.base
- Questions and comments to http://groupserver.org/groups/development
- Report bugs at https://redmine.iopen.net/projects/groupserver

.. _GroupServer: http://groupserver.org/
.. _GroupServer.org: http://groupserver.org/
.. _OnlineGroups.Net: https://onlinegroups.net
.. _Michael JasonSmith: http://groupserver.org/p/mpj17
