__author__ = 'user'

from distutils.core import setup
from pkg_resources import Requirement, resource_filename
from setuptools import setup, find_packages

setup(name='autospot',
    version='1.0',
    py_modules=['AutoSpot', 'AutoSpotB', 'AutoSpotC'],
    #packages = find_packages(),
    #package_data = {'': ['*.txt'],},
    data_files=[('/', ['settings_editthis'])],
    author='Patrik Hermansson',
    author_email='patrik@paheco.nu',
    url='https://github.com/bphermansson/AutoSpot/',
    install_requires=['pyspotify >= 2.0.0b4'],
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Environment :: Console :: Curses",
        "Intended Audience :: End Users/Desktop",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 2 :: Only",
        "Topic :: Music"        
    ],
    
)
