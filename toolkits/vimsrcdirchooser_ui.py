# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'vimsrcdirchooser.ui'
#
# Created: Fri Jun  6 17:25:48 2014
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

class Ui_SrcDirChooser(object):
    def setupUi(self, SrcDirChooser):
        SrcDirChooser.setObjectName(_fromUtf8("SrcDirChooser"))
        SrcDirChooser.resize(343, 122)
        self.gridLayout = QtGui.QGridLayout(SrcDirChooser)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(SrcDirChooser)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.txtSrcPath = QtGui.QLineEdit(SrcDirChooser)
        self.txtSrcPath.setObjectName(_fromUtf8("txtSrcPath"))
        self.gridLayout.addWidget(self.txtSrcPath, 0, 1, 1, 1)
        self.btnChoose = QtGui.QPushButton(SrcDirChooser)
        self.btnChoose.setObjectName(_fromUtf8("btnChoose"))
        self.gridLayout.addWidget(self.btnChoose, 0, 2, 1, 1)
        self.label_2 = QtGui.QLabel(SrcDirChooser)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.label_3 = QtGui.QLabel(SrcDirChooser)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(SrcDirChooser)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 3, 0, 1, 3)
        self.txtDesc = QtGui.QLineEdit(SrcDirChooser)
        self.txtDesc.setObjectName(_fromUtf8("txtDesc"))
        self.gridLayout.addWidget(self.txtDesc, 1, 1, 1, 2)
        self.comboLang = QtGui.QComboBox(SrcDirChooser)
        self.comboLang.setObjectName(_fromUtf8("comboLang"))
        self.gridLayout.addWidget(self.comboLang, 2, 1, 1, 2)
        self.label.setBuddy(self.txtSrcPath)
        self.label_2.setBuddy(self.txtDesc)
        self.label_3.setBuddy(self.comboLang)

        self.retranslateUi(SrcDirChooser)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), SrcDirChooser.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), SrcDirChooser.reject)
        QtCore.QObject.connect(self.btnChoose, QtCore.SIGNAL(_fromUtf8("clicked()")), SrcDirChooser.onBtnChoose)
        QtCore.QMetaObject.connectSlotsByName(SrcDirChooser)

    def retranslateUi(self, SrcDirChooser):
        SrcDirChooser.setWindowTitle(_translate("SrcDirChooser", "SrcDirChooser", None))
        self.label.setText(_translate("SrcDirChooser", "Source Path", None))
        self.btnChoose.setText(_translate("SrcDirChooser", "...", None))
        self.label_2.setText(_translate("SrcDirChooser", "Description", None))
        self.label_3.setText(_translate("SrcDirChooser", "Language", None))

