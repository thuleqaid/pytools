# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'fc.ui'
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

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(480, 400)
        self.verticalLayout = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.btnPathTemppath = QtGui.QPushButton(Dialog)
        self.btnPathTemppath.setObjectName(_fromUtf8("btnPathTemppath"))
        self.gridLayout.addWidget(self.btnPathTemppath, 3, 2, 1, 1)
        self.label_6 = QtGui.QLabel(Dialog)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.gridLayout.addWidget(self.label_6, 5, 0, 1, 1)
        self.btnOutpath = QtGui.QPushButton(Dialog)
        self.btnOutpath.setObjectName(_fromUtf8("btnOutpath"))
        self.gridLayout.addWidget(self.btnOutpath, 2, 2, 1, 1)
        self.editOutpath = DropEdit(Dialog)
        self.editOutpath.setObjectName(_fromUtf8("editOutpath"))
        self.gridLayout.addWidget(self.editOutpath, 2, 1, 1, 1)
        self.editPath1 = DropEdit(Dialog)
        self.editPath1.setObjectName(_fromUtf8("editPath1"))
        self.gridLayout.addWidget(self.editPath1, 0, 1, 1, 1)
        self.btnPath1 = QtGui.QPushButton(Dialog)
        self.btnPath1.setObjectName(_fromUtf8("btnPath1"))
        self.gridLayout.addWidget(self.btnPath1, 0, 2, 1, 1)
        self.editPath2 = DropEdit(Dialog)
        self.editPath2.setObjectName(_fromUtf8("editPath2"))
        self.gridLayout.addWidget(self.editPath2, 1, 1, 1, 1)
        self.label_3 = QtGui.QLabel(Dialog)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)
        self.btnPath2 = QtGui.QPushButton(Dialog)
        self.btnPath2.setObjectName(_fromUtf8("btnPath2"))
        self.gridLayout.addWidget(self.btnPath2, 1, 2, 1, 1)
        self.label_2 = QtGui.QLabel(Dialog)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.editTemppath = DropEdit(Dialog)
        self.editTemppath.setObjectName(_fromUtf8("editTemppath"))
        self.gridLayout.addWidget(self.editTemppath, 3, 1, 1, 1)
        self.label_4 = QtGui.QLabel(Dialog)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout.addWidget(self.label_4, 3, 0, 1, 1)
        self.label = QtGui.QLabel(Dialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.btnBCompare = QtGui.QPushButton(Dialog)
        self.btnBCompare.setObjectName(_fromUtf8("btnBCompare"))
        self.gridLayout.addWidget(self.btnBCompare, 4, 2, 1, 1)
        self.editBCompare = DropEdit(Dialog)
        self.editBCompare.setObjectName(_fromUtf8("editBCompare"))
        self.gridLayout.addWidget(self.editBCompare, 4, 1, 1, 1)
        self.label_5 = QtGui.QLabel(Dialog)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridLayout.addWidget(self.label_5, 4, 0, 1, 1)
        self.editFilter = QtGui.QLineEdit(Dialog)
        self.editFilter.setText(_fromUtf8("*.c;*.h"))
        self.editFilter.setObjectName(_fromUtf8("editFilter"))
        self.gridLayout.addWidget(self.editFilter, 5, 1, 1, 2)
        self.label_7 = QtGui.QLabel(Dialog)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.gridLayout.addWidget(self.label_7, 6, 0, 1, 1)
        self.editSummary = QtGui.QLineEdit(Dialog)
        self.editSummary.setText(_fromUtf8("Report.html"))
        self.editSummary.setObjectName(_fromUtf8("editSummary"))
        self.gridLayout.addWidget(self.editSummary, 6, 1, 1, 2)
        self.verticalLayout.addLayout(self.gridLayout)
        self.gridLayout_2 = QtGui.QGridLayout()
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.btnStep5 = QtGui.QPushButton(Dialog)
        self.btnStep5.setObjectName(_fromUtf8("btnStep5"))
        self.gridLayout_2.addWidget(self.btnStep5, 4, 0, 1, 1)
        self.spinBox = QtGui.QSpinBox(Dialog)
        self.spinBox.setMinimum(1)
        self.spinBox.setProperty("value", 5)
        self.spinBox.setObjectName(_fromUtf8("spinBox"))
        self.gridLayout_2.addWidget(self.spinBox, 3, 1, 1, 1)
        self.btnStep2 = QtGui.QPushButton(Dialog)
        self.btnStep2.setObjectName(_fromUtf8("btnStep2"))
        self.gridLayout_2.addWidget(self.btnStep2, 1, 0, 1, 1)
        self.btnStep1 = QtGui.QPushButton(Dialog)
        self.btnStep1.setObjectName(_fromUtf8("btnStep1"))
        self.gridLayout_2.addWidget(self.btnStep1, 0, 0, 1, 1)
        self.btnStep3 = QtGui.QPushButton(Dialog)
        self.btnStep3.setObjectName(_fromUtf8("btnStep3"))
        self.gridLayout_2.addWidget(self.btnStep3, 2, 0, 1, 1)
        self.btnStep4 = QtGui.QPushButton(Dialog)
        self.btnStep4.setObjectName(_fromUtf8("btnStep4"))
        self.gridLayout_2.addWidget(self.btnStep4, 3, 0, 1, 1)
        self.btnAll = QtGui.QPushButton(Dialog)
        self.btnAll.setObjectName(_fromUtf8("btnAll"))
        self.gridLayout_2.addWidget(self.btnAll, 5, 0, 1, 2)
        self.verticalLayout.addLayout(self.gridLayout_2)
        self.label_6.setBuddy(self.editFilter)
        self.label_3.setBuddy(self.editOutpath)
        self.label_2.setBuddy(self.editPath2)
        self.label_4.setBuddy(self.editTemppath)
        self.label.setBuddy(self.editPath1)
        self.label_5.setBuddy(self.editBCompare)
        self.label_7.setBuddy(self.editSummary)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.btnPath1, QtCore.SIGNAL(_fromUtf8("clicked()")), Dialog.onBtnPath1)
        QtCore.QObject.connect(self.btnPath2, QtCore.SIGNAL(_fromUtf8("clicked()")), Dialog.onBtnPath2)
        QtCore.QObject.connect(self.btnOutpath, QtCore.SIGNAL(_fromUtf8("clicked()")), Dialog.onBtnOutpath)
        QtCore.QObject.connect(self.btnPathTemppath, QtCore.SIGNAL(_fromUtf8("clicked()")), Dialog.onBtnTemppath)
        QtCore.QObject.connect(self.btnBCompare, QtCore.SIGNAL(_fromUtf8("clicked()")), Dialog.onBtnBCompare)
        QtCore.QObject.connect(self.btnStep1, QtCore.SIGNAL(_fromUtf8("clicked()")), Dialog.onBtnStep1)
        QtCore.QObject.connect(self.btnStep2, QtCore.SIGNAL(_fromUtf8("clicked()")), Dialog.onBtnStep2)
        QtCore.QObject.connect(self.btnStep3, QtCore.SIGNAL(_fromUtf8("clicked()")), Dialog.onBtnStep3)
        QtCore.QObject.connect(self.btnStep4, QtCore.SIGNAL(_fromUtf8("clicked()")), Dialog.onBtnStep4)
        QtCore.QObject.connect(self.btnStep5, QtCore.SIGNAL(_fromUtf8("clicked()")), Dialog.onBtnStep5)
        QtCore.QObject.connect(self.btnAll, QtCore.SIGNAL(_fromUtf8("clicked()")), Dialog.onBtnStepAll)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        Dialog.setTabOrder(self.editPath1, self.btnPath1)
        Dialog.setTabOrder(self.btnPath1, self.editPath2)
        Dialog.setTabOrder(self.editPath2, self.btnPath2)
        Dialog.setTabOrder(self.btnPath2, self.editOutpath)
        Dialog.setTabOrder(self.editOutpath, self.btnOutpath)
        Dialog.setTabOrder(self.btnOutpath, self.editTemppath)
        Dialog.setTabOrder(self.editTemppath, self.btnPathTemppath)
        Dialog.setTabOrder(self.btnPathTemppath, self.editBCompare)
        Dialog.setTabOrder(self.editBCompare, self.btnBCompare)
        Dialog.setTabOrder(self.btnBCompare, self.editFilter)
        Dialog.setTabOrder(self.editFilter, self.editSummary)
        Dialog.setTabOrder(self.editSummary, self.btnStep1)
        Dialog.setTabOrder(self.btnStep1, self.btnStep2)
        Dialog.setTabOrder(self.btnStep2, self.btnStep3)
        Dialog.setTabOrder(self.btnStep3, self.btnStep4)
        Dialog.setTabOrder(self.btnStep4, self.spinBox)
        Dialog.setTabOrder(self.spinBox, self.btnStep5)
        Dialog.setTabOrder(self.btnStep5, self.btnAll)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "FolderComparer", None))
        self.btnPathTemppath.setText(_translate("Dialog", "...", None))
        self.label_6.setText(_translate("Dialog", "Filter", None))
        self.btnOutpath.setText(_translate("Dialog", "...", None))
        self.btnPath1.setText(_translate("Dialog", "...", None))
        self.label_3.setText(_translate("Dialog", "Output Path", None))
        self.btnPath2.setText(_translate("Dialog", "...", None))
        self.label_2.setText(_translate("Dialog", "Modified Source Path", None))
        self.label_4.setText(_translate("Dialog", "Temp Path", None))
        self.label.setText(_translate("Dialog", "Base Source Path", None))
        self.btnBCompare.setText(_translate("Dialog", "...", None))
        self.label_5.setText(_translate("Dialog", "BCompare.exe Path", None))
        self.label_7.setText(_translate("Dialog", "Summary Filename", None))
        self.btnStep5.setText(_translate("Dialog", "Clear temp path", None))
        self.btnStep2.setText(_translate("Dialog", "Diff folder", None))
        self.btnStep1.setText(_translate("Dialog", "Generate Summary", None))
        self.btnStep3.setText(_translate("Dialog", "Patch Summary", None))
        self.btnStep4.setText(_translate("Dialog", "Patch diff", None))
        self.btnAll.setText(_translate("Dialog", "All", None))

from dropedit import DropEdit