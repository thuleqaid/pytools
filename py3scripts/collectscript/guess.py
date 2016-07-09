# -*- coding:utf-8 -*-
# VERSION: 0.1
import codecs
import os
from .logutil import LogUtil, registerLogger

LOGNAME = 'GuessEncode'
registerLogger(LOGNAME)

DEFAULT_ENCODE = ('cp932', 'cp936')

def unescape(txt, encoding):
    bstr = bytes(txt, encoding)
    bstr = bstr.replace(b'\\\\',b'\\')
    bstr = bstr.replace(b'\\/',b'/')
    return bstr.decode(encoding)

def setDefaultEncode(*encodelist):
    DEFAULT_ENCODE = tuple(encodelist)
def getDefaultEncode():
    return DEFAULT_ENCODE

def openTextFile(*args, **kwargs):
    if len(args) > 0:
        fname = args[0]
        encode = guessEncode(fname, *DEFAULT_ENCODE)[0]
        if encode:
            fh = open(*args, encoding=encode, errors='ignore', **kwargs)
        else:
            fh = open(*args, errors='ignore', **kwargs)
        return fh
    else:
        return None

def titledText(strlist, sep='', selectedtitle={}):
    # Comment Line: Line starts with '#'
    # Title Line: Line starts with '#@'
    flag = False
    data = []
    for idx, line in enumerate(strlist):
        if line.startswith('#@'):
            titleline = line[2:]
            if sep == '':
                # Guess seperator in ',','\t',':'
                seplist = ['\t', ',', ':']
                for sepitem in seplist:
                    if sepitem in titleline:
                        sep = sepitem
                        break
            else:
                if sep not in titleline:
                    sep = ''
            if sep == '':
                # Only one column
                title = [titleline]
            else:
                title = titleline.split(sep)
            flag = True
        elif line.startswith('#'):
            pass
        elif flag:
            # Date Lines
            if line.strip() == '':
                # Empty Line
                pass
            else:
                if sep == '':
                    data.append([line])
                else:
                    data.append(line.split(sep))
    titledict = dict(zip(title, range(len(title))))
    seltitledict = dict(selectedtitle)
    for key in seltitledict.keys():
        seltitledict[key] = titledict.get(seltitledict[key], -1)
    outinfo = { 'data': data,
                'title': titledict,
                'seltitle': seltitledict}
    return outinfo

def readTextFile(striptype, *args, **kwargs):
    fh = openTextFile(*args, **kwargs)
    if striptype == 'lstrip':
        stripfunc = str.lstrip
    elif striptype == 'rstrip':
        stripfunc = str.rstrip
    elif striptype == 'strip':
        stripfunc = str.strip
    else:
        stripfunc = None
    outlist = []
    for idx,line in enumerate(fh.readlines()):
        if stripfunc:
            line = stripfunc(line)
        outlist.append(line)
    fh.close()
    return outlist

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
    logger = LogUtil().logger(LOGNAME)
    logger.log(20, 'GuessEncode: File[%s] EncodeList[%s]'%(fname,','.join(encodelist)))
    fh=open(fname,'rb')
    lines=fh.read()
    fh.close()
    boms={'utf_32':   codecs.BOM_UTF32,
          'utf_32_be':codecs.BOM_UTF32_BE,
          'utf_32_le':codecs.BOM_UTF32_LE,
          'utf_16':   codecs.BOM_UTF16,
          'utf_16_be':codecs.BOM_UTF16_BE,
          'utf_16_le':codecs.BOM_UTF16_LE,
          'utf_8_sig':    codecs.BOM_UTF8}
    # bom check
    for enc,bom in boms.items():
        bomlen=len(bom)
        if lines[:bomlen]==bom:
            logger.log(10, 'GuessEncode: Bom for %s matches'%(enc,))
            data=lines[bomlen:]
            try:
                data.decode(enc)
                logger.log(20, 'GuessEncode: Found Encode %s'%(enc,))
                return (enc,bomlen)
            except:
                logger.log(10, 'GuessEncode: Test failed [%s]'%(enc,))
                pass
    # input encoding check
    bomlen=0
    for enc in encodelist:
        logger.log(10, 'GuessEncode: Test encode[%s]'%(enc,))
        data=lines[:]
        try:
            data.decode(enc)
            logger.log(20, 'GuessEncode: Found Encode %s'%(enc,))
            return (enc,bomlen)
        except:
            pass
    # utf_8 check
    enc='utf_8'
    data=lines[:]
    try:
        data.decode(enc)
        logger.log(20, 'GuessEncode: Found Encode %s'%(enc,))
        return (enc,bomlen)
    except:
        pass
    enc=''
    logger.log(30, 'GuessEncode: Failed to find encode')
    return (enc,bomlen)

def findExe(prgname):
    pathlist = os.getenv('PATH').split(';')
    found = ''
    for item in pathlist:
        if os.path.isfile(os.path.join(item,prgname)):
            found = item
            break
    ## .bat version
    # @echo off
    # set new="%path:;=" "%"
    # set curdir=%cd%
    # set found=
    # for %%a in (%new%) do (
    #   cd /d %%~a
    #   if exist python.exe set found=%%~a
    # )
    # cd /d %curdir%
    # if defined found (
    #   echo %found%
    # )
    return found
