# -*- coding: utf-8 -*-
from PyQt4 import QtGui,QtCore
import sys
from argparse import ArgumentParser
import logutil
import encodechanger
import encodechanger_ui

FILTER_LIST = (('C/C++ Files',r'\.(c|c\+\+|cc|cp|cpp|cxx|h|h\+\+|hh|hp|hpp|hxx)$'),
               ('Python Files', r'\.(py|pyx|pxd|pxi|scons)$'),
              )
ENCODE_IN_LIST = ('cp932', 'cp936')
ENCODE_OUT_LIST = (('UTF-8', 'utf-8'),
                   ('ShiftJIS', 'cp932'),
                   ('GBK', 'cp936'),
                   ('UTF-8(BOM)', 'utf_8_sig'),
                  )
class MainDialog(QtGui.QDialog):
    def setupUi(self):
        self._ui = encodechanger_ui.Ui_EncodeChangerDialog()
        self._ui.setupUi(self)
        self._loadConfig()
    def _loadConfig(self):
        for item in FILTER_LIST:
            self._ui.comboRegex.addItem(item[0], item[1])
        self._ui.comboRegex.setCurrentIndex(1)
        for item in ENCODE_OUT_LIST:
            self._ui.comboEncode.addItem(item[0], item[1])
        self._changer = encodechanger.EncodeChanger()
        self._changer.incode = ENCODE_IN_LIST
    def onBtnSrcDir(self):
        self._ui.editSrcDir.setText(QtGui.QFileDialog.getExistingDirectory(self))
    def onBtnDstDir(self):
        self._ui.editDstDir.setText(QtGui.QFileDialog.getExistingDirectory(self))
    def onBtnPreview(self):
        self._ui.listLog.clear()
        self._changer.vcs = (self._ui.checkIgnoreVCS.checkState() == QtCore.Qt.Checked)
        self._changer.srcdir = self._ui.editSrcDir.text()
        if self._changer.error:
            self._ui.listLog.addItem('Source directory error.')
            self._ui.editSrcDir.setText(self._changer.srcdir)
        self._changer.regex = self._ui.editRegex.text()
        if self._changer.error:
            self._ui.listLog.addItem('Filter error.')
        self._ui.listAll.clear()
        for item in sorted(self._changer.fileall):
            self._ui.listAll.addItem(item)
        self._ui.listHit.clear()
        for item in sorted(self._changer.filehit):
            self._ui.listHit.addItem(item)
        self._ui.listOther.clear()
        for item in sorted(self._changer.fileother):
            self._ui.listOther.addItem(item)
    def onBtnAction(self):
        self.onBtnPreview()
        self._changer.dstdir = self._ui.editDstDir.text()
        self._changer.outcode = self._ui.comboEncode.itemData(self._ui.comboEncode.currentIndex())
        self._changer.newline = self._ui.comboNewline.currentText()
        self._changer.copyother = (self._ui.checkCopyOther.checkState() == QtCore.Qt.Checked)
        errorlist = self._changer.translate()
        if self._changer.error:
            self._ui.listLog.addItem('Finished with follow errors.')
            for item in sorted(errorlist):
                self._ui.listLog.addItem(item)
        else:
            self._ui.listLog.addItem('Finished.')
    def onComboRegex(self, idx):
        if idx > 0:
            self._ui.editRegex.setText(self._ui.comboRegex.itemData(idx))
    def onEditRegex(self, text):
        self._ui.comboRegex.setCurrentIndex(0)

if __name__ == '__main__':
    # command line options
    parser = ArgumentParser()
    parser.add_argument('-l','--log',dest='flag_log',action='store_true',default=False,help='generate log config')
    options=parser.parse_args()
    if options.flag_log:
        logutil.newConf(('EncodeChanger',))

    app = QtGui.QApplication(sys.argv)
    # Change UI Language based on system
    locale = QtCore.QLocale.system()
    trans = QtCore.QTranslator()
    trans.load(":/qm/encodechanger_{}.qm".format(locale.name()))
    app.installTranslator(trans)

    mw  = MainDialog()
    mw.setupUi()
    mw.show()
    app.exec_()

