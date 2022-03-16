# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# sys.path.insert(0, os.path.abspath('.'))
import os
import sys

sys.path.insert(0, os.path.abspath("../.."))
import metaDMG

# -- Project information -----------------------------------------------------

project = "metaDMG"
copyright = "2022, Christian Michelsen"
author = "Christian Michelsen"


# The full version, including alpha/beta/rc tags
release = version = metaDMG.__version__


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx_rtd_theme",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.githubpages",
    "sphinx_click.ext",
    "sphinx_autodoc_typehints",
    "sphinx_copybutton",
    "myst_parser",  # to read markdown files
    "autodocsumm",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
# html_theme = "sphinx_rtd_theme"
# html_theme = "furo"

# sphinx_book_theme options

html_theme = "sphinx_book_theme"

html_theme_options = {
    "repository_url": "https://github.com/metaDMG/metaDMG",
    "use_repository_button": True,
    # "logo_only": True,
    "home_page_in_toc": True,
    "show_navbar_depth": 2,  # left sidebar
    # "toc_title": "Content:", # right sidebar
    "show_toc_level": 1,
}

# html_logo = "path/to/myimage.png"
html_title = "metaDMG"

html_permalinks_icon = "¶"


# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ["_static"]
# html_css_files = ["custom.css"]


source_suffix = [".rst", ".md", ".ipynb"]

master_doc = "index"

myst_enable_extensions = [
    "dollarmath",
    "amsmath",
]

autodoc_default_options = {
    "autosummary": True,
}
