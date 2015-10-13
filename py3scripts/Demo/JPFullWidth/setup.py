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

setup(name='JPFullWidth',
      version='0.1',
      description='Change halfwidth Japanese to fullwidth',
      options=options,
      executables=executables
      )

