# -*- coding: utf-8 -*-

import sys
from cx_Freeze import setup, Executable

base = None
if sys.platform == 'win32':
    base = 'Win32GUI'

options = {
    'build_exe': {
        'includes': 'atexit'
    }
}

executables = [
    Executable('qtmain.py', base=base)
]

setup(name='EncodeChanger',
      version='0.1',
      description='Change files''s encode',
      options=options,
      executables=executables
      )

