"""setup.py"""
from codecs import open as codecs_open
from setuptools import setup  # type: ignore

with codecs_open("README.md", "r", "utf-8") as f:
    README = f.read()

setup(
    author="Beau Barker",
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    description="Process JSON-RPC requests",
    extras_require={
        "tox": ["tox"],
        "examples": [
            "aiohttp",
            "aiozmq",
            "flask",
            "flask-socketio",
            "gmqtt",
            "pyzmq",
            "tornado",
            "websockets",
            "werkzeug",
        ],
    },
    include_package_data=True,
    install_requires=["jsonschema<4", "oslash<1"],
    license="MIT",
    long_description=README,
    long_description_content_type="text/markdown",
    name="jsonrpcserver",
    # Be PEP 561 compliant
    # https://mypy.readthedocs.io/en/stable/installed_packages.html#making-pep-561-compatible-packages
    package_data={"jsonrpcserver": ["request-schema.json", "py.typed"]},
    zip_safe=False,
    packages=["jsonrpcserver"],
    url="https://github.com/bcb/jsonrpcserver",
    version="5.0.0rc1",
)
