"""setup.py"""

from codecs import open as codecs_open
from setuptools import setup

with codecs_open('README.rst', 'r', 'utf-8') as f:
    readme = f.read()

with codecs_open('HISTORY.rst', 'r', 'utf-8') as f:
    history = f.read()

setup(
    name='jsonrpcserver',
    version='3.3.2',
    description='Process JSON-RPC requests',
    long_description=readme + '\n\n' + history,
    author='Beau Barker',
    author_email='beauinmelbourne@gmail.com',
    url='https://jsonrpcserver.readthedocs.io/',
    license='MIT',
    packages=['jsonrpcserver'],
    package_data={'jsonrpcserver': ['request-schema.json']},
    include_package_data=True,
    install_requires=['jsonschema', 'six', 'funcsigs'],
    tests_require=['tox'],
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
