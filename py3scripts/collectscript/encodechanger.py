# -*- coding:utf-8 -*-
# VERSION: 0.1
import os
from .logutil import LogUtil
from .guess import guessEncode

LOGNAME = 'EncodeChanger'

class EncodeChanger(object):
    NEWLINE_CR='\r'
    NEWLINE_LF='\n'
    NEWLINE_CRLF=NEWLINE_CR+NEWLINE_LF
    def __init__(self, encodelist=('cp932','cp936')):
        self._incode = tuple(encodelist)
        self._logger = LogUtil().logger(LOGNAME)
        self._logger.log(20, 'New Object')
    def change(self, srcfile, dstfile, outcode='utf-8-sig', newline=''):
        inpath = srcfile
        outpath = dstfile
        self._logger.log(10, "Action_Translate: {}->{}[{},{}]".format(srcfile,dstfile,outcode,newline))
        result = True
        try:
            incode = guessEncode(inpath, *self._incode)[0]
            if incode:
                fin = open(inpath, 'r', encoding=incode)
                data = fin.read()
                fin.close()
                if newline == 'dos':
                    newlinech = self.NEWLINE_CRLF
                elif newline == 'mac':
                    newlinech = self.NEWLINE_CR
                elif newline == 'unix':
                    newlinech = self.NEWLINE_LF
                else:
                    newlinech = None
                self._mkdir(outpath)
                fout = open(outpath, 'w', encoding=outcode, newline=newlinech)
                fout.write(data)
                fout.close()
                result = True
            else:
                result = False
                self._logger.log(30, "Read Error")
        except Exception as e:
            result = False
            self._logger.log(30, "Write Error:" + str(e))
        return result
    @staticmethod
    def _mkdir(filepath):
        head, tail = os.path.split(filepath)
        if os.path.isdir(head):
            if os.path.isfile(filepath):
                os.remove(filepath)
        else:
            os.makedirs(head, exist_ok=True)

