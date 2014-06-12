from setuptools import setup, find_packages
import os

version = '0.0.1'

setup(
    name='rohit_common',
    version=version,
    description='Rohit ERPNext Extensions (Common)',
    author='Rohit Industries Ltd.',
    author_email='aditya@rigpl.com',
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=("frappe",),
)
