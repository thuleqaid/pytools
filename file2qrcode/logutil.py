from os.path import exists,isfile
from logging import getLogger
from logging.config import fileConfig
from generalutil import singleton_s

@singleton_s
class LogUtil(object):
    CONFFILE='logging.conf'
    def __init__(self):
        if exists(self.CONFFILE) and isfile(self.CONFFILE):
            fileConfig(self.CONFFILE)
        else:
            pass
    def logger(self,logname):
        return getLogger(logname)
