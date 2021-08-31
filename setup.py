"""setup.py"""
from setuptools import setup  # type: ignore

with open("README.md") as f:
    README = f.read()

setup(
    author="Beau Barker",
    author_email="beau@explodinglabs.com",
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    description="Process JSON-RPC requests",
    extras_require={
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
    url="https://github.com/explodinglabs/jsonrpcserver",
    version="5.0.3",
)
