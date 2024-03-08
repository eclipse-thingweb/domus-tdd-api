'''******************************************************************************
 * Copyright (c) 2018 Contributors to the Eclipse Foundation
 *
 * See the NOTICE file(s) distributed with this work for additional
 * information regarding copyright ownership.
 *
 * This program and the accompanying materials are made available under the
 * terms of the Eclipse Public License v. 2.0 which is available at
 * http://www.eclipse.org/legal/epl-2.0, or the W3C Software Notice and
 * Document License (2015-05-13) which is available at
 * https://www.w3.org/Consortium/Legal/2015/copyright-software-and-document.
 *
 * SPDX-License-Identifier: EPL-2.0 OR W3C-20150513
 ********************************************************************************'''


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
