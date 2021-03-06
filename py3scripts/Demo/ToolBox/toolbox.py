# -*- coding: utf-8 -*-
try:
    from PyQt4 import QtGui,QtCore
    from PyQt4.QtGui import QDialog, QApplication
except:
    from PyQt5 import QtGui,QtCore
    from PyQt5.QtWidgets import QDialog, QApplication
import os
import sys
import shutil
import subprocess
import toolbox_ui
from collectscript import logutil, encodechanger, jp2fullwidth, multithread, guess, tagparser, source_diff
import analyze

if hasattr(sys,'frozen'):
    _selffile = sys.executable
else:
    _selffile = __file__
LOGCONFIG = os.path.join(logutil.scriptPath(_selffile), 'logging.conf')

class MainDialog(QDialog):
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
            self._ui.listWidget_Source.addItem("Start extract function info...")
            self.setDisabled(True)
            self.act_cscope = tagparser.CscopeParser(os.path.join(srcdir,'cscope.out'),sourceparser=tagparser.cscopeSourceParserEPS)
            fields = []
            if self._ui.checkFilePath.checkState() == QtCore.Qt.Checked:
                fields.append('Path')
            if self._ui.checkScope.checkState() == QtCore.Qt.Checked:
                fields.append('Scope')
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
            if self._ui.checkPrototype.checkState() == QtCore.Qt.Checked:
                fields.append('Prototype')
            if self._ui.checkLines.checkState() == QtCore.Qt.Checked:
                fields.append('SourceCount')
            if self._ui.checkFuncID.checkState() == QtCore.Qt.Checked:
                fields.append('FunctionID')
            if self._ui.checkFuncName.checkState() == QtCore.Qt.Checked:
                fields.append('FunctionName')
            if self._ui.checkInline.checkState() == QtCore.Qt.Checked:
                fields.append('Inline')
            self.act_cscope.outputFuncInfo(os.path.join(srcdir,'funcinfo.txt'),fields)
            self.act_cscope = None
            self.setDisabled(False)
            self._ui.listWidget_Source.addItem("Finished.")
            subprocess.Popen(['explorer.exe',os.path.normpath(srcdir)],shell=True)
    def onBtnExtractFuncDiff(self):
        newdir = self._ui.editNewSource.text()
        olddir = self._ui.editBaseSource.text()
        if newdir and olddir and os.path.isdir(newdir) and os.path.isdir(olddir):
            self._ui.listWidget_Source.addItem("Start extract function info...")
            sd = source_diff.SourceDiff(olddir, newdir)
            fields = []
            if self._ui.checkFilePath.checkState() == QtCore.Qt.Checked:
                fields.append('Path')
            if self._ui.checkScope.checkState() == QtCore.Qt.Checked:
                fields.append('Scope')
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
            if self._ui.checkPrototype.checkState() == QtCore.Qt.Checked:
                fields.append('Prototype')
            if self._ui.checkLines.checkState() == QtCore.Qt.Checked:
                fields.append('SourceCount')
            if self._ui.checkFuncID.checkState() == QtCore.Qt.Checked:
                fields.append('FunctionID')
            if self._ui.checkFuncName.checkState() == QtCore.Qt.Checked:
                fields.append('FunctionName')
            if self._ui.checkInline.checkState() == QtCore.Qt.Checked:
                fields.append('Inline')
            sd._tag.outputFuncInfo(os.path.join(newdir,'funcinfo.txt'),fields,[y for x in sd.getDiffFuncs().items() for y in x[1]])
            sd.report(os.path.join(newdir,'diffinfo.txt'))
            self._ui.listWidget_Source.addItem("Finished.")
            subprocess.Popen(['explorer.exe',os.path.normpath(newdir)],shell=True)
    # Tab_Inline
    def onBtnInlineSource(self):
        self._ui.editInlineSource.setText(QtGui.QFileDialog.getExistingDirectory(self))
    def onBtnInlineFunction(self):
        self._ui.editInlineFunction.setText(QtGui.QFileDialog.getOpenFileName(self))
    def onBtnInlineInline(self):
        self._ui.editInlineInline.setText(QtGui.QFileDialog.getSaveFileName(self))
    def onBtnInlineMetric(self):
        self._ui.editInlineMetric.setText(QtGui.QFileDialog.getSaveFileName(self))
    def onBtnInlineTree(self):
        self._ui.editInlineTree.setText(QtGui.QFileDialog.getSaveFileName(self))
    def onBtnInlineAdjust(self):
        self._ui.editInlineAdjust.setText(QtGui.QFileDialog.getSaveFileName(self))
    def onBtnInlineGenerateInline(self):
        srcroot = self._ui.editInlineSource.text()
        targets = self._ui.editInlineFunction.text()
        inlines = self._ui.editInlineInline.text()
        if srcroot and targets and inlines:
            ei = analyze.ExtractInline(srcroot)
            ei.setTargetFile(targets)
            ei.outputInline(inlines)
        else:
            QtGui.QMessageBox.warning(self, "Warning", "Missing Source Dir/Function List/Tree File")
    def onBtnInlineGenerateMetric(self):
        srcroot = self._ui.editInlineSource.text()
        targets = self._ui.editInlineFunction.text()
        outfile = self._ui.editInlineMetric.text()
        if srcroot and targets and outfile:
            ei = analyze.ExtractInline(srcroot)
            ei.setTargetFile(targets)
            inlines = self._ui.editInlineInline.text()
            if inlines:
                ei.setInlineFile(inlines)
            ei.outputMetric(outfile)
        else:
            QtGui.QMessageBox.warning(self, "Warning", "Missing Source Dir/Function List/Tree File")
    def onBtnInlineGenerateTree(self):
        srcroot = self._ui.editInlineSource.text()
        targets = self._ui.editInlineFunction.text()
        outfile = self._ui.editInlineTree.text()
        if srcroot and targets and outfile:
            ei = analyze.ExtractInline(srcroot)
            ei.setTargetFile(targets)
            inlines = self._ui.editInlineInline.text()
            if inlines:
                ei.setInlineFile(inlines)
            ei.outputTree(outfile)
        else:
            QtGui.QMessageBox.warning(self, "Warning", "Missing Source Dir/Function List/Tree File")
    def onBtnInlineGenerateAdjust(self):
        treefile = self._ui.editInlineTree.text()
        metricfile = self._ui.editInlineMetric.text()
        outfile = self._ui.editInlineAdjust.text()
        if treefile and metricfile and outfile:
            sm = analyze.SumMetrics(treefile)
            sm.setMetrics(metricfile)
            sm.outputMetrics(outfile)
        else:
            QtGui.QMessageBox.warning(self, "Warning", "Missing Metric File/Tree File/Output File")
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
        fullpath = os.path.join(srcdir,'cscope.out')
        os.unlink(fullpath)
        gen_cscope = tagparser.CscopeParser(fullpath,sourceparser=tagparser.cscopeSourceParserEPS)
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
    logutil.logConf(LOGCONFIG)
    logutil.LogUtil(LOGCONFIG)
    app = QApplication(sys.argv)
    #Change UI Language based on system
    locale = QtCore.QLocale.system()
    #print(locale.name())
    trans = QtCore.QTranslator()
    trans.load(os.path.join(logutil.scriptPath(_selffile),'qm',"toolbox_{}.qm".format(locale.name())))
    app.installTranslator(trans)

    mw  = MainDialog()
    mw.setupUi()
    mw.show()
    app.exec_()

