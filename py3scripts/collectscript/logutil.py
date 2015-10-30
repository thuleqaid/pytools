# -*- coding:utf-8 -*-
# VERSION: 0.1
import sys
import os
from threading import Lock
import logging
import logging.config

# LogUtil Usage:
#   1. create log-config file
#       newConf((logname1, logname2, ...))
#   2. create log object
#       logger = LogUtil().logger(lognameX)
#   3. output log
#       logger.log(nLvl, msg)

if hasattr(sys,'frozen'):
    _selffile = sys.executable
else:
    _selffile = __file__

def scriptPath(filepath):
    '''
    get dirpath
    @param  __file__
    @return dirpath
    '''
    outdir=os.path.dirname(os.path.abspath(filepath))
    # in case of cx_freeze
    while os.path.isfile(outdir):
        outdir=os.path.dirname(outdir)
    return outdir

def singleton(cls, *args, **kw):
    instance={}
    inslocker=Lock()
    def _singleton():
        if cls in instance:
            return instance[cls]
        inslocker.acquire()
        try:
            if cls in instance:
                return instance[cls]
            else:
                instance[cls]=cls(*args, **kw)
        finally:
            inslocker.release()
        return instance[cls]
    return _singleton

@singleton
class LogUtil(object):
    LOGDIR=scriptPath(_selffile).replace('\\','/')
    CONFFILE=os.path.join(scriptPath(_selffile),'logging.conf')
    def __init__(self):
        if os.path.exists(self.CONFFILE) and os.path.isfile(self.CONFFILE):
            logging.config.fileConfig(self.CONFFILE,{'logdir':self.LOGDIR})
        else:
            pass
    def logger(self,logname):
        return logging.getLogger(logname)

def newConf(lognames=('UnKnown',), filename='logging.conf', all_handlers=False):
    str_handler1='''
[handler_hnull]
class=NullHandler
level=NOTSET
args=()

[handler_hstream]
class=StreamHandler
level=NOTSET
formatter=fdatetime1
args=(sys.stdout,)

[handler_hfile]
class=FileHandler
level=NOTSET
formatter=fdatetime1
#args=('%(logdir)s/log.log', 'a', 'utf8')
args=('%(logdir)s/log.log', 'w', 'utf8')
'''
    str_handler2='''
[handler_hfilew]
class=handlers.WatchedFileHandler
level=NOTSET
formatter=fdatetime1
args=('%(logdir)s/log.log', 'a', 'utf8')

[handler_hfiler]
class=handlers.RotatingFileHandler
level=NOTSET
formatter=fdatetime1
args=('%(logdir)s/log.log', 'a', 1024*1024, 6, 'utf8')

[handler_hfilet]
class=handlers.TimedRotatingFileHandler
level=NOTSET
formatter=fdatetime1
args=('%(logdir)s/log.log', 'h', 1, 6, 'utf8')
'''
    str_format='''
[formatter_fdatetime1]
format=%(asctime)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s
datefmt=%Y-%m-%d %H:%M:%S

[formatter_fdatetime2]
format=%(asctime)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s
datefmt=

##format:
#1#%(asctime)s
#1#%(levelname)s
#1#%(levelno)s
#1#%(name)s
#1#%(message)s
#2#%(pathname)s
#2#%(filename)s
#2#%(module)s
#2#%(funcName)s
#2#%(lineno)d
#3#%(process)d
#3#%(processName)s
#3#%(thread)d
#3#%(threadName)s 
'''
    fh = open(os.path.join(scriptPath(_selffile), filename), 'w', encoding='utf-8')
    fh.write('''
##uncomment the following line will overwrite logdir's value in the python script
#[DEFAULT]
#logdir=
''')
    fh.write('''
[loggers]
keys=''')
    fh.write(','.join(['root',]+list(lognames)))
    fh.write('\n')
    if all_handlers:
        fh.write('''
[handlers]
keys=hnull,hstream,hfile,hfilew,hfiler,hfiler
''')
    else:
        fh.write('''
[handlers]
keys=hnull,hstream,hfile
''')
    fh.write('''
[formatters]
keys=fdatetime1,fdatetime2

[logger_root]
level=NOTSET
handlers=hstream
''')
    for lname in lognames:
        fh.write('''
[logger_%s]
level=NOTSET
handlers=hfile
propagate=0
qualname=%s
'''%(lname,lname))
    fh.write(str_handler1)
    if all_handlers:
        fh.write(str_handler2)
    fh.write(str_format)
    fh.close()

if __name__=='__main__':
    import sys
    from argparse import ArgumentParser
    parser=ArgumentParser()
    parser.add_argument('-f','--file',dest='outfile', default='logging.conf',
                      help='filename for output config file')
    parser.add_argument('-a','--all',dest='flag_all',
                      action='store_true', default=False,
                      help='output all handlers')
    parser.add_argument('names',nargs='*',help='logger names')
    options=parser.parse_args()
    args=options.names
    outfile=options.outfile
    flag=options.flag_all
    newConf(args, outfile, flag)
