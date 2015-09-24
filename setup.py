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
import codecs
import os
import sys
from setuptools import setup, find_packages
from version import get_version

version = get_version()

with codecs.open('README.rst', encoding='utf-8') as f:
    long_description = f.read()
with codecs.open(os.path.join("docs", "HISTORY.rst"),
                 encoding='utf-8') as f:
    long_description += '\n' + f.read()

install_requires = [
    'zope.cachedescriptors',
    'zope.interface',
    'gs.core', ]

if (sys.version_info < (3, 4)):
    install_requires += ['setuptools', 'enum34']

setup(name='gs.group.list.base',
      version=version,
      description="Base code for the mailing-list functionality",
      long_description=long_description,
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          "Environment :: Web Environment",
          "Framework :: Zope2",
          "Intended Audience :: Developers",
          'License :: OSI Approved :: Zope Public License',
          "Natural Language :: English",
          "Operating System :: POSIX :: Linux",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3.3",
          "Programming Language :: Python :: 3.4",
          "Programming Language :: Python :: Implementation :: CPython",
          "Programming Language :: Python :: Implementation :: PyPy",
          "Topic :: Software Development :: Libraries :: Python Modules",
      ],
      keywords='group, list, mailing list, email',
      author='Michael JasonSmith',
      author_email='mpj17@onlinegroups.net',
      url='https://github.com/groupserver/gs.group.list.base',
      license='ZPL 2.1',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['gs', 'gs.group', 'gs.group.list'],
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      tests_require=['mock', ],
      test_suite="gs.group.list.base.tests.test_all",
      extras_require={'docs': ['Sphinx', ], },
      entry_points="""# -*- Entry points: -*-
      """,)
