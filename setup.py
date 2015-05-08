"""setup.py"""
#pylint:disable=line-too-long

from codecs import open as codecs_open

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup #pylint:disable=import-error,no-name-in-module

with codecs_open('README.rst', 'r', 'utf-8') as f:
    readme = f.read()

with codecs_open('HISTORY.rst', 'r', 'utf-8') as f:
    history = f.read()

setup(
    name='jsonrpcserver',
    version='2.0.1',
    description='JSON-RPC server library.',
    long_description=readme + '\n\n' + history,
    author='Beau Barker',
    author_email='beauinmelbourne@gmail.com',
    url='https://jsonrpcserver.readthedocs.org/',
    packages=['jsonrpcserver'],
    package_data={'jsonrpcserver': ['request-schema.json']},
    include_package_data=True,
    install_requires=['jsonschema'],
    tests_require=['tox'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Operating System :: OS Independent'
        ],
    )
