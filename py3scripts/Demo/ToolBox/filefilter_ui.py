# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'filefilter.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_FileFilterWidget(object):
    def setupUi(self, FileFilterWidget):
        FileFilterWidget.setObjectName("FileFilterWidget")
        FileFilterWidget.resize(428, 522)
        self.gridLayout_3 = QtWidgets.QGridLayout(FileFilterWidget)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.label = QtWidgets.QLabel(FileFilterWidget)
        self.label.setObjectName("label")
        self.gridLayout_3.addWidget(self.label, 0, 0, 1, 1)
        self.editSrcDir = DropEdit(FileFilterWidget)
        self.editSrcDir.setObjectName("editSrcDir")
        self.gridLayout_3.addWidget(self.editSrcDir, 0, 1, 1, 1)
        self.btnSrcDir = QtWidgets.QPushButton(FileFilterWidget)
        self.btnSrcDir.setObjectName("btnSrcDir")
        self.gridLayout_3.addWidget(self.btnSrcDir, 0, 2, 1, 1)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.groupBox = QtWidgets.QGroupBox(FileFilterWidget)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName("gridLayout")
        self.editEx1 = QtWidgets.QLineEdit(self.groupBox)
        self.editEx1.setObjectName("editEx1")
        self.gridLayout.addWidget(self.editEx1, 1, 1, 1, 2)
        self.label_3 = QtWidgets.QLabel(self.groupBox)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 1, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.groupBox)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)
        self.comboEx1 = QtWidgets.QComboBox(self.groupBox)
        self.comboEx1.setObjectName("comboEx1")
        self.comboEx1.addItem("")
        self.comboEx1.addItem("")
        self.gridLayout.addWidget(self.comboEx1, 0, 1, 1, 2)
        self.line = QtWidgets.QFrame(self.groupBox)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.gridLayout.addWidget(self.line, 2, 0, 1, 3)
        self.label_7 = QtWidgets.QLabel(self.groupBox)
        self.label_7.setObjectName("label_7")
        self.gridLayout.addWidget(self.label_7, 7, 0, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.groupBox)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 3, 0, 1, 1)
        self.label_6 = QtWidgets.QLabel(self.groupBox)
        self.label_6.setObjectName("label_6")
        self.gridLayout.addWidget(self.label_6, 6, 0, 1, 1)
        self.label_5 = QtWidgets.QLabel(self.groupBox)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 4, 0, 1, 1)
        self.comboEx2 = QtWidgets.QComboBox(self.groupBox)
        self.comboEx2.setObjectName("comboEx2")
        self.comboEx2.addItem("")
        self.comboEx2.addItem("")
        self.gridLayout.addWidget(self.comboEx2, 3, 1, 1, 2)
        self.editEx2 = QtWidgets.QLineEdit(self.groupBox)
        self.editEx2.setObjectName("editEx2")
        self.gridLayout.addWidget(self.editEx2, 4, 1, 1, 2)
        self.line_3 = QtWidgets.QFrame(self.groupBox)
        self.line_3.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_3.setObjectName("line_3")
        self.gridLayout.addWidget(self.line_3, 5, 0, 1, 3)
        self.comboEx3 = QtWidgets.QComboBox(self.groupBox)
        self.comboEx3.setObjectName("comboEx3")
        self.comboEx3.addItem("")
        self.comboEx3.addItem("")
        self.gridLayout.addWidget(self.comboEx3, 6, 1, 1, 2)
        self.editEx3 = QtWidgets.QLineEdit(self.groupBox)
        self.editEx3.setObjectName("editEx3")
        self.gridLayout.addWidget(self.editEx3, 7, 1, 1, 2)
        self.horizontalLayout_4.addWidget(self.groupBox)
        self.groupBox_2 = QtWidgets.QGroupBox(FileFilterWidget)
        self.groupBox_2.setObjectName("groupBox_2")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.groupBox_2)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.editIn2 = QtWidgets.QLineEdit(self.groupBox_2)
        self.editIn2.setObjectName("editIn2")
        self.gridLayout_2.addWidget(self.editIn2, 4, 1, 1, 2)
        self.comboIn2 = QtWidgets.QComboBox(self.groupBox_2)
        self.comboIn2.setObjectName("comboIn2")
        self.comboIn2.addItem("")
        self.comboIn2.addItem("")
        self.gridLayout_2.addWidget(self.comboIn2, 3, 1, 1, 2)
        self.editIn1 = QtWidgets.QLineEdit(self.groupBox_2)
        self.editIn1.setObjectName("editIn1")
        self.gridLayout_2.addWidget(self.editIn1, 1, 1, 1, 2)
        self.comboIn1 = QtWidgets.QComboBox(self.groupBox_2)
        self.comboIn1.setObjectName("comboIn1")
        self.comboIn1.addItem("")
        self.comboIn1.addItem("")
        self.gridLayout_2.addWidget(self.comboIn1, 0, 1, 1, 2)
        self.label_16 = QtWidgets.QLabel(self.groupBox_2)
        self.label_16.setObjectName("label_16")
        self.gridLayout_2.addWidget(self.label_16, 4, 0, 1, 1)
        self.label_15 = QtWidgets.QLabel(self.groupBox_2)
        self.label_15.setObjectName("label_15")
        self.gridLayout_2.addWidget(self.label_15, 6, 0, 1, 1)
        self.label_14 = QtWidgets.QLabel(self.groupBox_2)
        self.label_14.setObjectName("label_14")
        self.gridLayout_2.addWidget(self.label_14, 3, 0, 1, 1)
        self.label_13 = QtWidgets.QLabel(self.groupBox_2)
        self.label_13.setObjectName("label_13")
        self.gridLayout_2.addWidget(self.label_13, 7, 0, 1, 1)
        self.line_4 = QtWidgets.QFrame(self.groupBox_2)
        self.line_4.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_4.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_4.setObjectName("line_4")
        self.gridLayout_2.addWidget(self.line_4, 2, 0, 1, 3)
        self.label_11 = QtWidgets.QLabel(self.groupBox_2)
        self.label_11.setObjectName("label_11")
        self.gridLayout_2.addWidget(self.label_11, 0, 0, 1, 1)
        self.label_10 = QtWidgets.QLabel(self.groupBox_2)
        self.label_10.setObjectName("label_10")
        self.gridLayout_2.addWidget(self.label_10, 1, 0, 1, 1)
        self.line_5 = QtWidgets.QFrame(self.groupBox_2)
        self.line_5.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_5.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_5.setObjectName("line_5")
        self.gridLayout_2.addWidget(self.line_5, 5, 0, 1, 3)
        self.comboIn3 = QtWidgets.QComboBox(self.groupBox_2)
        self.comboIn3.setObjectName("comboIn3")
        self.comboIn3.addItem("")
        self.comboIn3.addItem("")
        self.gridLayout_2.addWidget(self.comboIn3, 6, 1, 1, 2)
        self.editIn3 = QtWidgets.QLineEdit(self.groupBox_2)
        self.editIn3.setObjectName("editIn3")
        self.gridLayout_2.addWidget(self.editIn3, 7, 1, 1, 2)
        self.horizontalLayout_4.addWidget(self.groupBox_2)
        self.gridLayout_3.addLayout(self.horizontalLayout_4, 1, 0, 1, 3)
        self.tabWidget = QtWidgets.QTabWidget(FileFilterWidget)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.tab)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.listAll = QtWidgets.QListWidget(self.tab)
        self.listAll.setObjectName("listAll")
        self.horizontalLayout.addWidget(self.listAll)
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.tab_2)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.listHit = QtWidgets.QListWidget(self.tab_2)
        self.listHit.setObjectName("listHit")
        self.horizontalLayout_2.addWidget(self.listHit)
        self.tabWidget.addTab(self.tab_2, "")
        self.tab_3 = QtWidgets.QWidget()
        self.tab_3.setObjectName("tab_3")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.tab_3)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.listUnhit = QtWidgets.QListWidget(self.tab_3)
        self.listUnhit.setObjectName("listUnhit")
        self.horizontalLayout_3.addWidget(self.listUnhit)
        self.tabWidget.addTab(self.tab_3, "")
        self.tab_4 = QtWidgets.QWidget()
        self.tab_4.setObjectName("tab_4")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout(self.tab_4)
        self.horizontalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.listExclude = QtWidgets.QListWidget(self.tab_4)
        self.listExclude.setObjectName("listExclude")
        self.horizontalLayout_6.addWidget(self.listExclude)
        self.tabWidget.addTab(self.tab_4, "")
        self.gridLayout_3.addWidget(self.tabWidget, 3, 0, 1, 3)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.btnRefresh = QtWidgets.QPushButton(FileFilterWidget)
        self.btnRefresh.setObjectName("btnRefresh")
        self.horizontalLayout_5.addWidget(self.btnRefresh)
        self.btnPreview = QtWidgets.QPushButton(FileFilterWidget)
        self.btnPreview.setObjectName("btnPreview")
        self.horizontalLayout_5.addWidget(self.btnPreview)
        self.gridLayout_3.addLayout(self.horizontalLayout_5, 2, 0, 1, 3)
        self.label.raise_()
        self.btnSrcDir.raise_()
        self.tabWidget.raise_()
        self.editSrcDir.raise_()
        self.label.setBuddy(self.editSrcDir)

        self.retranslateUi(FileFilterWidget)
        self.tabWidget.setCurrentIndex(0)
        self.btnSrcDir.clicked.connect(FileFilterWidget.onBtnSrcDir)
        self.comboEx1.currentIndexChanged['int'].connect(FileFilterWidget.onComboEx1)
        self.comboEx2.currentIndexChanged['int'].connect(FileFilterWidget.onComboEx2)
        self.comboEx3.currentIndexChanged['int'].connect(FileFilterWidget.onComboEx3)
        self.comboIn1.currentIndexChanged['int'].connect(FileFilterWidget.onComboIn1)
        self.comboIn2.currentIndexChanged['int'].connect(FileFilterWidget.onComboIn2)
        self.comboIn3.currentIndexChanged['int'].connect(FileFilterWidget.onComboIn3)
        self.editEx1.textEdited['QString'].connect(FileFilterWidget.onEditEx1)
        self.editEx2.textEdited['QString'].connect(FileFilterWidget.onEditEx2)
        self.editEx3.textEdited['QString'].connect(FileFilterWidget.onEditEx3)
        self.editIn1.textEdited['QString'].connect(FileFilterWidget.onEditIn1)
        self.editIn2.textEdited['QString'].connect(FileFilterWidget.onEditIn2)
        self.editIn3.textEdited['QString'].connect(FileFilterWidget.onEditIn3)
        self.btnRefresh.clicked.connect(FileFilterWidget.onBtnRefresh)
        self.btnPreview.clicked.connect(FileFilterWidget.onBtnPreview)
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
        _translate = QtCore.QCoreApplication.translate
        FileFilterWidget.setWindowTitle(_translate("FileFilterWidget", "FileFilter"))
        self.label.setText(_translate("FileFilterWidget", "Source Dir"))
        self.btnSrcDir.setToolTip(_translate("FileFilterWidget", "Choose Source Dir"))
        self.btnSrcDir.setText(_translate("FileFilterWidget", "..."))
        self.groupBox.setTitle(_translate("FileFilterWidget", "Exclude Pattens"))
        self.label_3.setText(_translate("FileFilterWidget", "RegEx"))
        self.label_2.setText(_translate("FileFilterWidget", "Pattern"))
        self.comboEx1.setItemText(0, _translate("FileFilterWidget", "Null"))
        self.comboEx1.setItemText(1, _translate("FileFilterWidget", "Manual"))
        self.label_7.setText(_translate("FileFilterWidget", "RegEx"))
        self.label_4.setText(_translate("FileFilterWidget", "Pattern"))
        self.label_6.setText(_translate("FileFilterWidget", "Pattern"))
        self.label_5.setText(_translate("FileFilterWidget", "RegEx"))
        self.comboEx2.setItemText(0, _translate("FileFilterWidget", "Null"))
        self.comboEx2.setItemText(1, _translate("FileFilterWidget", "Manual"))
        self.comboEx3.setItemText(0, _translate("FileFilterWidget", "Null"))
        self.comboEx3.setItemText(1, _translate("FileFilterWidget", "Manual"))
        self.groupBox_2.setTitle(_translate("FileFilterWidget", "Filter Pattens"))
        self.comboIn2.setItemText(0, _translate("FileFilterWidget", "Null"))
        self.comboIn2.setItemText(1, _translate("FileFilterWidget", "Manual"))
        self.comboIn1.setItemText(0, _translate("FileFilterWidget", "Null"))
        self.comboIn1.setItemText(1, _translate("FileFilterWidget", "Manual"))
        self.label_16.setText(_translate("FileFilterWidget", "RegEx"))
        self.label_15.setText(_translate("FileFilterWidget", "Pattern"))
        self.label_14.setText(_translate("FileFilterWidget", "Pattern"))
        self.label_13.setText(_translate("FileFilterWidget", "RegEx"))
        self.label_11.setText(_translate("FileFilterWidget", "Pattern"))
        self.label_10.setText(_translate("FileFilterWidget", "RegEx"))
        self.comboIn3.setItemText(0, _translate("FileFilterWidget", "Null"))
        self.comboIn3.setItemText(1, _translate("FileFilterWidget", "Manual"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("FileFilterWidget", "All Files"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("FileFilterWidget", "Hit Files"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), _translate("FileFilterWidget", "Unhit Files"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_4), _translate("FileFilterWidget", "Exclude Files"))
        self.btnRefresh.setToolTip(_translate("FileFilterWidget", "Press this button when source dir changed"))
        self.btnRefresh.setText(_translate("FileFilterWidget", "Refresh All"))
        self.btnPreview.setToolTip(_translate("FileFilterWidget", "Press this button to view result of applying regex pattens"))
        self.btnPreview.setText(_translate("FileFilterWidget", "Preview"))

from dropedit import DropEdit
