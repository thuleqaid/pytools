# -*- coding: utf-8 -*-
from PyQt4 import QtGui,QtCore
import os
import sys
import shutil
import subprocess
import toolbox_ui
from collectscript import logutil, encodechanger, jp2fullwidth, multithread, guess, tagparser, source_diff

if hasattr(sys,'frozen'):
    _selffile = sys.executable
else:
    _selffile = __file__
class MainDialog(QtGui.QDialog):
    def setupUi(self):
        self._selfpath = os.path.abspath(logutil.scriptPath(_selffile))
        self._ui = toolbox_ui.Ui_ToolBoxDialog()
        self._ui.setupUi(self)
        self._ui.comboEncode_DirEncode.addItem('UTF-8(BOM)','utf_8_sig')
        self._ui.comboEncode_DirEncode.addItem('ShiftJIS','cp932')
        self._ui.comboEncode_DirEncode.addItem('GBK','cp936')
        self._ui.comboEncode_DirEncode.addItem('UTF-8','utf_8')
        self._ui.comboNewline_DirEncode.addItem('System',None)
        self._ui.comboNewline_DirEncode.addItem('Dos','dos')
        self._ui.comboNewline_DirEncode.addItem('Unix','unix')
        self._ui.comboNewline_DirEncode.addItem('Mac','mac')
        self._ui.filefilter._ui.comboIn1.setCurrentIndex(1)
        self._ui.filefilter._ui.editIn1.setText('.*')
        # Remove Text and File Tab
        self._ui.tabWidget.removeTab(0)
        self._ui.tabWidget.removeTab(0)
        self.act_encode = encodechanger.EncodeChanger()
        self.act_cscope = None
        self._worker = multithread.MultiThread(3, True)
        self._worker.register(self._actionCopy,'Copy')
        self._worker.register(self._actionEncode,'Encode')
        self._worker.register(self._actionKatakana,'Katakana')
        self._worker.register(self._actionCscope,'Cscope')
        self._worker.register(self._actionCtags,'Ctags')
        self._worker.start()
    # Tab_Folder
    def onBtnDstDir(self):
        self._ui.editDstDir.setText(QtGui.QFileDialog.getExistingDirectory(self))
    def onBtnActionDirEncode(self):
        srcdir = self._ui.filefilter._core.getSrcdir()
        dstdir = self._ui.editDstDir.text()
        if srcdir and dstdir:
            self._ui.listWidget.addItem("Start change encode...")
            self.setDisabled(True)
            for item in self._ui.filefilter._core.getHitFiles():
                self._worker.addJob((srcdir, dstdir, item),'Encode')
            if self._ui.comboUnhit.currentIndex() == 1:
                for item in self._ui.filefilter._core.getUnHitFiles():
                    self._worker.addJob((srcdir, dstdir, item),'Copy')
            if self._ui.comboExclude.currentIndex() == 1:
                for item in self._ui.filefilter._core.getExcludeFiles():
                    self._worker.addJob((srcdir, dstdir, item),'Copy')
            self._worker.join()
            self.setDisabled(False)
            self._ui.listWidget.addItem("Finished.")
    def onBtnActionDirKatakana(self):
        srcdir = self._ui.filefilter._core.getSrcdir()
        dstdir = self._ui.editDstDir.text()
        if srcdir and dstdir:
            self._ui.listWidget.addItem("Start change katakana...")
            self.setDisabled(True)
            for item in self._ui.filefilter._core.getHitFiles():
                self._worker.addJob((srcdir, dstdir, item),'Katakana')
            if self._ui.comboUnhit.currentIndex() == 1:
                for item in self._ui.filefilter._core.getUnHitFiles():
                    self._worker.addJob((srcdir, dstdir, item),'Copy')
            if self._ui.comboExclude.currentIndex() == 1:
                for item in self._ui.filefilter._core.getExcludeFiles():
                    self._worker.addJob((srcdir, dstdir, item),'Copy')
            self._worker.join()
            self.setDisabled(False)
            self._ui.listWidget.addItem("Finished.")
    # Tab_Source
    def onBtnNewSource(self):
        self._ui.editNewSource.setText(QtGui.QFileDialog.getExistingDirectory(self))
    def onBtnBaseSource(self):
        self._ui.editBaseSource.setText(QtGui.QFileDialog.getExistingDirectory(self))
    def onBtnGenerateTag(self):
        srcdir = self._ui.editNewSource.text()
        if srcdir:
            self._ui.listWidget_Source.addItem("Start generate tag files...")
            self.setDisabled(True)
            os.chdir(srcdir)
            self._worker.addJob((srcdir,),'Cscope')
            #self._worker.addJob((srcdir,),'Ctags')
            self._worker.join()
            os.chdir(self._selfpath)
            self.setDisabled(False)
            self._ui.listWidget_Source.addItem("Finished.")
    def onBtnExtractFunc(self):
        srcdir = self._ui.editNewSource.text()
        if srcdir:
            if os.path.isfile(os.path.join(srcdir,'cscope.out')):
                self._ui.listWidget_Source.addItem("Start extract function info...")
                self.setDisabled(True)
                self.act_cscope = tagparser.CscopeParser(os.path.join(srcdir,'cscope.out'))
                fields = []
                if self._ui.checkFilePath.checkState() == QtCore.Qt.Checked:
                    fields.append('Path')
                if self._ui.checkStartline.checkState() == QtCore.Qt.Checked:
                    fields.append('StartLine')
                if self._ui.checkStopline.checkState() == QtCore.Qt.Checked:
                    fields.append('StopLine')
                if self._ui.checkSubFuncCount.checkState() == QtCore.Qt.Checked:
                    fields.append('SubCount')
                if self._ui.checkSubFuncName.checkState() == QtCore.Qt.Checked:
                    fields.append('SubName')
                if self._ui.checkCondition.checkState() == QtCore.Qt.Checked:
                    fields.append('Condition')
                if self._ui.checkLoop.checkState() == QtCore.Qt.Checked:
                    fields.append('Loop')
                if self._ui.checkLines.checkState() == QtCore.Qt.Checked:
                    fields.append('Lines')
                if self._ui.checkFuncID.checkState() == QtCore.Qt.Checked:
                    fields.append('FunctionID')
                if self._ui.checkFuncName.checkState() == QtCore.Qt.Checked:
                    fields.append('FunctionName')
                self.act_cscope.outputFuncInfo(os.path.join(srcdir,'funcinfo.txt'),fields)
                self.act_cscope = None
                self.setDisabled(False)
                self._ui.listWidget_Source.addItem("Finished.")
                subprocess.Popen(['explorer.exe',os.path.normpath(srcdir)],shell=True)
            else:
                self._ui.listWidget_Source.addItem("Tag files not found.")
    def onBtnExtractFuncDiff(self):
        newdir = self._ui.editNewSource.text()
        olddir = self._ui.editBaseSource.text()
        if newdir and olddir and os.path.isdir(newdir) and os.path.isdir(olddir):
            if os.path.isfile(os.path.join(newdir,'cscope.out')):
                self._ui.listWidget_Source.addItem("Start extract function info...")
                sd = source_diff.SourceDiff(olddir, newdir)
                fields = []
                if self._ui.checkFilePath.checkState() == QtCore.Qt.Checked:
                    fields.append('Path')
                if self._ui.checkStartline.checkState() == QtCore.Qt.Checked:
                    fields.append('StartLine')
                if self._ui.checkStopline.checkState() == QtCore.Qt.Checked:
                    fields.append('StopLine')
                if self._ui.checkSubFuncCount.checkState() == QtCore.Qt.Checked:
                    fields.append('SubCount')
                if self._ui.checkSubFuncName.checkState() == QtCore.Qt.Checked:
                    fields.append('SubName')
                if self._ui.checkCondition.checkState() == QtCore.Qt.Checked:
                    fields.append('Condition')
                if self._ui.checkLoop.checkState() == QtCore.Qt.Checked:
                    fields.append('Loop')
                if self._ui.checkLines.checkState() == QtCore.Qt.Checked:
                    fields.append('Lines')
                if self._ui.checkFuncID.checkState() == QtCore.Qt.Checked:
                    fields.append('FunctionID')
                if self._ui.checkFuncName.checkState() == QtCore.Qt.Checked:
                    fields.append('FunctionName')
                sd._tag.outputFuncInfo(os.path.join(newdir,'funcinfo.txt'),fields,[y for x in sd.getDiffFuncs().items() for y in x[1]])
                sd.report(os.path.join(newdir,'diffinfo.txt'))
                self._ui.listWidget_Source.addItem("Finished.")
                subprocess.Popen(['explorer.exe',os.path.normpath(newdir)],shell=True)
            else:
                self._ui.listWidget_Source.addItem("Tag files not found.")
    # private functions
    def _actionCopy(self, param):
        srcdir = param[0]
        dstdir = param[1]
        filename = param[2]
        inpath = os.path.join(srcdir, filename)
        outpath = os.path.join(dstdir, filename)
        self._mkdir(outpath)
        shutil.copy(inpath, outpath)
    def _actionEncode(self, param):
        srcdir = param[0]
        dstdir = param[1]
        filename = param[2]
        srcfile = os.path.join(srcdir,filename)
        dstfile = os.path.join(dstdir,filename)
        encode = self._ui.comboEncode_DirEncode.itemData(self._ui.comboEncode_DirEncode.currentIndex())
        newline = self._ui.comboNewline_DirEncode.itemData(self._ui.comboNewline_DirEncode.currentIndex())
        ret = self.act_encode.change(srcfile, dstfile, encode, newline)
        if not ret:
            self._ui.listWidget.addItem("  Item [{}] fails.".format(filename))
            if self._ui.comboFail.currentIndex() == 1:
                self._worker.addJob((srcdir, dstdir, filename),'Copy')
    def _actionKatakana(self, param):
        srcdir = param[0]
        dstdir = param[1]
        filename = param[2]
        srcfile = os.path.join(srcdir,filename)
        dstfile = os.path.join(dstdir,filename)
        incode = guess.guessEncode(srcfile)[0]
        if incode:
            fh = open(srcfile, 'r', encoding=incode)
            data = fh.read()
            fh.close()
            newdata = jp2fullwidth.fullwidth(data)
            self._mkdir(dstfile)
            fh = open(dstfile, 'w', encoding=incode)
            fh.write(newdata)
            fh.close()
        else:
            self._ui.listWidget.addItem("  Item [{}] fails.".format(filename))
            if self._ui.comboFail.currentIndex() == 1:
                self._worker.addJob((srcdir, dstdir, filename),'Copy')
    def _actionCscope(self, param):
        srcdir = param[0]
        params = []
        params.append(os.path.join(self._selfpath,'bin','cscope.exe'))
        params.append('-Rbcu')
        self._runCmd(params)
    def _actionCtags(self, param):
        srcdir = param[0]
        params = []
        params.append(os.path.join(self._selfpath,'bin','ctags.exe'))
        params.append('-R')
        self._runCmd(params)
    @staticmethod
    def _runCmd(param):
        ret = True
        try:
            subprocess.check_call(param)
        except subprocess.CalledProcessError as e:
            ret = False
        return ret
    @staticmethod
    def _mkdir(filepath):
        head, tail = os.path.split(filepath)
        if os.path.isdir(head):
            if os.path.isfile(filepath):
                os.remove(filepath)
        else:
            os.makedirs(head, exist_ok=True)

if __name__ == '__main__':
    logutil.logConf()
    app = QtGui.QApplication(sys.argv)
    #Change UI Language based on system
    locale = QtCore.QLocale.system()
    trans = QtCore.QTranslator()
    trans.load(os.path.join(logutil.scriptPath(_selffile),'qm',"toolbox_{}.qm".format(locale.name())))
    app.installTranslator(trans)

    mw  = MainDialog()
    mw.setupUi()
    mw.show()
    app.exec_()

