#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

import setuptools

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

__author__ = "Dave Vandenbout"
__email__ = "devb@xess.com"
__version__ = "0.1.19"

if "sdist" in sys.argv[1:]:
    with open("kifield/pckg_info.py", "w") as f:
        for name in ["__version__", "__author__", "__email__"]:
            f.write("{} = '{}'\n".format(name, locals()[name]))

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read().replace(".. :changelog:", "")

requirements = [
    "future >= 0.15.0",
    "openpyxl >= 2.6.0",
    "sexpdata",
]

setup(
    name="kifield",
    version=__version__,
    description="Module and utilities for manipulating part fields in KiCad files.",
    long_description=readme + "\n\n" + history,
    author=__author__,
    author_email=__email__,
    url="https://github.com/devbisme/kifield",
    #    packages=['kifield',],
    packages=setuptools.find_packages(),
    entry_points={"console_scripts": ["kifield = kifield.__main__:main"]},
    package_dir={"kifield": "kifield"},
    include_package_data=True,
    package_data={"kifield": ["*.gif", "*.png"]},
    scripts=[],
    install_requires=requirements,
    license="MIT",
    zip_safe=False,
    keywords="kifield KiCad EDA ",
    classifiers=[
        # More information at https://pypi.org/classifiers/.
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)",
    ],
)
