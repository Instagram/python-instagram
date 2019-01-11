#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name="instagram",
    version="1.3.4",
    description="Instagram API client",
    license="MIT",
    install_requires=[
        "simplejson",
        "httplib2",
        "six",
        "pytz",
    ],
    author="instagram, wkoot",
    author_email="pypi@rondarchief.nl",
    url="http://github.com/wkoot/python-instagram",
    packages=find_packages(),
    keywords="instagram",
    zip_safe=True
)
