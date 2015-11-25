# -*- coding: utf-8 -*-

from cx_Freeze import setup, Executable

options = {
    'build_exe': {
        'include_files': ['collectscript/bin','tpl','xmlconf.ini','Readme.xls']
    }
}

executables = [
    Executable('astahFlowChart.py')
]

setup(name='AstahFlowChart',
      version='0.1',
      description='Generate flowchart files accepted by Astah',
      options=options,
      executables=executables
      )
