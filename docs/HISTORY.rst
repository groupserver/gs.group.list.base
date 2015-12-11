Changelog
=========

1.1.1 (2015-12-10)
------------------

* Fixing the unit-tests so the work with `zc.recipe.testrunner`_

.. _zc.recipe.testrunner:
   https://pypi.python.org/pypi/zc.recipe.testrunner

1.1.0 (2015-09-24)
------------------

* Adding the ``replyto`` function, and ``ReplyTo`` enumeration,
  moving them here from `gs.group.list.sender`_
* Updating the documentation

.. _gs.group.list.sender:
   https://github.com/groupserver/gs.group.list.sender

1.0.3 (2015-04-08)
------------------

* Improving the handling of ``Subject`` headers that contain
  ``[square brackets]``

1.0.2 (2015-02-11)
------------------

* Handling corner cases where the header lies about its encoding

1.0.1 (2015-02-10)
------------------

* Handling corner cases where the body or HTML body is ``None``

1.0.0 (2015-01-23)
------------------

Initial release. Prior to the creation of `this product`_ the
code was found in the :class:`Products.XWFMailingListManager`
product.

.. _this product:
   https://github.com/groupserver.gs.group.list.base

..  LocalWords:  Changelog XWFMailingListManager github groupserver
