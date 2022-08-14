# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import ast
import re

from setuptools import find_packages, setup

# get version from __version__ variable in rohit_common/__init__.py
_version_re = re.compile(r"__version__\s+=\s+(.*)")

with open("requirements.txt") as f:
    install_requires = f.read().strip().split("\n")

with open("rohit_common/__init__.py", "rb") as f:
    version = str(ast.literal_eval(
        _version_re.search(f.read().decode("utf-8")).group(1)))

setup(
    name='rohit_common',
    version=version,
    description='Rohit ERPNext Extensions (Common)',
    author='Rohit Industries Group Pvt Ltd.',
    author_email='aditya@rigpl.com',
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires,
)
