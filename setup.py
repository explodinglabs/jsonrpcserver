#!/usr/bin/env python
#pylint:disable=line-too-long
"""setup.py"""

import os

from codecs import open

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open('README.rst', 'r', 'utf-8') as f:
    readme = f.read()

with open('HISTORY.rst', 'r', 'utf-8') as f:
    history = f.read()

setup(
    name='jsonrpcserver',
    version='1.0.7',
    description='JSON-RPC 2.0 server library for Python 3.',
    long_description=readme + '\n\n' + history,
    author='Beau Barker',
    author_email='beauinmelbourne@gmail.com',
    url='http://jsonrpcserver.readthedocs.org/',
    packages=['jsonrpcserver'],
    package_data={'jsonrpcserver': ['request-schema.json']},
    include_package_data=True,
    install_requires=['flask', 'jsonschema'],
    tests_require=['nose','nose-cov','rednose','flask-testing'],
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
