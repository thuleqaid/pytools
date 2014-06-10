# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'encode.ui'
#
# Created: Mon Mar 31 15:57:48 2014
#      by: PyQt4 UI code generator 4.9.6
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

class Ui_Encode(object):
    def setupUi(self, Encode):
        Encode.setObjectName(_fromUtf8("Encode"))
        Encode.resize(311, 328)
        self.gridLayout = QtGui.QGridLayout(Encode)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label = QtGui.QLabel(Encode)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        self.inPath = QtGui.QLineEdit(Encode)
        self.inPath.setObjectName(_fromUtf8("inPath"))
        self.horizontalLayout.addWidget(self.inPath)
        self.btnChoose = QtGui.QPushButton(Encode)
        self.btnChoose.setObjectName(_fromUtf8("btnChoose"))
        self.horizontalLayout.addWidget(self.btnChoose)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 2)
        self.outHistory = QtGui.QListWidget(Encode)
        self.outHistory.setObjectName(_fromUtf8("outHistory"))
        self.gridLayout.addWidget(self.outHistory, 3, 0, 1, 2)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.btnRestore = QtGui.QPushButton(Encode)
        self.btnRestore.setObjectName(_fromUtf8("btnRestore"))
        self.horizontalLayout_3.addWidget(self.btnRestore)
        self.btnChange = QtGui.QPushButton(Encode)
        self.btnChange.setObjectName(_fromUtf8("btnChange"))
        self.horizontalLayout_3.addWidget(self.btnChange)
        self.gridLayout.addLayout(self.horizontalLayout_3, 4, 0, 1, 1)
        self.inIgnore = QtGui.QCheckBox(Encode)
        self.inIgnore.setChecked(True)
        self.inIgnore.setObjectName(_fromUtf8("inIgnore"))
        self.gridLayout.addWidget(self.inIgnore, 4, 1, 1, 1)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.label_2 = QtGui.QLabel(Encode)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.horizontalLayout_2.addWidget(self.label_2)
        self.outEncode = QtGui.QComboBox(Encode)
        self.outEncode.setObjectName(_fromUtf8("outEncode"))
        self.horizontalLayout_2.addWidget(self.outEncode)
        self.label_3 = QtGui.QLabel(Encode)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.horizontalLayout_2.addWidget(self.label_3)
        self.outEOL = QtGui.QComboBox(Encode)
        self.outEOL.setObjectName(_fromUtf8("outEOL"))
        self.outEOL.addItem(_fromUtf8(""))
        self.outEOL.addItem(_fromUtf8(""))
        self.outEOL.addItem(_fromUtf8(""))
        self.horizontalLayout_2.addWidget(self.outEOL)
        self.gridLayout.addLayout(self.horizontalLayout_2, 1, 0, 1, 2)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.label_4 = QtGui.QLabel(Encode)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.horizontalLayout_4.addWidget(self.label_4)
        self.inFileType = QtGui.QComboBox(Encode)
        self.inFileType.setObjectName(_fromUtf8("inFileType"))
        self.inFileType.addItem(_fromUtf8(""))
        self.horizontalLayout_4.addWidget(self.inFileType)
        self.gridLayout.addLayout(self.horizontalLayout_4, 2, 0, 1, 2)
        self.label.setBuddy(self.inPath)
        self.label_2.setBuddy(self.outEncode)
        self.label_3.setBuddy(self.outEOL)
        self.label_4.setBuddy(self.inFileType)

        self.retranslateUi(Encode)
        QtCore.QObject.connect(self.btnChoose, QtCore.SIGNAL(_fromUtf8("clicked()")), Encode.onBtnChoose)
        QtCore.QObject.connect(self.btnRestore, QtCore.SIGNAL(_fromUtf8("clicked()")), Encode.onBtnRestore)
        QtCore.QObject.connect(self.btnChange, QtCore.SIGNAL(_fromUtf8("clicked()")), Encode.onBtnChange)
        QtCore.QMetaObject.connectSlotsByName(Encode)

    def retranslateUi(self, Encode):
        Encode.setWindowTitle(_translate("Encode", "Encode", None))
        self.label.setText(_translate("Encode", "Source Folder", None))
        self.btnChoose.setText(_translate("Encode", "Choose...", None))
        self.btnRestore.setText(_translate("Encode", "Restore", None))
        self.btnChange.setText(_translate("Encode", "Change", None))
        self.inIgnore.setText(_translate("Encode", "Ignore VCS Files", None))
        self.label_2.setText(_translate("Encode", "Encoding", None))
        self.label_3.setText(_translate("Encode", "LineTerminator", None))
        self.outEOL.setItemText(0, _translate("Encode", "DOS", None))
        self.outEOL.setItemText(1, _translate("Encode", "UNIX", None))
        self.outEOL.setItemText(2, _translate("Encode", "MAC", None))
        self.label_4.setText(_translate("Encode", "FilePattern", None))
        self.inFileType.setItemText(0, _translate("Encode", "All Files(*.*)", None))

