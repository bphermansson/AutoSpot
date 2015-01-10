__author__ = 'user'

from distutils.core import setup
from pkg_resources import Requirement, resource_filename
from setuptools import setup, find_packages

setup(name='autospot',
    version='1.0',
    packages = find_packages(),
    scripts = ['AutoSpot.py'],
    package_data = {

    # If any package contains *.txt or *.rst files, include them:
    '': ['*.txt'],
    },
    author='Patrik Hermansson',
    author_email='patrik@paheco.nu',
    url='https://github.com/bphermansson/AutoSpot/',
    install_requires=['pyspotify >= 2.0.0b3']
)



filename = resource_filename(Requirement.parse("autospot"),"settings_editthis")