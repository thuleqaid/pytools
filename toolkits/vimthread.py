from PyQt4 import QtCore
import os
import subprocess
import tempfile
import re
import logutil

class VimThread(QtCore.QThread):
    def __init__(self,vimpath,parent=None):
        super(VimThread,self).__init__(parent)
        self._log=logutil.LogUtil().logger('VimThread')
        self._tmpdir=''
        self._vimpath=vimpath
        self._log.debug("VimPath: %s"%(self._vimpath,))
    def setSrcPath(self,srcpath):
        self._srcpath=srcpath
        self._log.debug("SrcPath: %s"%(self._srcpath,))
    def run(self):
        self.cleanTempfile()
        params=[]
        params.append(self._vimpath)
        params.append('-s')
        params.append(self.newTempfile())
        self._log.debug(str(params))
        try:
            subprocess.check_call(params)
        except subprocess.CalledProcessError as err:
            self._log.error(err)
    def newTempfile(self):
        txt=":STag %s\n"%(self._srcpath,)
        tmpfile=tempfile.NamedTemporaryFile(dir=self._tmpdir,delete=False)
        tmpfile.write(txt.encode('utf-8'))
        tmpfile.close()
        return tmpfile.name
    def cleanTempfile(self):
        cwd=os.getcwd()
        self._tmpdir=os.path.join(cwd,'temp')
        if os.path.isdir(self._tmpdir):
            for f in os.listdir(self._tmpdir):
                os.remove(os.path.join(self._tmpdir,f))
        else:
            os.mkdir(self._tmpdir)

class VimTagThread(QtCore.QThread):
    D_STR_INDEXFILE='cscope.files'
    def __init__(self,cscope,ctags,parent=None):
        super(VimTagThread,self).__init__(parent)
        self._log=logutil.LogUtil().logger('VimThread')
        self._cscope=cscope
        self._ctags=ctags
        self._srcpath=''
        self._filepat=None
        self._currentdir=os.getcwd()
        self._log.debug("CscopePath: %s, CtagsPath: %s"%(self._cscope,self._ctags))
    def setSrcPath(self,srcpath,filepat):
        self._srcpath=srcpath
        self._filepat=re.compile(filepat)
        self._log.debug("SrcPath: %s, FileFilter: %s"%(self._srcpath,filepat))
    def cscopeindex(self):
        self.emit(QtCore.SIGNAL("threadStatus(const QString&)"),"making filelist")
        outlist=[]
        for root,dirs,files in os.walk(self._srcpath):
            for fname in files:
                if self._filepat.search(fname):
                    outlist.append(os.path.relpath(os.path.join(root,fname),self._srcpath))
        with open(os.path.join(self._srcpath,self.D_STR_INDEXFILE),'w') as fh:
            fh.write("\n".join(outlist))
    def runCscope(self):
        if os.path.isfile(self._cscope):
            self.cscopeindex()
            self.emit(QtCore.SIGNAL("threadStatus(const QString&)"),"Running cscope...")
            idxfile=os.path.join(self._srcpath,self.D_STR_INDEXFILE)
            params=[]
            params.append(self._cscope)
            params.append('-Rbc')
            params.append('-i')
            params.append(idxfile)
            self._log.debug(str(params))
            try:
                subprocess.check_call(params)
            except subprocess.CalledProcessError as err:
                self._log.error(err)
            finally:
                os.remove(idxfile)
    def runCtags(self):
        if os.path.isfile(self._ctags):
            self.emit(QtCore.SIGNAL("threadStatus(const QString&)"),"Running ctags...")
            params=[]
            params.append(self._ctags)
            params.append('-R')
            self._log.debug(str(params))
            try:
                subprocess.check_call(params)
            except subprocess.CalledProcessError as err:
                self._log.error(err)
    def run(self):
        if os.path.isdir(self._srcpath):
            os.chdir(self._srcpath)
            self.runCscope()
            self.runCtags()
            os.chdir(self._currentdir)
            self.emit(QtCore.SIGNAL("threadStatus(const QString&)"),"Done.")
        else:
            self.emit(QtCore.SIGNAL("threadStatus(const QString&)"),"Invalid source folder.")
