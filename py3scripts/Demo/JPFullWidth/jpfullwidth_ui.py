# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'jpfullwidth.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_JPFullWidthDialog(object):
    def setupUi(self, JPFullWidthDialog):
        JPFullWidthDialog.setObjectName(_fromUtf8("JPFullWidthDialog"))
        JPFullWidthDialog.resize(400, 100)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/icon/jpfullwidth.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        JPFullWidthDialog.setWindowIcon(icon)
        self.gridLayout = QtGui.QGridLayout(JPFullWidthDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(JPFullWidthDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.editHalf = QtGui.QLineEdit(JPFullWidthDialog)
        self.editHalf.setObjectName(_fromUtf8("editHalf"))
        self.gridLayout.addWidget(self.editHalf, 0, 1, 1, 1)
        self.btnPaste = QtGui.QPushButton(JPFullWidthDialog)
        self.btnPaste.setObjectName(_fromUtf8("btnPaste"))
        self.gridLayout.addWidget(self.btnPaste, 0, 2, 1, 1)
        self.label_2 = QtGui.QLabel(JPFullWidthDialog)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.editFull = QtGui.QLineEdit(JPFullWidthDialog)
        self.editFull.setEnabled(True)
        self.editFull.setReadOnly(True)
        self.editFull.setObjectName(_fromUtf8("editFull"))
        self.gridLayout.addWidget(self.editFull, 1, 1, 1, 1)
        self.btnCopy = QtGui.QPushButton(JPFullWidthDialog)
        self.btnCopy.setObjectName(_fromUtf8("btnCopy"))
        self.gridLayout.addWidget(self.btnCopy, 1, 2, 1, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.checkTranslate = QtGui.QCheckBox(JPFullWidthDialog)
        self.checkTranslate.setChecked(True)
        self.checkTranslate.setObjectName(_fromUtf8("checkTranslate"))
        self.horizontalLayout.addWidget(self.checkTranslate)
        self.checkCopy = QtGui.QCheckBox(JPFullWidthDialog)
        self.checkCopy.setChecked(True)
        self.checkCopy.setObjectName(_fromUtf8("checkCopy"))
        self.horizontalLayout.addWidget(self.checkCopy)
        self.gridLayout.addLayout(self.horizontalLayout, 2, 1, 1, 1)
        self.btnTranslate = QtGui.QPushButton(JPFullWidthDialog)
        self.btnTranslate.setObjectName(_fromUtf8("btnTranslate"))
        self.gridLayout.addWidget(self.btnTranslate, 2, 2, 1, 1)
        self.label.setBuddy(self.editHalf)
        self.label_2.setBuddy(self.editFull)

        self.retranslateUi(JPFullWidthDialog)
        QtCore.QObject.connect(self.btnPaste, QtCore.SIGNAL(_fromUtf8("clicked()")), JPFullWidthDialog.onBtnPaste)
        QtCore.QObject.connect(self.btnCopy, QtCore.SIGNAL(_fromUtf8("clicked()")), JPFullWidthDialog.onBtnCopy)
        QtCore.QObject.connect(self.btnTranslate, QtCore.SIGNAL(_fromUtf8("clicked()")), JPFullWidthDialog.onBtnTranslate)
        QtCore.QMetaObject.connectSlotsByName(JPFullWidthDialog)

    def retranslateUi(self, JPFullWidthDialog):
        JPFullWidthDialog.setWindowTitle(_translate("JPFullWidthDialog", "JPFullWidth", None))
        self.label.setText(_translate("JPFullWidthDialog", "HalfWidth", None))
        self.btnPaste.setText(_translate("JPFullWidthDialog", "Paste", None))
        self.label_2.setText(_translate("JPFullWidthDialog", "FullWidth", None))
        self.btnCopy.setText(_translate("JPFullWidthDialog", "Copy", None))
        self.checkTranslate.setText(_translate("JPFullWidthDialog", "Auto Translate", None))
        self.checkCopy.setText(_translate("JPFullWidthDialog", "Auto Copy", None))
        self.btnTranslate.setText(_translate("JPFullWidthDialog", "Translate", None))

import jpfullwidth_rc
