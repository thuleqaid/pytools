import os
import configparser
import sys
import logutil

class EncodeConfig(object):
    def __init__(self,configfile=''):
        self._log=logutil.LogUtil().logger('EncodeConfig')
        if configfile and os.path.isfile(configfile):
            self._conffile=configfile
        else:
            self._conffile=os.path.join(logutil.scriptPath(__file__),'encode.ini')
        self._log.info('config-file:%s'%(self._conffile,))
        self._loadConfig()
    def _loadConfig(self):
        if not self._validConfig():
            self._initConfig()
        config=configparser.ConfigParser()
        with open(self._conffile,'r',encoding='utf-8') as fh:
            config.read_file(fh)
        self._pattern=config.items('FilePattern',raw=True)
        encodes=[]
        for item in config.items('Encoding',raw=True):
            parts=item[1].split(',')
            encodes.append([item[0],parts[0],int(parts[1]),int(parts[2])])
        self._encode=list(encodes)
        self._log.debug('FilePattern:%s'%(str(self._pattern),))
        self._log.debug('Encoding:%s'%(str(self._encode),))
    def _validConfig(self):
        ret=True
        if os.path.isfile(self._conffile):
            config=configparser.ConfigParser()
            with open(self._conffile,'r',encoding='utf-8') as fh:
                config.read_file(fh)
            for sectname in ('FilePattern','Encoding'):
                if not config.has_section(sectname):
                    self._log.warning('invalid config file: Section[%s] not found'%(sectname,))
                    ret=False
                    break
        else:
            self._log.warning('config file not exist')
            ret=False
        return ret
    def _initConfig(self):
        config=configparser.ConfigParser()
        config.add_section('FilePattern')
        config.set('FilePattern','C/C++ Files',r'\.(c|c\+\+|cc|cp|cpp|cxx|h|h\+\+|hh|hp|hpp|hxx)$')
        config.set('FilePattern','Python Files',r'\.(py|pyx|pxd|pxi|scons)$')
        config.add_section('Encoding')
        config.set('Encoding','ShiftJIS','cp932,1,1')
        config.set('Encoding','GBK','cp936,1,1')
        config.set('Encoding','UTF8','utf-8,1,1')
        with open(self._conffile,'w',encoding='utf-8') as fh:
            config.write(fh)
    def patterns(self):
        return tuple(self._pattern)
    def encodes(self):
        return tuple(self._encode)

