# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'toolbox.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ToolBoxDialog(object):
    def setupUi(self, ToolBoxDialog):
        ToolBoxDialog.setObjectName("ToolBoxDialog")
        ToolBoxDialog.resize(800, 600)
        self.horizontalLayout = QtWidgets.QHBoxLayout(ToolBoxDialog)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.tabWidget = QtWidgets.QTabWidget(ToolBoxDialog)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.tabWidget.addTab(self.tab_2, "")
        self.tab_3 = QtWidgets.QWidget()
        self.tab_3.setObjectName("tab_3")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.tab_3)
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.filefilter = FileFilterQt(self.tab_3)
        self.filefilter.setMinimumSize(QtCore.QSize(428, 522))
        self.filefilter.setObjectName("filefilter")
        self.horizontalLayout_4.addWidget(self.filefilter)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label = QtWidgets.QLabel(self.tab_3)
        self.label.setObjectName("label")
        self.horizontalLayout_2.addWidget(self.label)
        self.editDstDir = DropEdit(self.tab_3)
        self.editDstDir.setObjectName("editDstDir")
        self.horizontalLayout_2.addWidget(self.editDstDir)
        self.btnDstDir = QtWidgets.QPushButton(self.tab_3)
        self.btnDstDir.setObjectName("btnDstDir")
        self.horizontalLayout_2.addWidget(self.btnDstDir)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.groupBox = QtWidgets.QGroupBox(self.tab_3)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName("gridLayout")
        self.label_2 = QtWidgets.QLabel(self.groupBox)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)
        self.comboFail = QtWidgets.QComboBox(self.groupBox)
        self.comboFail.setObjectName("comboFail")
        self.comboFail.addItem("")
        self.comboFail.addItem("")
        self.gridLayout.addWidget(self.comboFail, 0, 1, 1, 1)
        self.comboUnhit = QtWidgets.QComboBox(self.groupBox)
        self.comboUnhit.setObjectName("comboUnhit")
        self.comboUnhit.addItem("")
        self.comboUnhit.addItem("")
        self.gridLayout.addWidget(self.comboUnhit, 1, 1, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.groupBox)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 1, 0, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.groupBox)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 2, 0, 1, 1)
        self.comboExclude = QtWidgets.QComboBox(self.groupBox)
        self.comboExclude.setObjectName("comboExclude")
        self.comboExclude.addItem("")
        self.comboExclude.addItem("")
        self.gridLayout.addWidget(self.comboExclude, 2, 1, 1, 1)
        self.verticalLayout.addWidget(self.groupBox)
        self.tabWidget_2 = QtWidgets.QTabWidget(self.tab_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tabWidget_2.sizePolicy().hasHeightForWidth())
        self.tabWidget_2.setSizePolicy(sizePolicy)
        self.tabWidget_2.setObjectName("tabWidget_2")
        self.tab_5 = QtWidgets.QWidget()
        self.tab_5.setObjectName("tab_5")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.tab_5)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.btnAction_DirEncode = QtWidgets.QPushButton(self.tab_5)
        self.btnAction_DirEncode.setObjectName("btnAction_DirEncode")
        self.gridLayout_2.addWidget(self.btnAction_DirEncode, 4, 0, 1, 2)
        self.comboEncode_DirEncode = QtWidgets.QComboBox(self.tab_5)
        self.comboEncode_DirEncode.setObjectName("comboEncode_DirEncode")
        self.gridLayout_2.addWidget(self.comboEncode_DirEncode, 0, 1, 2, 1)
        self.comboNewline_DirEncode = QtWidgets.QComboBox(self.tab_5)
        self.comboNewline_DirEncode.setObjectName("comboNewline_DirEncode")
        self.gridLayout_2.addWidget(self.comboNewline_DirEncode, 2, 1, 1, 1)
        self.label_6 = QtWidgets.QLabel(self.tab_5)
        self.label_6.setObjectName("label_6")
        self.gridLayout_2.addWidget(self.label_6, 2, 0, 1, 1)
        self.label_5 = QtWidgets.QLabel(self.tab_5)
        self.label_5.setObjectName("label_5")
        self.gridLayout_2.addWidget(self.label_5, 0, 0, 2, 1)
        self.tabWidget_2.addTab(self.tab_5, "")
        self.tab_6 = QtWidgets.QWidget()
        self.tab_6.setObjectName("tab_6")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.tab_6)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.btnAction_DirKatakana = QtWidgets.QPushButton(self.tab_6)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnAction_DirKatakana.sizePolicy().hasHeightForWidth())
        self.btnAction_DirKatakana.setSizePolicy(sizePolicy)
        self.btnAction_DirKatakana.setObjectName("btnAction_DirKatakana")
        self.horizontalLayout_3.addWidget(self.btnAction_DirKatakana)
        self.tabWidget_2.addTab(self.tab_6, "")
        self.verticalLayout.addWidget(self.tabWidget_2)
        self.listWidget = QtWidgets.QListWidget(self.tab_3)
        self.listWidget.setObjectName("listWidget")
        self.verticalLayout.addWidget(self.listWidget)
        self.horizontalLayout_4.addLayout(self.verticalLayout)
        self.tabWidget.addTab(self.tab_3, "")
        self.tab_4 = QtWidgets.QWidget()
        self.tab_4.setObjectName("tab_4")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.tab_4)
        self.gridLayout_4.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.btnGenerateTag = QtWidgets.QPushButton(self.tab_4)
        self.btnGenerateTag.setObjectName("btnGenerateTag")
        self.horizontalLayout_5.addWidget(self.btnGenerateTag)
        self.btnExtractFunc = QtWidgets.QPushButton(self.tab_4)
        self.btnExtractFunc.setObjectName("btnExtractFunc")
        self.horizontalLayout_5.addWidget(self.btnExtractFunc)
        self.btnExtractFuncDiff = QtWidgets.QPushButton(self.tab_4)
        self.btnExtractFuncDiff.setObjectName("btnExtractFuncDiff")
        self.horizontalLayout_5.addWidget(self.btnExtractFuncDiff)
        self.gridLayout_4.addLayout(self.horizontalLayout_5, 5, 0, 1, 3)
        self.btnBaseSource = QtWidgets.QPushButton(self.tab_4)
        self.btnBaseSource.setObjectName("btnBaseSource")
        self.gridLayout_4.addWidget(self.btnBaseSource, 1, 2, 1, 1)
        self.editBaseSource = DropEdit(self.tab_4)
        self.editBaseSource.setObjectName("editBaseSource")
        self.gridLayout_4.addWidget(self.editBaseSource, 1, 1, 1, 1)
        self.label_8 = QtWidgets.QLabel(self.tab_4)
        self.label_8.setObjectName("label_8")
        self.gridLayout_4.addWidget(self.label_8, 1, 0, 1, 1)
        self.btnNewSource = QtWidgets.QPushButton(self.tab_4)
        self.btnNewSource.setObjectName("btnNewSource")
        self.gridLayout_4.addWidget(self.btnNewSource, 0, 2, 1, 1)
        self.editNewSource = DropEdit(self.tab_4)
        self.editNewSource.setObjectName("editNewSource")
        self.gridLayout_4.addWidget(self.editNewSource, 0, 1, 1, 1)
        self.label_7 = QtWidgets.QLabel(self.tab_4)
        self.label_7.setObjectName("label_7")
        self.gridLayout_4.addWidget(self.label_7, 0, 0, 1, 1)
        self.listWidget_Source = QtWidgets.QListWidget(self.tab_4)
        self.listWidget_Source.setObjectName("listWidget_Source")
        self.gridLayout_4.addWidget(self.listWidget_Source, 4, 0, 1, 3)
        self.groupBox_2 = QtWidgets.QGroupBox(self.tab_4)
        self.groupBox_2.setObjectName("groupBox_2")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.groupBox_2)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.checkSubFuncName = QtWidgets.QCheckBox(self.groupBox_2)
        self.checkSubFuncName.setChecked(True)
        self.checkSubFuncName.setObjectName("checkSubFuncName")
        self.gridLayout_3.addWidget(self.checkSubFuncName, 1, 1, 1, 1)
        self.line = QtWidgets.QFrame(self.groupBox_2)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.gridLayout_3.addWidget(self.line, 3, 0, 1, 4)
        self.checkLoop = QtWidgets.QCheckBox(self.groupBox_2)
        self.checkLoop.setObjectName("checkLoop")
        self.gridLayout_3.addWidget(self.checkLoop, 1, 3, 1, 1)
        self.checkCondition = QtWidgets.QCheckBox(self.groupBox_2)
        self.checkCondition.setObjectName("checkCondition")
        self.gridLayout_3.addWidget(self.checkCondition, 1, 2, 1, 1)
        self.checkSubFuncCount = QtWidgets.QCheckBox(self.groupBox_2)
        self.checkSubFuncCount.setChecked(False)
        self.checkSubFuncCount.setObjectName("checkSubFuncCount")
        self.gridLayout_3.addWidget(self.checkSubFuncCount, 1, 0, 1, 1)
        self.checkStopline = QtWidgets.QCheckBox(self.groupBox_2)
        self.checkStopline.setObjectName("checkStopline")
        self.gridLayout_3.addWidget(self.checkStopline, 0, 3, 1, 1)
        self.checkFilePath = QtWidgets.QCheckBox(self.groupBox_2)
        self.checkFilePath.setChecked(True)
        self.checkFilePath.setObjectName("checkFilePath")
        self.gridLayout_3.addWidget(self.checkFilePath, 0, 0, 1, 1)
        self.checkStartline = QtWidgets.QCheckBox(self.groupBox_2)
        self.checkStartline.setObjectName("checkStartline")
        self.gridLayout_3.addWidget(self.checkStartline, 0, 2, 1, 1)
        self.checkLines = QtWidgets.QCheckBox(self.groupBox_2)
        self.checkLines.setChecked(False)
        self.checkLines.setObjectName("checkLines")
        self.gridLayout_3.addWidget(self.checkLines, 5, 0, 1, 1)
        self.checkScope = QtWidgets.QCheckBox(self.groupBox_2)
        self.checkScope.setObjectName("checkScope")
        self.gridLayout_3.addWidget(self.checkScope, 0, 1, 1, 1)
        self.checkPrototype = QtWidgets.QCheckBox(self.groupBox_2)
        self.checkPrototype.setChecked(True)
        self.checkPrototype.setObjectName("checkPrototype")
        self.gridLayout_3.addWidget(self.checkPrototype, 2, 0, 1, 1)
        self.checkFuncID = QtWidgets.QCheckBox(self.groupBox_2)
        self.checkFuncID.setChecked(True)
        self.checkFuncID.setObjectName("checkFuncID")
        self.gridLayout_3.addWidget(self.checkFuncID, 6, 0, 1, 1)
        self.checkFuncName = QtWidgets.QCheckBox(self.groupBox_2)
        self.checkFuncName.setChecked(True)
        self.checkFuncName.setObjectName("checkFuncName")
        self.gridLayout_3.addWidget(self.checkFuncName, 6, 1, 1, 1)
        self.checkInline = QtWidgets.QCheckBox(self.groupBox_2)
        self.checkInline.setChecked(True)
        self.checkInline.setObjectName("checkInline")
        self.gridLayout_3.addWidget(self.checkInline, 5, 2, 1, 1)
        self.checkHeaderline = QtWidgets.QCheckBox(self.groupBox_2)
        self.checkHeaderline.setObjectName("checkHeaderline")
        self.gridLayout_3.addWidget(self.checkHeaderline, 5, 1, 1, 1)
        self.gridLayout_4.addWidget(self.groupBox_2, 2, 0, 1, 3)
        self.tabWidget.addTab(self.tab_4, "")
        self.tab_7 = QtWidgets.QWidget()
        self.tab_7.setObjectName("tab_7")
        self.gridLayout_5 = QtWidgets.QGridLayout(self.tab_7)
        self.gridLayout_5.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.btnInlineSource = QtWidgets.QPushButton(self.tab_7)
        self.btnInlineSource.setObjectName("btnInlineSource")
        self.gridLayout_5.addWidget(self.btnInlineSource, 0, 4, 1, 1)
        self.label_10 = QtWidgets.QLabel(self.tab_7)
        self.label_10.setObjectName("label_10")
        self.gridLayout_5.addWidget(self.label_10, 1, 0, 1, 1)
        self.label_15 = QtWidgets.QLabel(self.tab_7)
        self.label_15.setObjectName("label_15")
        self.gridLayout_5.addWidget(self.label_15, 5, 0, 1, 3)
        self.editInlineInline = DropEdit(self.tab_7)
        self.editInlineInline.setObjectName("editInlineInline")
        self.gridLayout_5.addWidget(self.editInlineInline, 2, 3, 1, 1)
        self.editInlineSource = DropEdit(self.tab_7)
        self.editInlineSource.setObjectName("editInlineSource")
        self.gridLayout_5.addWidget(self.editInlineSource, 0, 3, 1, 1)
        self.btnInlineFunction = QtWidgets.QPushButton(self.tab_7)
        self.btnInlineFunction.setObjectName("btnInlineFunction")
        self.gridLayout_5.addWidget(self.btnInlineFunction, 1, 4, 1, 1)
        self.editInlineFunction = DropEdit(self.tab_7)
        self.editInlineFunction.setObjectName("editInlineFunction")
        self.gridLayout_5.addWidget(self.editInlineFunction, 1, 3, 1, 1)
        self.label_12 = QtWidgets.QLabel(self.tab_7)
        self.label_12.setObjectName("label_12")
        self.gridLayout_5.addWidget(self.label_12, 3, 0, 1, 2)
        self.label_11 = QtWidgets.QLabel(self.tab_7)
        self.label_11.setObjectName("label_11")
        self.gridLayout_5.addWidget(self.label_11, 2, 0, 1, 1)
        self.btnInlineMetric = QtWidgets.QPushButton(self.tab_7)
        self.btnInlineMetric.setObjectName("btnInlineMetric")
        self.gridLayout_5.addWidget(self.btnInlineMetric, 3, 4, 1, 1)
        self.editMinMetric = QtWidgets.QLineEdit(self.tab_7)
        self.editMinMetric.setObjectName("editMinMetric")
        self.gridLayout_5.addWidget(self.editMinMetric, 5, 3, 1, 1)
        self.btnInlineInline = QtWidgets.QPushButton(self.tab_7)
        self.btnInlineInline.setObjectName("btnInlineInline")
        self.gridLayout_5.addWidget(self.btnInlineInline, 2, 4, 1, 1)
        self.label_9 = QtWidgets.QLabel(self.tab_7)
        self.label_9.setObjectName("label_9")
        self.gridLayout_5.addWidget(self.label_9, 0, 0, 1, 1)
        self.editInlineMetric = DropEdit(self.tab_7)
        self.editInlineMetric.setObjectName("editInlineMetric")
        self.gridLayout_5.addWidget(self.editInlineMetric, 3, 3, 1, 1)
        self.btnInlineGenerateAdjust = QtWidgets.QPushButton(self.tab_7)
        self.btnInlineGenerateAdjust.setEnabled(True)
        self.btnInlineGenerateAdjust.setObjectName("btnInlineGenerateAdjust")
        self.gridLayout_5.addWidget(self.btnInlineGenerateAdjust, 8, 5, 1, 1)
        self.btnInlineAdjust = QtWidgets.QPushButton(self.tab_7)
        self.btnInlineAdjust.setObjectName("btnInlineAdjust")
        self.gridLayout_5.addWidget(self.btnInlineAdjust, 8, 4, 1, 1)
        self.editInlineAdjust = DropEdit(self.tab_7)
        self.editInlineAdjust.setObjectName("editInlineAdjust")
        self.gridLayout_5.addWidget(self.editInlineAdjust, 8, 3, 1, 1)
        self.label_13 = QtWidgets.QLabel(self.tab_7)
        self.label_13.setObjectName("label_13")
        self.gridLayout_5.addWidget(self.label_13, 7, 0, 1, 1)
        self.label_14 = QtWidgets.QLabel(self.tab_7)
        self.label_14.setObjectName("label_14")
        self.gridLayout_5.addWidget(self.label_14, 8, 0, 1, 3)
        self.btnInlineGenerateTree = QtWidgets.QPushButton(self.tab_7)
        self.btnInlineGenerateTree.setEnabled(True)
        self.btnInlineGenerateTree.setObjectName("btnInlineGenerateTree")
        self.gridLayout_5.addWidget(self.btnInlineGenerateTree, 7, 5, 1, 1)
        self.btnInlineTree = QtWidgets.QPushButton(self.tab_7)
        self.btnInlineTree.setObjectName("btnInlineTree")
        self.gridLayout_5.addWidget(self.btnInlineTree, 7, 4, 1, 1)
        self.editInlineTree = DropEdit(self.tab_7)
        self.editInlineTree.setObjectName("editInlineTree")
        self.gridLayout_5.addWidget(self.editInlineTree, 7, 3, 1, 1)
        self.line_2 = QtWidgets.QFrame(self.tab_7)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.gridLayout_5.addWidget(self.line_2, 6, 0, 1, 6)
        self.btnInlineGenerateInline = QtWidgets.QPushButton(self.tab_7)
        self.btnInlineGenerateInline.setObjectName("btnInlineGenerateInline")
        self.gridLayout_5.addWidget(self.btnInlineGenerateInline, 2, 5, 1, 1)
        self.btnInlineGenerateMetric = QtWidgets.QPushButton(self.tab_7)
        self.btnInlineGenerateMetric.setObjectName("btnInlineGenerateMetric")
        self.gridLayout_5.addWidget(self.btnInlineGenerateMetric, 3, 5, 1, 1)
        self.plainTextEdit = QtWidgets.QPlainTextEdit(self.tab_7)
        self.plainTextEdit.setEnabled(False)
        self.plainTextEdit.setObjectName("plainTextEdit")
        self.gridLayout_5.addWidget(self.plainTextEdit, 9, 0, 1, 6)
        self.tabWidget.addTab(self.tab_7, "")
        self.horizontalLayout.addWidget(self.tabWidget)
        self.label.setBuddy(self.editDstDir)
        self.label_2.setBuddy(self.comboFail)
        self.label_3.setBuddy(self.comboUnhit)
        self.label_4.setBuddy(self.comboExclude)
        self.label_6.setBuddy(self.comboNewline_DirEncode)
        self.label_5.setBuddy(self.comboEncode_DirEncode)
        self.label_8.setBuddy(self.editBaseSource)
        self.label_7.setBuddy(self.editNewSource)
        self.label_10.setBuddy(self.editNewSource)
        self.label_15.setBuddy(self.editMinMetric)
        self.label_12.setBuddy(self.editNewSource)
        self.label_11.setBuddy(self.editNewSource)
        self.label_9.setBuddy(self.editNewSource)
        self.label_13.setBuddy(self.editNewSource)
        self.label_14.setBuddy(self.editNewSource)

        self.retranslateUi(ToolBoxDialog)
        self.tabWidget.setCurrentIndex(3)
        self.tabWidget_2.setCurrentIndex(0)
        self.btnDstDir.clicked.connect(ToolBoxDialog.onBtnDstDir)
        self.btnAction_DirEncode.clicked.connect(ToolBoxDialog.onBtnActionDirEncode)
        self.btnAction_DirKatakana.clicked.connect(ToolBoxDialog.onBtnActionDirKatakana)
        self.btnNewSource.clicked.connect(ToolBoxDialog.onBtnNewSource)
        self.btnBaseSource.clicked.connect(ToolBoxDialog.onBtnBaseSource)
        self.btnExtractFunc.clicked.connect(ToolBoxDialog.onBtnExtractFunc)
        self.btnExtractFuncDiff.clicked.connect(ToolBoxDialog.onBtnExtractFuncDiff)
        self.btnGenerateTag.clicked.connect(ToolBoxDialog.onBtnGenerateTag)
        self.btnInlineSource.clicked.connect(ToolBoxDialog.onBtnInlineSource)
        self.btnInlineFunction.clicked.connect(ToolBoxDialog.onBtnInlineFunction)
        self.btnInlineInline.clicked.connect(ToolBoxDialog.onBtnInlineInline)
        self.btnInlineMetric.clicked.connect(ToolBoxDialog.onBtnInlineMetric)
        self.btnInlineTree.clicked.connect(ToolBoxDialog.onBtnInlineTree)
        self.btnInlineAdjust.clicked.connect(ToolBoxDialog.onBtnInlineAdjust)
        self.btnInlineGenerateTree.clicked.connect(ToolBoxDialog.onBtnInlineGenerateTree)
        self.btnInlineGenerateAdjust.clicked.connect(ToolBoxDialog.onBtnInlineGenerateAdjust)
        self.btnInlineGenerateInline.clicked.connect(ToolBoxDialog.onBtnInlineGenerateInline)
        self.btnInlineGenerateMetric.clicked.connect(ToolBoxDialog.onBtnInlineGenerateMetric)
        QtCore.QMetaObject.connectSlotsByName(ToolBoxDialog)

    def retranslateUi(self, ToolBoxDialog):
        _translate = QtCore.QCoreApplication.translate
        ToolBoxDialog.setWindowTitle(_translate("ToolBoxDialog", "ToolBox"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("ToolBoxDialog", "Text"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("ToolBoxDialog", "File"))
        self.label.setText(_translate("ToolBoxDialog", "Dest Dir"))
        self.btnDstDir.setText(_translate("ToolBoxDialog", "..."))
        self.groupBox.setTitle(_translate("ToolBoxDialog", "Exception Action"))
        self.label_2.setText(_translate("ToolBoxDialog", "Fail Files"))
        self.comboFail.setItemText(0, _translate("ToolBoxDialog", "Ignore"))
        self.comboFail.setItemText(1, _translate("ToolBoxDialog", "Copy"))
        self.comboUnhit.setItemText(0, _translate("ToolBoxDialog", "Ignore"))
        self.comboUnhit.setItemText(1, _translate("ToolBoxDialog", "Copy"))
        self.label_3.setText(_translate("ToolBoxDialog", "UnHit Files"))
        self.label_4.setText(_translate("ToolBoxDialog", "Excluded Files"))
        self.comboExclude.setItemText(0, _translate("ToolBoxDialog", "Ignore"))
        self.comboExclude.setItemText(1, _translate("ToolBoxDialog", "Copy"))
        self.btnAction_DirEncode.setText(_translate("ToolBoxDialog", "Action"))
        self.label_6.setText(_translate("ToolBoxDialog", "Output Newline"))
        self.label_5.setText(_translate("ToolBoxDialog", "Output Encode"))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_5), _translate("ToolBoxDialog", "Encode"))
        self.btnAction_DirKatakana.setText(_translate("ToolBoxDialog", "Action"))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_6), _translate("ToolBoxDialog", "Katakana"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), _translate("ToolBoxDialog", "Folder"))
        self.btnGenerateTag.setText(_translate("ToolBoxDialog", "Generate Tag"))
        self.btnExtractFunc.setText(_translate("ToolBoxDialog", "Extract"))
        self.btnExtractFuncDiff.setText(_translate("ToolBoxDialog", "Extract Diff"))
        self.btnBaseSource.setText(_translate("ToolBoxDialog", "..."))
        self.label_8.setText(_translate("ToolBoxDialog", "Base Source Dir"))
        self.btnNewSource.setText(_translate("ToolBoxDialog", "..."))
        self.label_7.setText(_translate("ToolBoxDialog", "New Source Dir"))
        self.groupBox_2.setTitle(_translate("ToolBoxDialog", "Output Field"))
        self.checkSubFuncName.setText(_translate("ToolBoxDialog", "Sub Function Names"))
        self.checkLoop.setText(_translate("ToolBoxDialog", "Loop"))
        self.checkCondition.setText(_translate("ToolBoxDialog", "Condition"))
        self.checkSubFuncCount.setText(_translate("ToolBoxDialog", "Sub Function Call Count"))
        self.checkStopline.setText(_translate("ToolBoxDialog", "Stop Line"))
        self.checkFilePath.setText(_translate("ToolBoxDialog", "File Path"))
        self.checkStartline.setText(_translate("ToolBoxDialog", "Start Line"))
        self.checkLines.setText(_translate("ToolBoxDialog", "Lines"))
        self.checkScope.setText(_translate("ToolBoxDialog", "Scope"))
        self.checkPrototype.setText(_translate("ToolBoxDialog", "Prototype"))
        self.checkFuncID.setText(_translate("ToolBoxDialog", "Function ID"))
        self.checkFuncName.setText(_translate("ToolBoxDialog", "Function Name"))
        self.checkInline.setText(_translate("ToolBoxDialog", "Inline"))
        self.checkHeaderline.setText(_translate("ToolBoxDialog", "Header Line"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_4), _translate("ToolBoxDialog", "Source"))
        self.btnInlineSource.setText(_translate("ToolBoxDialog", "..."))
        self.label_10.setText(_translate("ToolBoxDialog", "Function List"))
        self.label_15.setText(_translate("ToolBoxDialog", "Minimum Metric"))
        self.btnInlineFunction.setText(_translate("ToolBoxDialog", "..."))
        self.label_12.setText(_translate("ToolBoxDialog", "Metric File"))
        self.label_11.setText(_translate("ToolBoxDialog", "Inline List"))
        self.btnInlineMetric.setText(_translate("ToolBoxDialog", "..."))
        self.btnInlineInline.setText(_translate("ToolBoxDialog", "..."))
        self.label_9.setText(_translate("ToolBoxDialog", "Source Dir"))
        self.btnInlineGenerateAdjust.setText(_translate("ToolBoxDialog", "Generate"))
        self.btnInlineAdjust.setText(_translate("ToolBoxDialog", "..."))
        self.label_13.setText(_translate("ToolBoxDialog", "Inline Tree"))
        self.label_14.setText(_translate("ToolBoxDialog", "Metric File(Adjusted)"))
        self.btnInlineGenerateTree.setText(_translate("ToolBoxDialog", "Generate"))
        self.btnInlineTree.setText(_translate("ToolBoxDialog", "..."))
        self.btnInlineGenerateInline.setText(_translate("ToolBoxDialog", "Generate"))
        self.btnInlineGenerateMetric.setText(_translate("ToolBoxDialog", "Generate"))
        self.plainTextEdit.setPlainText(_translate("ToolBoxDialog", "01. Choose/Drag&Drop Source Dir\n"
"02. Choose/Drag&Drop Function List File\n"
"03. Choose Inline List File\n"
"04. Push Button after Inline List File\n"
"05. Filter Inline List File\n"
"06. Choose Metric File\n"
"07. Push Button after Metric File\n"
"08. Add metric data into Metric File\n"
"09. Choose Inline Tree File\n"
"10. Push Button after Inline Tree File\n"
"11. (Optional) Set Minimum Metric data\n"
"12. Choose Metric File(Adjusted)\n"
"13. Push Button after Metric File(Adjusted)"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_7), _translate("ToolBoxDialog", "Inline"))

from dropedit import DropEdit
from filefilterqt import FileFilterQt
