# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'filefilter.ui'
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

class Ui_FileFilterWidget(object):
    def setupUi(self, FileFilterWidget):
        FileFilterWidget.setObjectName(_fromUtf8("FileFilterWidget"))
        FileFilterWidget.resize(428, 522)
        self.gridLayout_3 = QtGui.QGridLayout(FileFilterWidget)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.label = QtGui.QLabel(FileFilterWidget)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout_3.addWidget(self.label, 0, 0, 1, 1)
        self.editSrcDir = DropEdit(FileFilterWidget)
        self.editSrcDir.setObjectName(_fromUtf8("editSrcDir"))
        self.gridLayout_3.addWidget(self.editSrcDir, 0, 1, 1, 1)
        self.btnSrcDir = QtGui.QPushButton(FileFilterWidget)
        self.btnSrcDir.setObjectName(_fromUtf8("btnSrcDir"))
        self.gridLayout_3.addWidget(self.btnSrcDir, 0, 2, 1, 1)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.groupBox = QtGui.QGroupBox(FileFilterWidget)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout = QtGui.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.editEx1 = QtGui.QLineEdit(self.groupBox)
        self.editEx1.setObjectName(_fromUtf8("editEx1"))
        self.gridLayout.addWidget(self.editEx1, 1, 1, 1, 2)
        self.label_3 = QtGui.QLabel(self.groupBox)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 1, 0, 1, 1)
        self.label_2 = QtGui.QLabel(self.groupBox)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)
        self.comboEx1 = QtGui.QComboBox(self.groupBox)
        self.comboEx1.setObjectName(_fromUtf8("comboEx1"))
        self.comboEx1.addItem(_fromUtf8(""))
        self.comboEx1.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.comboEx1, 0, 1, 1, 2)
        self.line = QtGui.QFrame(self.groupBox)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.gridLayout.addWidget(self.line, 2, 0, 1, 3)
        self.label_7 = QtGui.QLabel(self.groupBox)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.gridLayout.addWidget(self.label_7, 7, 0, 1, 1)
        self.label_4 = QtGui.QLabel(self.groupBox)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout.addWidget(self.label_4, 3, 0, 1, 1)
        self.label_6 = QtGui.QLabel(self.groupBox)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.gridLayout.addWidget(self.label_6, 6, 0, 1, 1)
        self.label_5 = QtGui.QLabel(self.groupBox)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridLayout.addWidget(self.label_5, 4, 0, 1, 1)
        self.comboEx2 = QtGui.QComboBox(self.groupBox)
        self.comboEx2.setObjectName(_fromUtf8("comboEx2"))
        self.comboEx2.addItem(_fromUtf8(""))
        self.comboEx2.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.comboEx2, 3, 1, 1, 2)
        self.editEx2 = QtGui.QLineEdit(self.groupBox)
        self.editEx2.setObjectName(_fromUtf8("editEx2"))
        self.gridLayout.addWidget(self.editEx2, 4, 1, 1, 2)
        self.line_3 = QtGui.QFrame(self.groupBox)
        self.line_3.setFrameShape(QtGui.QFrame.HLine)
        self.line_3.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_3.setObjectName(_fromUtf8("line_3"))
        self.gridLayout.addWidget(self.line_3, 5, 0, 1, 3)
        self.comboEx3 = QtGui.QComboBox(self.groupBox)
        self.comboEx3.setObjectName(_fromUtf8("comboEx3"))
        self.comboEx3.addItem(_fromUtf8(""))
        self.comboEx3.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.comboEx3, 6, 1, 1, 2)
        self.editEx3 = QtGui.QLineEdit(self.groupBox)
        self.editEx3.setObjectName(_fromUtf8("editEx3"))
        self.gridLayout.addWidget(self.editEx3, 7, 1, 1, 2)
        self.horizontalLayout_4.addWidget(self.groupBox)
        self.groupBox_2 = QtGui.QGroupBox(FileFilterWidget)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox_2)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.editIn2 = QtGui.QLineEdit(self.groupBox_2)
        self.editIn2.setObjectName(_fromUtf8("editIn2"))
        self.gridLayout_2.addWidget(self.editIn2, 4, 1, 1, 2)
        self.comboIn2 = QtGui.QComboBox(self.groupBox_2)
        self.comboIn2.setObjectName(_fromUtf8("comboIn2"))
        self.comboIn2.addItem(_fromUtf8(""))
        self.comboIn2.addItem(_fromUtf8(""))
        self.gridLayout_2.addWidget(self.comboIn2, 3, 1, 1, 2)
        self.editIn1 = QtGui.QLineEdit(self.groupBox_2)
        self.editIn1.setObjectName(_fromUtf8("editIn1"))
        self.gridLayout_2.addWidget(self.editIn1, 1, 1, 1, 2)
        self.comboIn1 = QtGui.QComboBox(self.groupBox_2)
        self.comboIn1.setObjectName(_fromUtf8("comboIn1"))
        self.comboIn1.addItem(_fromUtf8(""))
        self.comboIn1.addItem(_fromUtf8(""))
        self.gridLayout_2.addWidget(self.comboIn1, 0, 1, 1, 2)
        self.label_16 = QtGui.QLabel(self.groupBox_2)
        self.label_16.setObjectName(_fromUtf8("label_16"))
        self.gridLayout_2.addWidget(self.label_16, 4, 0, 1, 1)
        self.label_15 = QtGui.QLabel(self.groupBox_2)
        self.label_15.setObjectName(_fromUtf8("label_15"))
        self.gridLayout_2.addWidget(self.label_15, 6, 0, 1, 1)
        self.label_14 = QtGui.QLabel(self.groupBox_2)
        self.label_14.setObjectName(_fromUtf8("label_14"))
        self.gridLayout_2.addWidget(self.label_14, 3, 0, 1, 1)
        self.label_13 = QtGui.QLabel(self.groupBox_2)
        self.label_13.setObjectName(_fromUtf8("label_13"))
        self.gridLayout_2.addWidget(self.label_13, 7, 0, 1, 1)
        self.line_4 = QtGui.QFrame(self.groupBox_2)
        self.line_4.setFrameShape(QtGui.QFrame.HLine)
        self.line_4.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_4.setObjectName(_fromUtf8("line_4"))
        self.gridLayout_2.addWidget(self.line_4, 2, 0, 1, 3)
        self.label_11 = QtGui.QLabel(self.groupBox_2)
        self.label_11.setObjectName(_fromUtf8("label_11"))
        self.gridLayout_2.addWidget(self.label_11, 0, 0, 1, 1)
        self.label_10 = QtGui.QLabel(self.groupBox_2)
        self.label_10.setObjectName(_fromUtf8("label_10"))
        self.gridLayout_2.addWidget(self.label_10, 1, 0, 1, 1)
        self.line_5 = QtGui.QFrame(self.groupBox_2)
        self.line_5.setFrameShape(QtGui.QFrame.HLine)
        self.line_5.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_5.setObjectName(_fromUtf8("line_5"))
        self.gridLayout_2.addWidget(self.line_5, 5, 0, 1, 3)
        self.comboIn3 = QtGui.QComboBox(self.groupBox_2)
        self.comboIn3.setObjectName(_fromUtf8("comboIn3"))
        self.comboIn3.addItem(_fromUtf8(""))
        self.comboIn3.addItem(_fromUtf8(""))
        self.gridLayout_2.addWidget(self.comboIn3, 6, 1, 1, 2)
        self.editIn3 = QtGui.QLineEdit(self.groupBox_2)
        self.editIn3.setObjectName(_fromUtf8("editIn3"))
        self.gridLayout_2.addWidget(self.editIn3, 7, 1, 1, 2)
        self.horizontalLayout_4.addWidget(self.groupBox_2)
        self.gridLayout_3.addLayout(self.horizontalLayout_4, 1, 0, 1, 3)
        self.tabWidget = QtGui.QTabWidget(FileFilterWidget)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tab = QtGui.QWidget()
        self.tab.setObjectName(_fromUtf8("tab"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.tab)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.listAll = QtGui.QListWidget(self.tab)
        self.listAll.setObjectName(_fromUtf8("listAll"))
        self.horizontalLayout.addWidget(self.listAll)
        self.tabWidget.addTab(self.tab, _fromUtf8(""))
        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName(_fromUtf8("tab_2"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.tab_2)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.listHit = QtGui.QListWidget(self.tab_2)
        self.listHit.setObjectName(_fromUtf8("listHit"))
        self.horizontalLayout_2.addWidget(self.listHit)
        self.tabWidget.addTab(self.tab_2, _fromUtf8(""))
        self.tab_3 = QtGui.QWidget()
        self.tab_3.setObjectName(_fromUtf8("tab_3"))
        self.horizontalLayout_3 = QtGui.QHBoxLayout(self.tab_3)
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.listUnhit = QtGui.QListWidget(self.tab_3)
        self.listUnhit.setObjectName(_fromUtf8("listUnhit"))
        self.horizontalLayout_3.addWidget(self.listUnhit)
        self.tabWidget.addTab(self.tab_3, _fromUtf8(""))
        self.tab_4 = QtGui.QWidget()
        self.tab_4.setObjectName(_fromUtf8("tab_4"))
        self.horizontalLayout_6 = QtGui.QHBoxLayout(self.tab_4)
        self.horizontalLayout_6.setObjectName(_fromUtf8("horizontalLayout_6"))
        self.listExclude = QtGui.QListWidget(self.tab_4)
        self.listExclude.setObjectName(_fromUtf8("listExclude"))
        self.horizontalLayout_6.addWidget(self.listExclude)
        self.tabWidget.addTab(self.tab_4, _fromUtf8(""))
        self.gridLayout_3.addWidget(self.tabWidget, 3, 0, 1, 3)
        self.horizontalLayout_5 = QtGui.QHBoxLayout()
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        self.btnRefresh = QtGui.QPushButton(FileFilterWidget)
        self.btnRefresh.setObjectName(_fromUtf8("btnRefresh"))
        self.horizontalLayout_5.addWidget(self.btnRefresh)
        self.btnPreview = QtGui.QPushButton(FileFilterWidget)
        self.btnPreview.setObjectName(_fromUtf8("btnPreview"))
        self.horizontalLayout_5.addWidget(self.btnPreview)
        self.gridLayout_3.addLayout(self.horizontalLayout_5, 2, 0, 1, 3)
        self.label.raise_()
        self.btnSrcDir.raise_()
        self.tabWidget.raise_()
        self.editSrcDir.raise_()
        self.label.setBuddy(self.editSrcDir)

        self.retranslateUi(FileFilterWidget)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QObject.connect(self.btnSrcDir, QtCore.SIGNAL(_fromUtf8("clicked()")), FileFilterWidget.onBtnSrcDir)
        QtCore.QObject.connect(self.comboEx1, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(int)")), FileFilterWidget.onComboEx1)
        QtCore.QObject.connect(self.comboEx2, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(int)")), FileFilterWidget.onComboEx2)
        QtCore.QObject.connect(self.comboEx3, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(int)")), FileFilterWidget.onComboEx3)
        QtCore.QObject.connect(self.comboIn1, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(int)")), FileFilterWidget.onComboIn1)
        QtCore.QObject.connect(self.comboIn2, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(int)")), FileFilterWidget.onComboIn2)
        QtCore.QObject.connect(self.comboIn3, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(int)")), FileFilterWidget.onComboIn3)
        QtCore.QObject.connect(self.editEx1, QtCore.SIGNAL(_fromUtf8("textEdited(QString)")), FileFilterWidget.onEditEx1)
        QtCore.QObject.connect(self.editEx2, QtCore.SIGNAL(_fromUtf8("textEdited(QString)")), FileFilterWidget.onEditEx2)
        QtCore.QObject.connect(self.editEx3, QtCore.SIGNAL(_fromUtf8("textEdited(QString)")), FileFilterWidget.onEditEx3)
        QtCore.QObject.connect(self.editIn1, QtCore.SIGNAL(_fromUtf8("textEdited(QString)")), FileFilterWidget.onEditIn1)
        QtCore.QObject.connect(self.editIn2, QtCore.SIGNAL(_fromUtf8("textEdited(QString)")), FileFilterWidget.onEditIn2)
        QtCore.QObject.connect(self.editIn3, QtCore.SIGNAL(_fromUtf8("textEdited(QString)")), FileFilterWidget.onEditIn3)
        QtCore.QObject.connect(self.btnRefresh, QtCore.SIGNAL(_fromUtf8("clicked()")), FileFilterWidget.onBtnRefresh)
        QtCore.QObject.connect(self.btnPreview, QtCore.SIGNAL(_fromUtf8("clicked()")), FileFilterWidget.onBtnPreview)
        QtCore.QMetaObject.connectSlotsByName(FileFilterWidget)
        FileFilterWidget.setTabOrder(self.editSrcDir, self.btnSrcDir)
        FileFilterWidget.setTabOrder(self.btnSrcDir, self.comboEx1)
        FileFilterWidget.setTabOrder(self.comboEx1, self.editEx1)
        FileFilterWidget.setTabOrder(self.editEx1, self.comboEx2)
        FileFilterWidget.setTabOrder(self.comboEx2, self.editEx2)
        FileFilterWidget.setTabOrder(self.editEx2, self.comboEx3)
        FileFilterWidget.setTabOrder(self.comboEx3, self.editEx3)
        FileFilterWidget.setTabOrder(self.editEx3, self.comboIn1)
        FileFilterWidget.setTabOrder(self.comboIn1, self.editIn1)
        FileFilterWidget.setTabOrder(self.editIn1, self.comboIn2)
        FileFilterWidget.setTabOrder(self.comboIn2, self.editIn2)
        FileFilterWidget.setTabOrder(self.editIn2, self.comboIn3)
        FileFilterWidget.setTabOrder(self.comboIn3, self.editIn3)
        FileFilterWidget.setTabOrder(self.editIn3, self.btnRefresh)
        FileFilterWidget.setTabOrder(self.btnRefresh, self.btnPreview)
        FileFilterWidget.setTabOrder(self.btnPreview, self.tabWidget)
        FileFilterWidget.setTabOrder(self.tabWidget, self.listAll)
        FileFilterWidget.setTabOrder(self.listAll, self.listHit)
        FileFilterWidget.setTabOrder(self.listHit, self.listUnhit)
        FileFilterWidget.setTabOrder(self.listUnhit, self.listExclude)

    def retranslateUi(self, FileFilterWidget):
        FileFilterWidget.setWindowTitle(_translate("FileFilterWidget", "FileFilter", None))
        self.label.setText(_translate("FileFilterWidget", "Source Dir", None))
        self.btnSrcDir.setToolTip(_translate("FileFilterWidget", "Choose Source Dir", None))
        self.btnSrcDir.setText(_translate("FileFilterWidget", "...", None))
        self.groupBox.setTitle(_translate("FileFilterWidget", "Exclude Pattens", None))
        self.label_3.setText(_translate("FileFilterWidget", "RegEx", None))
        self.label_2.setText(_translate("FileFilterWidget", "Pattern", None))
        self.comboEx1.setItemText(0, _translate("FileFilterWidget", "Null", None))
        self.comboEx1.setItemText(1, _translate("FileFilterWidget", "Manual", None))
        self.label_7.setText(_translate("FileFilterWidget", "RegEx", None))
        self.label_4.setText(_translate("FileFilterWidget", "Pattern", None))
        self.label_6.setText(_translate("FileFilterWidget", "Pattern", None))
        self.label_5.setText(_translate("FileFilterWidget", "RegEx", None))
        self.comboEx2.setItemText(0, _translate("FileFilterWidget", "Null", None))
        self.comboEx2.setItemText(1, _translate("FileFilterWidget", "Manual", None))
        self.comboEx3.setItemText(0, _translate("FileFilterWidget", "Null", None))
        self.comboEx3.setItemText(1, _translate("FileFilterWidget", "Manual", None))
        self.groupBox_2.setTitle(_translate("FileFilterWidget", "Filter Pattens", None))
        self.comboIn2.setItemText(0, _translate("FileFilterWidget", "Null", None))
        self.comboIn2.setItemText(1, _translate("FileFilterWidget", "Manual", None))
        self.comboIn1.setItemText(0, _translate("FileFilterWidget", "Null", None))
        self.comboIn1.setItemText(1, _translate("FileFilterWidget", "Manual", None))
        self.label_16.setText(_translate("FileFilterWidget", "RegEx", None))
        self.label_15.setText(_translate("FileFilterWidget", "Pattern", None))
        self.label_14.setText(_translate("FileFilterWidget", "Pattern", None))
        self.label_13.setText(_translate("FileFilterWidget", "RegEx", None))
        self.label_11.setText(_translate("FileFilterWidget", "Pattern", None))
        self.label_10.setText(_translate("FileFilterWidget", "RegEx", None))
        self.comboIn3.setItemText(0, _translate("FileFilterWidget", "Null", None))
        self.comboIn3.setItemText(1, _translate("FileFilterWidget", "Manual", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("FileFilterWidget", "All Files", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("FileFilterWidget", "Hit Files", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), _translate("FileFilterWidget", "Unhit Files", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_4), _translate("FileFilterWidget", "Exclude Files", None))
        self.btnRefresh.setToolTip(_translate("FileFilterWidget", "Press this button when source dir changed", None))
        self.btnRefresh.setText(_translate("FileFilterWidget", "Refresh All", None))
        self.btnPreview.setToolTip(_translate("FileFilterWidget", "Press this button to view result of applying regex pattens", None))
        self.btnPreview.setText(_translate("FileFilterWidget", "Preview", None))

from dropedit import DropEdit
