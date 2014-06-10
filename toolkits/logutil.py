from os.path import exists,isfile,join,dirname,abspath
from logging import getLogger
from logging.config import fileConfig
from threading import Lock
import codecs

def scriptPath(filepath):
    '''
    get dirpath
    @param  __file__
    @return dirpath
    '''
    outdir=dirname(abspath(filepath))
    # in case of cx_freeze
    while isfile(outdir):
        outdir=dirname(outdir)
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
    LOGDIR=scriptPath(__file__).replace('\\','/')
    CONFFILE=join(scriptPath(__file__),'logging.conf')
    def __init__(self):
        if exists(self.CONFFILE) and isfile(self.CONFFILE):
            fileConfig(self.CONFFILE,{'logdir':self.LOGDIR})
        else:
            pass
    def logger(self,logname):
        return getLogger(logname)

def IOLog(func):
    def wrapper(*args,**kv):
        self=args[0]
        if '_log' not in self.__dict__:
            self._log=LogUtil().logger(self.__class__.__name__)
        self._log.info('Entry:%s.%s'%(self.__class__.__name__,func.__name__,))
        ret=func(*args,**kv)
        self._log.info('Exit:%s.%s'%(self.__class__.__name__,func.__name__,))
        return ret
    return wrapper
def IOLog1(func):
    def wrapper(*args,**kv):
        self=args[0]
        if '_log' not in self.__dict__:
            self._log=LogUtil().logger(self.__class__.__name__)
        self._log.info('Entry:%s.%s'%(self.__class__.__name__,func.__name__,))
        if len(args)>1:
            self._log.debug('  Parameters:%s'%(str(args[1:]),))
        if len(kv)>0:
            self._log.debug('  Parameters:%s'%(str(kv),))
        ret=func(*args,**kv)
        self._log.info('Exit:%s.%s'%(self.__class__.__name__,func.__name__,))
        return ret
    return wrapper
def IOLog2(func):
    def wrapper(*args,**kv):
        self=args[0]
        if '_log' not in self.__dict__:
            self._log=LogUtil().logger(self.__class__.__name__)
        self._log.info('Entry:%s.%s'%(self.__class__.__name__,func.__name__,))
        ret=func(*args,**kv)
        self._log.info('Exit:%s.%s'%(self.__class__.__name__,func.__name__,))
        if ret:
            self._log.debug('  Return:%s'%(str(ret),))
        return ret
    return wrapper
def IOLog3(func):
    def wrapper(*args,**kv):
        self=args[0]
        if '_log' not in self.__dict__:
            self._log=LogUtil().logger(self.__class__.__name__)
        self._log.info('Entry:%s.%s'%(self.__class__.__name__,func.__name__,))
        if len(args)>1:
            self._log.debug('  Parameters:%s'%(str(args[1:]),))
        if len(kv)>0:
            self._log.debug('  Parameters:%s'%(str(kv),))
        ret=func(*args,**kv)
        self._log.info('Exit:%s.%s'%(self.__class__.__name__,func.__name__,))
        if ret:
            self._log.debug('  Return:%s'%(str(ret),))
        return ret
    return wrapper

def guessEncode(fname,*encodelist):
    '''
    check file's encode
    first check if the file has a bom and test associated encode
    then test encodes in encodelist
    last test 'utf_8'
    param:
        fname -- file path
        encodelist -- encodes to be tested
    return:
        encodename, bomlen
    '''
    log=LogUtil().logger('root')
    log.info('File[%s] EncodeList[%s]'%(fname,','.join(encodelist)))
    fh=open(fname,'rb')
    lines=fh.read()
    fh.close()
    boms={'utf_32':   codecs.BOM_UTF32,
          'utf_32_be':codecs.BOM_UTF32_BE,
          'utf_32_le':codecs.BOM_UTF32_LE,
          'utf_16':   codecs.BOM_UTF16,
          'utf_16_be':codecs.BOM_UTF16_BE,
          'utf_16_le':codecs.BOM_UTF16_LE,
          'utf_8':    codecs.BOM_UTF8}
    # bom check
    for enc,bom in boms.items():
        bomlen=len(bom)
        if lines[:bomlen]==bom:
            log.debug('Bom for %s matches'%(enc,))
            data=lines[bomlen:]
            try:
                data.decode(enc)
                log.info('Found Encode %s'%(enc,))
                return (enc,bomlen)
            except:
                log.debug('Test failed [%s]'%(enc,))
                pass
    # input encoding check
    bomlen=0
    for enc in encodelist:
        log.debug('Test encode[%s]'%(enc,))
        data=lines[:]
        try:
            data.decode(enc)
            log.info('Found Encode %s'%(enc,))
            return (enc,bomlen)
        except:
            pass
    # utf_8 check
    enc='utf_8'
    data=lines[:]
    try:
        data.decode(enc)
        log.info('Found Encode %s'%(enc,))
        return (enc,bomlen)
    except:
        pass
    enc=''
    log.info('Failed to find encode')
    return (enc,bomlen)

def generateLogConfig(outfile,lognames,all_handlers=False):
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
    with open(outfile,'w') as fh:
        fh.write('''
##uncomment the following line will overwrite logdir's value in the python script
#[DEFAULT]
#logdir=
''')
        fh.write('''
[loggers]
keys=''')
        fh.write(','.join(['root',]+lognames))
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


if __name__=='__main__':
    import sys
    if sys.version_info[0]<3:
        from optparse import OptionParser
        parser=OptionParser()
        parser.add_option('-f','--file',dest='outfile', default='logging.conf',
                          help='filename for output config file')
        parser.add_option('-a','--all',dest='flag_all',
                          action='store_true', default=False,
                          help='output all handlers')
        (options,args)=parser.parse_args()
    else:
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
    generateLogConfig(outfile,args,flag)
