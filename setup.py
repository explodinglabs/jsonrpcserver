#!/usr/bin/env python
"""setup.py"""

from distutils.core import setup

setup(
    name = 'jsonrpcserver',
    packages = ['jsonrpcserver'],
    package_data={'jsonrpcserver': ['request-schema.json']},
    install_requires = ['jsonschema', 'flask'],
    version = '0.01',
    description = 'JSON-RPC 2.0 server library',
    author = 'Beau Barker',
    author_email = 'beauinmelbourne@gmail.com',
    url = 'https://bitbucket.org/beau-barker/jsonrpcserver',
    keywords = ['json-rpc', 'json', 'api'],
    classifiers = [
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Development Status :: 4 - Beta',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
    )
