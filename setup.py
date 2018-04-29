"""setup.py"""
from codecs import open as codecs_open
from setuptools import setup

with codecs_open('README.md', 'r', 'utf-8') as f:
    README = f.read()
with codecs_open('HISTORY.md', 'r', 'utf-8') as f:
    HISTORY = f.read()

setup(
    author='Beau Barker',
    author_email='beauinmelbourne@gmail.com',
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ],
    description='Process JSON-RPC requests',
    extras_require={
        'tox': ['tox'],
        'examples': [
            'aiohttp',
            'aiozmq',
            'flask',
            'flask-socketio',
            'pyzmq',
            'tornado',
            'websockets',
            'werkzeug',
        ]
    },
    include_package_data=True,
    install_requires=['jsonschema', 'six', 'funcsigs'],
    license='MIT',
    long_description=README + '\n\n' + HISTORY,
    long_description_content_type='text/markdown',
    name='jsonrpcserver',
    package_data={'jsonrpcserver': ['request-schema.json']},
    packages=['jsonrpcserver'],
    url='https://github.com/bcb/jsonrpcserver',
    version='3.5.4'
)
