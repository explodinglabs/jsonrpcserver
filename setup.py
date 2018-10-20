"""setup.py"""
from codecs import open as codecs_open
from setuptools import setup

with codecs_open("README.md", "r", "utf-8") as f:
    README = f.read()

setup(
    author="Beau Barker",
    author_email="beauinmelbourne@gmail.com",
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    description="Process JSON-RPC requests",
    extras_require={
        "tox": ["tox"],
        "examples": [
            "aiohttp",
            "aiozmq",
            "flask",
            "flask-socketio",
            "pyzmq",
            "tornado",
            "websockets",
            "werkzeug",
        ],
    },
    include_package_data=True,
    install_requires=["apply_defaults<1", "jsonschema>=2,<3", "funcsigs>=1,<2"],
    license="MIT",
    long_description=README,
    long_description_content_type="text/markdown",
    name="jsonrpcserver",
    package_data={"jsonrpcserver": ["request-schema.json"]},
    packages=["jsonrpcserver"],
    url="https://github.com/bcb/jsonrpcserver",
    version="4.0.0",
)
