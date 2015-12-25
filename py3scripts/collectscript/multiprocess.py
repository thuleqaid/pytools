# -*- coding:utf-8 -*-
# VERSION: 0.1
import os
import subprocess
from .logutil import LogUtil, registerLogger

LOGNAME = 'MultiProcess'
registerLogger(LOGNAME)

class MultiProcess(object):
    def __init__(self):
        self._log = LogUtil().logger(LOGNAME)
        self._kwargs = {}
        if os.name == 'nt':
            self._log.log(10, 'Windows NT')
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags = subprocess.CREATE_NEW_CONSOLE | subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            self._kwargs['startupinfo'] = startupinfo
        else:
            self._log.log(10, 'Not NT')
            self._iswin = False
    def call(self, *args, **kwargs):
        for key in self._kwargs.keys():
            kwargs.setdefault(key, self._kwargs[key])
        retcode = subprocess.call(*args, **kwargs)
        return retcode
