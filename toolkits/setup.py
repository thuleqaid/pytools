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
    Executable('toolkits.py', base=base)
]

setup(name='toolkits',
      version='0.1',
      description='toolkits',
      options=options,
      executables=executables
      )
