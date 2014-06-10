import os
import configparser
import sys
import logutil

class VimConfig(object):
    def __init__(self,configfile=''):
        self._log=logutil.LogUtil().logger('VimConfig')
        if configfile and os.path.isfile(configfile):
            self._conffile=configfile
        else:
            self._conffile=os.path.join(logutil.scriptPath(__file__),'vim.ini')
        self._log.info('config-file:%s'%(self._conffile,))
        self._loadConfig()
    def _loadConfig(self):
        if not self._validConfig():
            self._initConfig()
        config=configparser.ConfigParser()
        with open(self._conffile,'r',encoding='utf-8') as fh:
            config.read_file(fh)
        self._pattern=config.items('FilePattern',raw=True)
        self._tool=config.items('Tool',raw=True)
        self._log.debug('FilePattern:%s'%(str(self._pattern),))
        self._log.debug('Tool:%s'%(str(self._tool),))
    def _validConfig(self):
        ret=True
        if os.path.isfile(self._conffile):
            config=configparser.ConfigParser()
            with open(self._conffile,'r',encoding='utf-8') as fh:
                config.read_file(fh)
            for sectname in ('FilePattern','Tool'):
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
        config.add_section('Tool')
        config.set('Tool','vim','')
        config.set('Tool','cscope','')
        config.set('Tool','ctags','')
        with open(self._conffile,'w',encoding='utf-8') as fh:
            config.write(fh)
    def patterns(self):
        return tuple(self._pattern)
    def tools(self):
        return dict(self._tool)

