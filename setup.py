__author__ = 'user'

from distutils.core import setup
from pkg_resources import Requirement, resource_filename
from setuptools import setup, find_packages

setup(name='autospot',
    version='1.0',
    py_modules=['AutoSpot', 'AutoSpotB'],
    #packages = find_packages(),
    #package_data = {'': ['*.txt'],},
    data_files=[('/', ['settings_editthis'])],
    author='Patrik Hermansson',
    author_email='patrik@paheco.nu',
    url='https://github.com/bphermansson/AutoSpot/',
    install_requires=['pyspotify >= 2.0.0b4']
    Programming Language :: Python :: 2 :: Only
)