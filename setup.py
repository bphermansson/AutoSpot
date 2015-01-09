__author__ = 'user'

from distutils.core import setup
setup(name='autospot',
      version='1.0',
      py_modules=['AutoSpot'],
      author='Patrik Hermansson',
      author_email='patrik@paheco.nu',
      url='https://github.com/bphermansson/AutoSpot/',
      )

install_requires=[
    'pyspotify'
]