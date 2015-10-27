# -*- coding: utf-8 -*-
from PyQt4 import QtGui,QtCore
import os
import shutil
import toolbox_ui
from collectscript import logutil, encodechanger, jp2fullwidth, multithread, guess

class MainDialog(QtGui.QDialog):
    def setupUi(self):
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
        self.act_encode = encodechanger.EncodeChanger()
    def onBtnDstDir(self):
        self._ui.editDstDir.setText(QtGui.QFileDialog.getExistingDirectory(self))
    def onBtnActionDirEncode(self):
        srcdir = self._ui.filefilter._core.getSrcdir()
        dstdir = self._ui.editDstDir.text()
        if srcdir and dstdir:
            self._ui.listWidget.addItem("Start change encode...")
            self._worker = multithread.MultiThread(3)
            self._worker.register(self._actionCopy,'Copy')
            self._worker.register(self._actionEncode,'Encode')
            self.setDisabled(True)
            self._worker.start()
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
            self._worker = multithread.MultiThread(3)
            self._worker.register(self._actionCopy,'Copy')
            self._worker.register(self._actionKatakana,'Katakana')
            self.setDisabled(True)
            self._worker.start()
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
    @staticmethod
    def _mkdir(filepath):
        head, tail = os.path.split(filepath)
        if os.path.isdir(head):
            if os.path.isfile(filepath):
                os.remove(filepath)
        else:
            os.makedirs(head, exist_ok=True)

if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    ##Change UI Language based on system
    #locale = QtCore.QLocale.system()
    #trans = QtCore.QTranslator()
    #trans.load("toolbox_{}.qm".format(locale.name()))
    #app.installTranslator(trans)

    mw  = MainDialog()
    mw.setupUi()
    mw.show()
    app.exec_()

