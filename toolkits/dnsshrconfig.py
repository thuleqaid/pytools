import os
import configparser
import sys
import logutil

class DNSSHRConfig(object):
    def __init__(self,configfile=''):
        if configfile and os.path.isfile(configfile):
            self._conffile=configfile
        else:
            self._conffile=os.path.join(logutil.scriptPath(__file__),'dnsshr.ini')
        self._loadConfig()
    def _loadConfig(self):
        if not self._validConfig():
            self._initConfig()
        config=configparser.ConfigParser()
        with open(self._conffile,'r',encoding='utf-8') as fh:
            config.read_file(fh)
        self._holiday=config.items('Holiday',raw=True)
        self._workday=config.items('Workday',raw=True)
    def _validConfig(self):
        ret=True
        if os.path.isfile(self._conffile):
            config=configparser.ConfigParser()
            with open(self._conffile,'r',encoding='utf-8') as fh:
                config.read_file(fh)
            for sectname in ('Workday','Holiday'):
                if not config.has_section(sectname):
                    ret=False
                    break
        else:
            ret=False
        return ret
    def _initConfig(self):
        config=configparser.ConfigParser()
        config.add_section('Workday')
        config.add_section('Holiday')
        with open(self._conffile,'w',encoding='utf-8') as fh:
            config.write(fh)
    def workday(self):
        return dict(self._workday)
    def holiday(self):
        return dict(self._holiday)

