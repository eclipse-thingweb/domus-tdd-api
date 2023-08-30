#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name="TDD API",
    version="1.0",
    long_description=__doc__,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "Flask",
        "httpx",
        "jsonschema",
        "rdflib",
        "json-merge-patch",
        "python-configuration[toml]",
        "pyshacl",
    ],
    extras_require={
        "prod": [
            "gunicorn",
        ],
        "dev": [
            "pytest",
            "pytest-env",
            "pytest_httpx",
            "jsoncomparison",
            "pytz",
            "black",
            "flake8",
            "requests",
        ],
    },
)
