HTML to Text
=============

 .. currentmodule:: gs.group.list.base.html2txt
 .. default-domain:: py

The :class:`gs.group.list.base.html2txt.HTMLConverter` class is a
subclass of :class:`HTMLParser.HTMLParser` (or
:class:`html.parser.HTMLParser` in Python 3) that produces a
plain-text version of a HTML documents. It is fairly simple,
returning a Unicode version of the HTML, and it is used in the
rare case that a plain-text body is absent from an email message.

The :func:`convert_to_txt` function is a wrapper for convenience.

.. autofunction:: convert_to_txt

Example
-------

.. code-block:: py

   >>> from gs.group.list.base.html2txt import HTMLConverter
   >>> converter = HTMLConverter()
   >>> html = '<p>Je ne ecrit pas fran&ccedil;ais.</p>'
   >>> converter.feed(html)
   >>> converter.close()
   >>> print(converter)
   Je ne ecrit pas français.
