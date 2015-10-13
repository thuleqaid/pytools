# -*- coding: utf-8 -*-
from PyQt4 import QtGui,QtCore
import sys
import jp2fullwidth
import jpfullwidth_ui

class MainDialog(QtGui.QDialog):
    def setupUi(self):
        self._ui = jpfullwidth_ui.Ui_JPFullWidthDialog()
        self._ui.setupUi(self)
        self._clip = QtGui.QApplication.clipboard()
    def onBtnPaste(self):
        self._ui.editHalf.setText(self._clip.text())
        if self._ui.checkTranslate.checkState() == QtCore.Qt.Checked:
            self.onBtnTranslate()
    def onBtnCopy(self):
        self._clip.setText(self._ui.editFull.text())
    def onBtnTranslate(self):
        self._ui.editFull.setText(jp2fullwidth.fullwidth(self._ui.editHalf.text()))
        if self._ui.checkCopy.checkState() == QtCore.Qt.Checked:
            self.onBtnCopy()

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    # Change UI Language based on system
    locale = QtCore.QLocale.system()
    trans = QtCore.QTranslator()
    trans.load(":/qm/jpfullwidth_{}.qm".format(locale.name()))
    app.installTranslator(trans)

    mw  = MainDialog()
    mw.setupUi()
    mw.show()
    app.exec_()

