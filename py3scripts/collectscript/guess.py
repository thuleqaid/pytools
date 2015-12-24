# -*- coding:utf-8 -*-
# VERSION: 0.1
import codecs
from .logutil import LogUtil, registerLogger

LOGNAME = 'GuessEncode'
registerLogger(LOGNAME)

def unescape(txt, encoding):
    bstr = bytes(txt, encoding)
    bstr = bstr.replace(b'\\\\',b'\\')
    bstr = bstr.replace(b'\\/',b'/')
    return bstr.decode(encoding)

def openTextFile(encodelist, *args, **kwargs):
    if len(args) > 0:
        fname = args[0]
        encode = guessEncode(fname, *encodelist)[0]
        if encode:
            fh = open(*args, encoding=encode, errors='ignore', **kwargs)
        else:
            fh = open(*args, errors='ignore', **kwargs)
        return fh
    else:
        return None

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

