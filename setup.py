"""setup.py"""
#pylint:disable=line-too-long

from setuptools import setup
from codecs import open as codecs_open

with codecs_open('README.rst', 'r', 'utf-8') as f:
    readme = f.read()

with codecs_open('HISTORY.rst', 'r', 'utf-8') as f:
    history = f.read()

setup(
    name='jsonrpcserver',
    version='2.1.1',
    description='JSON-RPC server library.',
    long_description=readme + '\n\n' + history,
    author='Beau Barker',
    author_email='beauinmelbourne@gmail.com',
    url='https://jsonrpcserver.readthedocs.org/',
    packages=['jsonrpcserver'],
    package_data={'jsonrpcserver': ['request-schema.json']},
    include_package_data=True,
    install_requires=['jsonschema', 'six', 'funcsigs'],
    tests_require=['tox']
)
