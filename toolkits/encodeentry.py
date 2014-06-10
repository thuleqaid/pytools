from PyQt4 import QtGui,QtCore
import re
import sys
import os
import logutil
import encode_ui
import encodethread
import encodeconfig

class MainWidget(QtGui.QWidget):
    def setupUi(self):
        self._ui=encode_ui.Ui_Encode()
        self._ui.setupUi(self)
        self._loadConfig()
        self._log=logutil.LogUtil().logger('EncodeMainWidget')
        self._worker=encodethread.EncodeThread(self)
        self.connect(self._worker,QtCore.SIGNAL("started()"),self.workStarted)
        self.connect(self._worker,QtCore.SIGNAL("finished()"),self.workFinished)
        self.connect(self._worker,QtCore.SIGNAL("terminated()"),self.workTerminated)
        self.connect(self._worker,QtCore.SIGNAL("progress(int,int)"),self.workProgress)
        self.connect(self._worker,QtCore.SIGNAL("currentDir(const QString&)"),self.workCurrentDir)
    def _loadConfig(self):
        config=encodeconfig.EncodeConfig()
        self._pattern=config.patterns()
        while self._ui.inFileType.count()>1:
            self._ui.inFileType.removeItem(1)
        for pntkey,pntvalue in self._pattern:
            self._ui.inFileType.addItem(pntkey)
        while self._ui.outEncode.count()>0:
            self._ui.outEncode.removeItem(0)
        self._encode_checklist=[]
        self._encode_convertlist=[]
        for encode in config.encodes():
            if encode[2]>0:
                # encode for checking input
                self._encode_checklist.append(encode[1])
            if encode[3]>0:
                # encode for output
                self._encode_convertlist.append((encode[0],encode[1]))
                self._ui.outEncode.addItem(encode[0])
    def onBtnChoose(self):
        self._ui.inPath.setText(QtGui.QFileDialog.getExistingDirectory(self))
    def onBtnChange(self):
        srcpath,fileptn,code,eol=self._getSetting()
        if srcpath:
            self._ui.outHistory.addItem('Start Changing...')
            self._ui.outHistory.scrollToItem(self._ui.outHistory.item(self._ui.outHistory.count()-1))
            self._worker.setData(srcpath,code,eol,fileptn,self._ui.inIgnore.isChecked())
            self._worker.setEncodeList(self._encode_checklist)
            self._worker.setWorktype(self._worker.D_WORK_CHANGE)
            self._worker.start()
    def onBtnRestore(self):
        srcpath,fileptn,code,eol=self._getSetting()
        if srcpath:
            self._ui.outHistory.addItem('Start Restoring...')
            self._ui.outHistory.scrollToItem(self._ui.outHistory.item(self._ui.outHistory.count()-1))
            self._worker.setData(srcpath)
            self._worker.setWorktype(self._worker.D_WORK_RESTORE)
            self._worker.start()
    def workStarted(self):
        self._ui.btnChoose.setEnabled(False)
        self._ui.btnChange.setEnabled(False)
        self._ui.btnRestore.setEnabled(False)
    def workFinished(self):
        self._ui.outHistory.addItem('Work Finished.')
        self._ui.outHistory.addItem('==========')
        self._ui.outHistory.scrollToItem(self._ui.outHistory.item(self._ui.outHistory.count()-1))
        self._ui.btnChoose.setEnabled(True)
        self._ui.btnChange.setEnabled(True)
        self._ui.btnRestore.setEnabled(True)
    def workTerminated(self):
        self._ui.outHistory.addItem('Work Terminated.')
        self._ui.outHistory.addItem('==========')
        self._ui.outHistory.scrollToItem(self._ui.outHistory.item(self._ui.outHistory.count()-1))
        self._ui.btnChoose.setEnabled(True)
        self._ui.btnChange.setEnabled(True)
        self._ui.btnRestore.setEnabled(True)
    def workCurrentDir(self,workdir):
        self._ui.outHistory.addItem(workdir)
        self._ui.outHistory.scrollToItem(self._ui.outHistory.item(self._ui.outHistory.count()-1))
    def workProgress(self,cur,total):
        self.emit(QtCore.SIGNAL("encodeProgress(int,int)"),cur,total)
    def _getSetting(self):
        indir=self._ui.inPath.text()
        if not os.path.isdir(indir):
            indir=''
        outcode=self._ui.outEncode.currentText()
        for encode in self._encode_convertlist:
            if encode[0]==outcode:
                outcode=encode[1]
                break
        else:
            outcode=''
        outeol=self._ui.outEOL.currentText()
        if outeol=='DOS':
            outeol='DOS'
        elif outeol=='UNIX':
            outeol='UNIX'
        elif outeol=='MAC':
            outeol='MAC'
        else:
            outeol=''
        infileptn=self._ui.inFileType.currentIndex()
        if infileptn>0:
            inptn=re.compile(self._pattern[infileptn-1][1])
        else:
            inptn=None
        inptnname=self._ui.inFileType.currentText()
        self._log.debug('Input Dir[%s], Input Pattern[%s], Output Encode[%s], Output EOL[%s]'%(indir,inptnname,outcode,outeol))
        return indir,inptn,outcode,outeol

