from PyQt4 import QtGui,QtCore
import pickle
import logutil
import vimconfig
import vimthread
import vim_ui
import vimsrcdirchooser_ui

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class MainWidget(QtGui.QWidget):
    D_STR_LISTFILE='vimlist.dat'
    def setupUi(self):
        self._ui=vim_ui.Ui_Vim()
        self._ui.setupUi(self)
        self._log=logutil.LogUtil().logger('VimMainWidget')
        config=vimconfig.VimConfig()
        self._tool=config.tools()
        self._pattern=config.patterns()
        self.loadProjects()
        for item in self.projlist:
            txt="%-24s%-8s%s"%(item[0],item[2],item[1])
            self._ui.listProject.addItem(txt)
        self._vim=vimthread.VimThread(self._tool.get('vim',''))
        self._tag=vimthread.VimTagThread(self._tool.get('cscope',''),self._tool.get('ctags',''))
        self.connect(self._tag,QtCore.SIGNAL("threadStatus(const QString&)"),self.threadStatus)
        self.connect(self._tag,QtCore.SIGNAL("finished()"),self.threadFinished)
    def onBtnAdd(self):
        dirchooser=SrcDirChooser()
        dirchooser.setupUi()
        dirchooser.exec()
        if QtGui.QDialog.Accepted == dirchooser.result():
            srcpath,srcdesc,srclang=dirchooser.info()
            self.projlist.append((srcdesc,srcpath,srclang))
            self.saveProjects()
            txt="%-24s%-8s%s"%(srcdesc,srclang,srcpath)
            self._ui.listProject.addItem(txt)
            # ToDo: generate tag-files
            self.generateTags(srcpath,srclang)
    def onBtnDelete(self):
        row=self._ui.listProject.currentRow()
        if row>=0:
            self._log.debug("Row: %d"%(row,))
            self._ui.listProject.takeItem(row)
            srcpath=self.projlist[row][1]
            srcdir=QtCore.QDir(srcpath)
            for tag in ("tags",'cscope.out','cscope.cache'):
                tagfile=QtCore.QFileInfo(srcdir,tag)
                if tagfile.exists():
                    QtCore.QFile.remove(tagfile.filePath())
            del self.projlist[row]
            self.saveProjects()
    def onBtnUpdate(self):
        row=self._ui.listProject.currentRow()
        if row>=0:
            srcdesc,srcpath,srclang=self.projlist[row]
            srcdir=QtCore.QDir(srcpath)
            for tag in ("tags",'cscope.out','cscope.cache'):
                tagfile=QtCore.QFileInfo(srcdir,tag)
                if tagfile.exists():
                    QtCore.QFile.remove(tagfile.filePath())
            self.generateTags(srcpath,srclang)
    def onItemDoubleClicked(self,item):
        idx=self._ui.listProject.row(item)
        self._vim.setSrcPath(self.projlist[idx][1])
        self._vim.start()
    def onRowChanged(self,row):
        if row>=0:
            self._ui.btnDelete.setEnabled(True)
            self._ui.listProject.setCurrentRow(row)
        else:
            self._ui.btnDelete.setEnabled(False)
    def threadStatus(self,status):
        self._ui.txtStatus.setText(status)
    def threadFinished(self):
        self._ui.btnAdd.setEnabled(True)
        self._ui.btnUpdate.setEnabled(True)
    def loadProjects(self):
        if QtCore.QFile.exists(self.D_STR_LISTFILE):
            with open(self.D_STR_LISTFILE,'rb') as fd:
                self.projlist=pickle.load(fd)
        else:
            self.projlist=[]
    def saveProjects(self):
        with open(self.D_STR_LISTFILE,'wb') as fd:
            pickle.dump(self.projlist,fd)
    def generateTags(self,srcpath,srclang):
        self._ui.btnAdd.setEnabled(False)
        self._ui.btnUpdate.setEnabled(False)
        filepat='.*'
        for pat in self._pattern:
            if pat[0]==srclang:
                filepat=pat[1]
                break
        self._tag.setSrcPath(srcpath,filepat)
        self._tag.start()

class SrcDirChooser(QtGui.QDialog):
    def setupUi(self):
        self._ui=vimsrcdirchooser_ui.Ui_SrcDirChooser()
        self._ui.setupUi(self)
        config=vimconfig.VimConfig()
        for patkey,patval in config.patterns():
            self._ui.comboLang.addItem(patkey)
    def onBtnChoose(self):
        fdialog=QtGui.QFileDialog.getExistingDirectory(self,_translate("SrcDirChooser","Source Folder",None))
        if QtCore.QFile.exists(fdialog):
            self._ui.txtSrcPath.setText(fdialog)
    def info(self):
        srcpath,srcdesc=self._ui.txtSrcPath.text(),self._ui.txtDesc.text()
        srclang=self._ui.comboLang.currentText()
        return srcpath,srcdesc,srclang

