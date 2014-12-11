#!/usr/bin/env python
# pylint: disable=line-too-long
"""setup.py"""

import os
from setuptools import setup

def read(fname):
    """Get the readme from a file, to use as long_description"""
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='jsonrpcserver',
    packages=['jsonrpcserver'],
    package_data={'jsonrpcserver': ['request-schema.json']},
    install_requires=['flask', 'jsonschema'],
    version='1.0.6',
    description='JSON-RPC 2.0 server library for Python 3',
    long_description=read('README.rst'),
    author='Beau Barker',
    author_email='beauinmelbourne@gmail.com',
    url='https://bitbucket.org/beau-barker/jsonrpcserver',
    keywords=['json-rpc', 'json', 'api'],
    classifiers=[
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
