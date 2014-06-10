# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'vim.ui'
#
# Created: Mon Jun  9 14:49:56 2014
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

class Ui_Vim(object):
    def setupUi(self, Vim):
        Vim.setObjectName(_fromUtf8("Vim"))
        Vim.resize(274, 267)
        self.verticalLayout = QtGui.QVBoxLayout(Vim)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.btnAdd = QtGui.QPushButton(Vim)
        self.btnAdd.setObjectName(_fromUtf8("btnAdd"))
        self.horizontalLayout.addWidget(self.btnAdd)
        self.btnDelete = QtGui.QPushButton(Vim)
        self.btnDelete.setEnabled(False)
        self.btnDelete.setObjectName(_fromUtf8("btnDelete"))
        self.horizontalLayout.addWidget(self.btnDelete)
        self.btnUpdate = QtGui.QPushButton(Vim)
        self.btnUpdate.setObjectName(_fromUtf8("btnUpdate"))
        self.horizontalLayout.addWidget(self.btnUpdate)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.listProject = QtGui.QListWidget(Vim)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("FixedSys"))
        self.listProject.setFont(font)
        self.listProject.setObjectName(_fromUtf8("listProject"))
        self.verticalLayout.addWidget(self.listProject)
        self.txtStatus = QtGui.QLineEdit(Vim)
        self.txtStatus.setEnabled(False)
        self.txtStatus.setObjectName(_fromUtf8("txtStatus"))
        self.verticalLayout.addWidget(self.txtStatus)

        self.retranslateUi(Vim)
        QtCore.QObject.connect(self.btnAdd, QtCore.SIGNAL(_fromUtf8("clicked()")), Vim.onBtnAdd)
        QtCore.QObject.connect(self.btnDelete, QtCore.SIGNAL(_fromUtf8("clicked()")), Vim.onBtnDelete)
        QtCore.QObject.connect(self.btnUpdate, QtCore.SIGNAL(_fromUtf8("clicked()")), Vim.onBtnUpdate)
        QtCore.QObject.connect(self.listProject, QtCore.SIGNAL(_fromUtf8("itemDoubleClicked(QListWidgetItem*)")), Vim.onItemDoubleClicked)
        QtCore.QObject.connect(self.listProject, QtCore.SIGNAL(_fromUtf8("currentRowChanged(int)")), Vim.onRowChanged)
        QtCore.QMetaObject.connectSlotsByName(Vim)

    def retranslateUi(self, Vim):
        Vim.setWindowTitle(_translate("Vim", "Vim", None))
        self.btnAdd.setText(_translate("Vim", "Add", None))
        self.btnDelete.setText(_translate("Vim", "Delete", None))
        self.btnUpdate.setText(_translate("Vim", "Update", None))

