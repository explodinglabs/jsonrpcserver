import os
import sys
import datetime

# -- Path setup --------------------------------------------------------------

sys.path.insert(0, os.path.abspath('..'))

# -- Project information -----------------------------------------------------

project = 'jsonrpcserver'
author = 'Exploding Labs'
copyright = f'{datetime.datetime.now().year}, {author}'
release = '5.0.9'  # Or dynamically read from package metadata

# -- General configuration ---------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',  # for Google/NumPy docstrings
    'sphinx.ext.viewcode',
]

templates_path = ['_templates']
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
