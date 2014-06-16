# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dnsshr.ui'
#
# Created: Mon Jun 16 10:54:31 2014
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

class Ui_DNSSHR(object):
    def setupUi(self, DNSSHR):
        DNSSHR.setObjectName(_fromUtf8("DNSSHR"))
        DNSSHR.resize(274, 345)
        self.verticalLayout = QtGui.QVBoxLayout(DNSSHR)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(DNSSHR)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.txtUsername = QtGui.QLineEdit(DNSSHR)
        self.txtUsername.setObjectName(_fromUtf8("txtUsername"))
        self.gridLayout.addWidget(self.txtUsername, 0, 1, 1, 3)
        self.label_2 = QtGui.QLabel(DNSSHR)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.txtPassword = QtGui.QLineEdit(DNSSHR)
        self.txtPassword.setEchoMode(QtGui.QLineEdit.Password)
        self.txtPassword.setObjectName(_fromUtf8("txtPassword"))
        self.gridLayout.addWidget(self.txtPassword, 1, 1, 1, 3)
        self.label_3 = QtGui.QLabel(DNSSHR)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)
        self.inYear = QtGui.QSpinBox(DNSSHR)
        self.inYear.setAlignment(QtCore.Qt.AlignCenter)
        self.inYear.setMinimum(2014)
        self.inYear.setMaximum(2050)
        self.inYear.setObjectName(_fromUtf8("inYear"))
        self.gridLayout.addWidget(self.inYear, 2, 1, 1, 1)
        self.label_4 = QtGui.QLabel(DNSSHR)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout.addWidget(self.label_4, 2, 2, 1, 1)
        self.inMonth = QtGui.QComboBox(DNSSHR)
        self.inMonth.setObjectName(_fromUtf8("inMonth"))
        self.inMonth.addItem(_fromUtf8(""))
        self.inMonth.addItem(_fromUtf8(""))
        self.inMonth.addItem(_fromUtf8(""))
        self.inMonth.addItem(_fromUtf8(""))
        self.inMonth.addItem(_fromUtf8(""))
        self.inMonth.addItem(_fromUtf8(""))
        self.inMonth.addItem(_fromUtf8(""))
        self.inMonth.addItem(_fromUtf8(""))
        self.inMonth.addItem(_fromUtf8(""))
        self.inMonth.addItem(_fromUtf8(""))
        self.inMonth.addItem(_fromUtf8(""))
        self.inMonth.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.inMonth, 2, 3, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.btnRefresh = QtGui.QPushButton(DNSSHR)
        self.btnRefresh.setObjectName(_fromUtf8("btnRefresh"))
        self.verticalLayout.addWidget(self.btnRefresh)
        self.graphics = QtGui.QGraphicsView(DNSSHR)
        self.graphics.setObjectName(_fromUtf8("graphics"))
        self.verticalLayout.addWidget(self.graphics)
        self.txtStatus = QtGui.QLineEdit(DNSSHR)
        self.txtStatus.setEnabled(False)
        self.txtStatus.setObjectName(_fromUtf8("txtStatus"))
        self.verticalLayout.addWidget(self.txtStatus)
        self.label.setBuddy(self.txtUsername)
        self.label_2.setBuddy(self.txtPassword)
        self.label_3.setBuddy(self.inYear)
        self.label_4.setBuddy(self.inMonth)

        self.retranslateUi(DNSSHR)
        QtCore.QObject.connect(self.btnRefresh, QtCore.SIGNAL(_fromUtf8("clicked()")), DNSSHR.onBtnRefresh)
        QtCore.QMetaObject.connectSlotsByName(DNSSHR)

    def retranslateUi(self, DNSSHR):
        DNSSHR.setWindowTitle(_translate("DNSSHR", "DNSSHR", None))
        self.label.setText(_translate("DNSSHR", "Username", None))
        self.label_2.setText(_translate("DNSSHR", "Password", None))
        self.label_3.setText(_translate("DNSSHR", "Year", None))
        self.label_4.setText(_translate("DNSSHR", "Month", None))
        self.inMonth.setItemText(0, _translate("DNSSHR", "1", None))
        self.inMonth.setItemText(1, _translate("DNSSHR", "2", None))
        self.inMonth.setItemText(2, _translate("DNSSHR", "3", None))
        self.inMonth.setItemText(3, _translate("DNSSHR", "4", None))
        self.inMonth.setItemText(4, _translate("DNSSHR", "5", None))
        self.inMonth.setItemText(5, _translate("DNSSHR", "6", None))
        self.inMonth.setItemText(6, _translate("DNSSHR", "7", None))
        self.inMonth.setItemText(7, _translate("DNSSHR", "8", None))
        self.inMonth.setItemText(8, _translate("DNSSHR", "9", None))
        self.inMonth.setItemText(9, _translate("DNSSHR", "10", None))
        self.inMonth.setItemText(10, _translate("DNSSHR", "11", None))
        self.inMonth.setItemText(11, _translate("DNSSHR", "12", None))
        self.btnRefresh.setText(_translate("DNSSHR", "Show", None))

