Email message
=============

 .. currentmodule:: gs.group.list.base
 .. default-domain:: py

The :class:`EmailMessage` class represents an email message that
is being added to a group. It takes an email message, with its
lies about character encodings, and produces a message with a
Unicode plain-text body, a Unicode HTML-formatted body (if
present) and some headers in Unicode. (Most of the attributes of
the :class:`EmailMessage` are methods decorated with the
:func:`zope.cachedescriptors.property.Lazy` decorator.)

.. class:: EmailMessage(messageString, list_title='', group_id='', site_id='', sender_id_cb=None)

   An email message with Unicode knowledge

   :param str messageString: The email message.
   :param str listTitle: The name of the group.
   :param str group_id: The identifier for the group.
   :param str site_id: The identifier for the site that contains
                       the group.
   :param function sender_id_cb: The function to call to get the
                              identifier of the message author
                              from an email address.

   The standard Python :class:`email.message.Message` class is
   great. Really. Use it. About the only thing it lacks is some
   nouse about GroupServer groups, and it does not provide
   Unicode versions of the headers by default.

   .. attribute:: message

      :rtype: :class:`email.message.Message`

      The parsed version of the ``messageString``.

   .. attribute:: encoding

      :rtype: unicode

      The encoding of the message, or ``utf-8`` if the encoding is
      lies.

   .. attribute:: attachments
      
      The files attached to the message, **including** the HTML
      and plain-text bodies, but **excluding** those that lack
      filenames. 

      The attachments are represented as dictionaries with the
      following values.

      ``payload``: 

        The content of the attachment, decoded (based on the
        :mailheader:`Content-Transfer-Encoding`) to a sequence of
        bytes.

      ``fileid``:

        The GroupServer file identifier.

      ``filename``:
       
        The name of the file. :rfc:`2183#2.3` restricts this to
        ``ASCII``, but the value is Unicode.

      ``length``:

        The length of the file in bytes.

      ``charset``

        The character-set of the file if the major-type of the
        MIME-type of the attachment is ``text``; ``None`` for all
        other MIME types. If the attachment itself does not
        specify a character-set then the character-set for the
        overall message is returned. If the overall message does
        not specify a character-set then ``utf-8`` is returned.

      ``mimetype``:

        The MIME type of the file.

      ``maintype``:

        The main-type of the ``mimetype``.

      ``subtype``:

        The subtype of the ``mimetype``.

      ``contentid``:

        The value of the :mailheader:`Content-ID` header for the
        attachment, or an empty string if absent.

   .. attribute:: body

      :rtype: unicode

      The plain-text (:mimetype:`text/plain`) version of the
      message body, decoded into a ``unicode`` string. If absent
      (which happens sometimes) the
      :attr:`EmailMessage.html_body` is converted to plain text
      and returned.

   .. attribute:: html_body

      :rtype: unicode

      The HTML version (:mimetype:`text/html`) of the message
      body, decoded into a ``unicode`` string. If absent an empty
      string (``''``) is returned.

   .. attribute:: subject

      :rtype: unicode

      The :mailheader:`Subject` of the message, without the group
      name, and ``Re:``.

      It is common for a :mailheader:`Subject` of an email to
      contain the name of the group that the message is from, or
      is posted-to::

        Subject: [groupserver development] Email Processing Rewrite

      While useful for the recipients of the message, it is just
      noise for GroupServer.

   .. attribute:: compressed_subject

      :rtype: unicode

      The :attr:`EmailMessage.subject` without white-space, and
      transformed to lowercase, which is useful for comparisons
      (see :attr:`EmailMessage.topic_id`).

   .. attribute:: sender

      :rtype: unicode

      The email address of the person who wrote the message. This
      is actually generated from the :mailheader:`From` header,
      rather than the :mailheader:`Sender` header.

   .. attribute:: name

      :rtype: unicode

      The name of the person who wrote the message, taken from
      the :mailheader:`From` header.


   .. attribute:: topic_id

      :rtype: unicode

      The identifier of the topic that this post will belong to.

      A :attr:`topic_id` for two posts will clash if the
      :attr:`EmailMessage.compressed_subject`, group identifier,
      and site identifier are all identical.

   .. attribute:: post_id

      :rtype: unicode

      The identifier for the post, which will (almost certainly)
      be unique.

      A :attr:`post_id` for a post will clash with another post
      if

      * The :attr:`topic_id` is the same, so

        + The :attr:`compressed_subject` is the same, and
        + The group identifier is the same, and
        + The site identifier is the same, and

      * The :attr:`body` of the post is the same, and
      * The :attr:`sender` is the same author, and
      * The post is a response to the same message (the value of
        the :mailheader:`In-Reply-To` header is the same), and
      * The total length of all the attachments is the same.
