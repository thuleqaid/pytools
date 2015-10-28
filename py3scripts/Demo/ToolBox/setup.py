# -*- coding: utf-8 -*-

import sys
from cx_Freeze import setup, Executable

base = None
if sys.platform == 'win32':
    base = 'Win32GUI'

options = {
    'build_exe': {
        'includes': 'atexit',
        'include_files': ['bin','qm']
    }
}

executables = [
    Executable('toolbox.py', base=base)
]

setup(name='ToolBox',
      version='0.1',
      description='ToolBox',
      options=options,
      executables=executables
      )

