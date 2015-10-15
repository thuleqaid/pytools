# -*- coding:utf-8 -*-
# VERSION: 0.1
import os
import re
import codecs
import shutil
import logutil  # logger name: EncodeChanger

class EncodeChanger(object):
    NEWLINE_CR='\r'
    NEWLINE_LF='\n'
    NEWLINE_CRLF=NEWLINE_CR+NEWLINE_LF
    def __init__(self):
        self._srcdir = ''                   # Property:srcdir
        self._dstdir = ''                   # Property:dstdir
        self._filter = None                 # Property:regex, Regular Expression Object
        self._fileall = set()               # Property(Read):fileall, Relative path of all files in the self._srcdir
        self._filehit = set()               # Property(Read):filehit/fileother, Subset of self._filehit, which contains items that meet self._filter
        self._copyother = False             # Property:copyother, Whether copy un-hit items into self._dstdir
        self._ignoreVCS = True              # Property:vcs, Whether ignore VCS files
        self._incode = ('cp932', 'cp936')   # Property:incode, Input files' encode list
        self._outcode = 'utf-8-sig'         # Property:outcode, Output files' encode
        self._newline = ''                  # Property:newline, value choices:'', 'dos', 'mac', 'unix'
        self._error = False                 # Property(Read):error, flag for each function call
        self._logger = logutil.LogUtil().logger('EncodeChanger')
        self._logger.log(20, 'New Object')
    def translate(self):
        self._logger.log(20, 'Translate {0}:{1} -> {2}:{3} [CopyOther:{4}]'.format(self.srcdir,self.incode,self.dstdir,self.outcode,self.copyother))
        self._error = False
        errorlist = []
        if self.dstdir:
            for item in self.filehit:
                if not self._translate(item):
                    errorlist.append(item)
                    self._copy(item)
                    self._error = True
            if self.copyother:
                for item in self.fileother:
                    self._copy(item)
        return errorlist
    @property
    def srcdir(self):
        return self._srcdir
    @srcdir.setter
    def srcdir(self, srcdir):
        self._error = False
        fullpath = self._checkdir(srcdir)
        if not fullpath:
            self._error = True
        else:
            if fullpath != self._srcdir:
                self._srcdir = fullpath
                # update filelist
                skiplength = len(self._srcdir) + 1
                self._fileall = set()
                for dirpath, dirnames, filenames in os.walk(self._srcdir):
                    for filename in filenames:
                        fullpath = os.path.normpath(os.path.join(dirpath, filename))
                        if not self._ignore(fullpath):
                            self._fileall.add(fullpath[skiplength:])
                self._checkfiles()
    @property
    def dstdir(self):
        return self._dstdir
    @dstdir.setter
    def dstdir(self, dstdir):
        self._error = False
        fullpath = self._checkdir(dstdir)
        if fullpath:
            self._dstdir = fullpath
        else:
            self._dstdir = os.path.normpath(os.path.abspath(dstdir))
            os.makedirs(self._dstdir)
    @property
    def regex(self):
        if self._filter:
            return self._filter.pattern
        else:
            return ''
    @regex.setter
    def regex(self, regex):
        self._error = False
        try:
            newptn = re.compile(regex)
            if self._filter:
                if newptn.pattern != self._filter.pattern:
                    self._filter = newptn
                    self._checkfiles()
            else:
                self._filter = newptn
                self._checkfiles()
        except Exception as e:
            self._logger.log(30, "RegEx Error:" + str(e))
            self._error = True
    @property
    def fileall(self):
        return list(self._fileall)
    @property
    def filehit(self):
        return list(self._filehit)
    @property
    def fileother(self):
        return list(self._fileall - self._filehit)
    @property
    def copyother(self):
        return self._copyother
    @copyother.setter
    def copyother(self, copyother):
        self._error = False
        self._copyother = copyother
    @property
    def vcs(self):
        return self._ignoreVCS
    @copyother.setter
    def vcs(self, vcs):
        self._error = False
        self._ignoreVCS = vcs
    @property
    def incode(self):
        return self._incode
    @incode.setter
    def incode(self, incode):
        self._error = False
        newcode = []
        for item in incode:
            formalcode = self._checkencode(item)
            if formalcode:
                newcode.append(formalcode)
        if len(newcode) > 0:
            self._incode = tuple(newcode)
        else:
            self._error = True
    @property
    def outcode(self):
        return self._outcode
    @outcode.setter
    def outcode(self, outcode):
        self._error = False
        formalcode = self._checkencode(outcode)
        if formalcode:
            if formalcode != self._outcode:
                self._outcode = formalcode
        else:
            self._error = True
    @property
    def newline(self):
        return self._newline
    @newline.setter
    def newline(self, newline):
        self._error = False
        newline = newline.lower()
        if newline in ('dos','mac','unix'):
            self._newline = newline
        else:
            self._newline = ''
            self._error = True
    @property
    def error(self):
        return self._error

    def _checkfiles(self):
        if self._filter:
            self._filehit = set()
            for item in self._fileall:
                if self._filter.search(item):
                    self._filehit.add(item)
        else:
            self._filehit = set(self._fileall)
    def _translate(self, item):
        inpath = os.path.join(self.srcdir, item)
        outpath = os.path.join(self.dstdir, item)
        self._logger.log(10, "Action_Translate: {}".format(item))
        self._mkdir(outpath)
        result = True
        try:
            incode = guessEncode(inpath, *self.incode)[0]
            if incode:
                fin = open(inpath, 'r', encoding=incode)
                data = fin.read()
                fin.close()
                if self.newline == 'dos':
                    newline = self.NEWLINE_CRLF
                elif self.newline == 'mac':
                    newline = self.NEWLINE_CR
                elif self.newline == 'unix':
                    newline = self.NEWLINE_LF
                else:
                    newline = None
                fout = open(outpath, 'w', encoding=self.outcode, newline=newline)
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
    def _copy(self, item):
        inpath = os.path.join(self.srcdir, item)
        outpath = os.path.join(self.dstdir, item)
        self._logger.log(10, "Action_Copy: {}".format(item))
        self._mkdir(outpath)
        shutil.copy(inpath, outpath)
    def _ignore(self, fullpath):
        ret = False
        if self._ignoreVCS:
            if fullpath.endswith('.vss'):
                ret=True
            elif fullpath.find(os.sep+'.svn'+os.sep)>=0:
                ret=True
            elif fullpath.find(os.sep+'.git'+os.sep)>=0:
                ret=True
        return ret

    @staticmethod
    def _checkdir(path):
        fullpath = os.path.abspath(path)
        if os.path.isdir(fullpath):
            return os.path.normpath(fullpath)
        else:
            return ''

    @staticmethod
    def _checkencode(code):
        try:
            outcode = codecs.lookup(code).name
        except Exception as e:
            outcode = ''
            self._logger.log(30, "Invalid Encode:" + str(e))
        return outcode

    @staticmethod
    def _mkdir(filepath):
        head, tail = os.path.split(filepath)
        if os.path.isdir(head):
            if os.path.isfile(filepath):
                os.remove(filepath)
        else:
            os.makedirs(head)

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
    logger = logutil.LogUtil().logger('EncodeChanger')
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

if __name__ == '__main__':
    #logutil.newConf(('EncodeChanger',))
    ec = encodechanger.EncodeChanger()
    #ec.srcdir = 'd:/work_files/AB0100_SRC/ECUSAR'
    #ec.dstdir = 'd:/work_files/AB0100_SRC/ECUSAR2'
    ec.regex = r'\.[cChH]$'
    ec.copyother = True
    errorlist = ec.translate()
    if ec.error:
        print('\n'.join(errorlist))

