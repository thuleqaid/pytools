from PyQt4 import QtCore
import os
import sys
import logutil

class EncodeThread(QtCore.QThread):
    D_FILENAME_SUFFIX='.org'
    D_WORK_CHANGE=1
    D_WORK_RESTORE=2
    def __init__(self,parent=None):
        super(EncodeThread,self).__init__(parent)
        self._log=logutil.LogUtil().logger('EncodeThread')
    def setEncodeList(self,encodelist):
        self._encode_checklist=tuple(encodelist)
    def setData(self,inpath,outcode='utf-8',outeol='UNIX',fnamepattern=None,ignore=False):
        self._inpath=inpath
        self._outcode=outcode
        self._outeol=outeol
        self._fnptn=fnamepattern
        self._ignore=ignore
    def setWorktype(self,worktype):
        self._worktype=worktype
    def run(self):
        filelist=[]
        for root,folders,files in os.walk(self._inpath):
            for fname in files:
                fullpath=os.path.join(root,fname)
                self._log.debug('Check Filename:%s'%(fullpath,))
                if not self.isVCSFile(fullpath):
                    if self._worktype==self.D_WORK_CHANGE:
                        if self.checkChange(fullpath):
                            filelist.append(fullpath)
                            self._log.debug('Add Change File')
                    elif self._worktype==self.D_WORK_RESTORE:
                        if self.checkRestore(fullpath):
                            filelist.append(fullpath)
                            self._log.debug('Add Restore File')
        self.emit(QtCore.SIGNAL("progress(int,int)"),0,len(filelist))
        workingdir=''
        for fidx,fullpath in enumerate(filelist):
            curdir=os.path.dirname(fullpath)
            if workingdir!=curdir:
                workingdir=curdir
                self.emit(QtCore.SIGNAL("currentDir(const QString&)"),workingdir)
            if self._worktype==1:
                self.doChange(fullpath)
            elif self._worktype==2:
                self.doRestore(fullpath)
            self.emit(QtCore.SIGNAL("progress(int,int)"),fidx+1,len(filelist))
    def checkChange(self,fullpath):
        flag=False
        if self._fnptn:
            if self._fnptn.search(fullpath):
                flag=True
        else:
            flag=True
        return flag
    def doChange(self,fullpath):
        bakpath=fullpath+self.__class__.D_FILENAME_SUFFIX
        os.rename(fullpath,bakpath)
        incode=logutil.guessEncode(bakpath,*self._encode_checklist)[0]
        if not self._outcode:
            outcode=incode
        else:
            outcode=self._outcode
        self._encode(bakpath,incode,fullpath,outcode,self._outeol)
    def checkRestore(self,fullpath):
        if fullpath.endswith(self.__class__.D_FILENAME_SUFFIX):
            return True
        else:
            return False
    def doRestore(self,fullpath):
        bakpath=fullpath[:-len(self.__class__.D_FILENAME_SUFFIX)]
        if os.path.exists(bakpath):
            os.remove(bakpath)
        os.rename(fullpath,bakpath)
    def _encode(self,infile,incode,outfile,outcode,fileformat='UNIX'):
        CR='\r'
        LF='\n'
        CRLF=CR+LF
        fh=open(infile,'r',encoding=incode)
        data=fh.read()
        fh.close()
        if fileformat.upper()=='DOS':
            eol=CRLF
        elif fileformat.upper()=='MAC':
            eol=CR
        else:
            eol=LF
        fh=open(outfile,'w',encoding=outcode,errors='ignore',newline=eol)
        fh.write(data)
        fh.close()
    def isVCSFile(self,fullpath):
        ret=False
        if self._ignore:
            cfullpath=os.path.normcase(fullpath).lower()
            if cfullpath.endswith('.vss'):
                ret=True
            elif cfullpath.find(os.sep+'.svn'+os.sep)>=0:
                ret=True
            elif cfullpath.find(os.sep+'.git'+os.sep)>=0:
                ret=True
            if ret:
                self._log.debug('Ignore VCS File')
        return ret
