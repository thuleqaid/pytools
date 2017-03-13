# -*- coding: utf-8 -*-
# FileName: main.py
from PyQt4 import QtGui,QtCore
import sys
import os
import configparser
import fc_ui # ui界面转换生成的python文件
from fc_ui import _translate
from foldercompare import FolderCompare
from collectscript import logutil

if hasattr(sys, 'frozen'):
    SELFPATH = logutil.scriptPath(sys.executable)
else:
    SELFPATH = logutil.scriptPath(__file__)

class MainDialog(QtGui.QDialog):
        def setupUi(self):
            self._ui = fc_ui.Ui_Dialog() # Ui_Dialog类是test_ui文件中的唯一一个类
            self._ui.setupUi(self) # 应用界面
            self._fc = FolderCompare()
            self._loadLastInfo()
        def closeEvent(self, event):
            self._saveLastInfo()
            event.accept()
        def onBtnPath1(self):
            self._ui.editPath1.setText(QtGui.QFileDialog.getExistingDirectory(self, _translate("Dialog", "Base Source Path", None), self._ui.editPath1.text()))
        def onBtnPath2(self):
            self._ui.editPath2.setText(QtGui.QFileDialog.getExistingDirectory(self, _translate("Dialog", "Modified Source Path", None), self._ui.editPath2.text()))
        def onBtnOutpath(self):
            self._ui.editOutpath.setText(QtGui.QFileDialog.getExistingDirectory(self, _translate("Dialog", "Output Path", None), self._ui.editOutpath.text()))
        def onBtnTemppath(self):
            self._ui.editTemppath.setText(QtGui.QFileDialog.getExistingDirectory(self, _translate("Dialog", "Temp Path", None), self._ui.editTemppath.text()))
        def onBtnBCompare(self):
            self._ui.editBCompare.setText(QtGui.QFileDialog.getOpenFileName(self, _translate("Dialog", "BCompare.exe Path", None), self._ui.editBCompare.text()))
        def onBtnStep1(self):
            if self._setFCParam():
                self._fc.run1()
        def onBtnStep2(self):
            if self._setFCParam():
                self._fc.run2()
        def onBtnStep3(self):
            if self._setFCParam():
                self._fc.run3()
        def onBtnStep4(self):
            if self._setFCParam():
                self._fc.run4(self._ui.spinBox.value())
        def onBtnStep5(self):
            if self._setFCParam():
                self._fc.run5()
        def onBtnStepAll(self):
            if self._setFCParam():
                self._fc.run1()
                self._fc.run2()
                self._fc.run3()
                self._fc.run4(self._ui.spinBox.value())
                self._fc.run5()
        def onBtnStepExcel(self):
            if self._setFCParam():
                self._fc.runExcel()
        def onBtnOpenHtml(self):
            outdir = self._ui.editOutpath.text()
            summary = self._ui.editSummary.text()
            os.startfile(os.path.join(outdir, summary))
        def onBtnOpenOutDir(self):
            outdir = self._ui.editOutpath.text()
            os.startfile(outdir)
        def onBtnOpenExcel(self):
            outdir = self._ui.editOutpath.text()
            summary = os.path.splitext(self._ui.editSummary.text())[0] + '.xlsm'
            os.startfile(os.path.join(outdir, summary))
        def _setFCParam(self):
            ret = False
            path1 = self._ui.editPath1.text()
            path2 = self._ui.editPath2.text()
            path3 = self._ui.editOutpath.text()
            path4 = self._ui.editTemppath.text()
            path5 = self._ui.editBCompare.text()
            if os.path.isdir(path1) and os.path.isdir(path2) and os.path.isfile(path5):
                self._fc.setPath(path1, path2, path3, path4)
                self._fc.setBComp(path5)
                filter = self._ui.editFilter.text()
                self._fc.setFilter(filter)
                summary = self._ui.editSummary.text()
                self._fc.setSummaryFile(summary)
                ret = True
            return ret
        def _loadLastInfo(self):
            infofile = os.path.join(SELFPATH, 'last.ini')
            if os.path.isfile(infofile):
                config = configparser.ConfigParser()
                config.read(infofile)
                self._ui.editPath1.setText(config['LAST'].get('Path1', ''))
                self._ui.editPath2.setText(config['LAST'].get('Path2', ''))
                self._ui.editOutpath.setText(config['LAST'].get('Outpath', ''))
                self._ui.editTemppath.setText(config['LAST'].get('Temppath', ''))
                self._ui.editBCompare.setText(config['LAST'].get('BeyondCompare', ''))
                self._ui.editFilter.setText(config['LAST'].get('Filter', ''))
                self._ui.spinBox.setValue(int(config['LAST'].get('Neighbor', 5)))
        def _saveLastInfo(self):
            config = configparser.ConfigParser()
            config['LAST'] = {}
            config['LAST']['Path1'] = self._ui.editPath1.text()
            config['LAST']['Path2'] = self._ui.editPath2.text()
            config['LAST']['Outpath'] = self._ui.editOutpath.text()
            config['LAST']['Temppath'] = self._ui.editTemppath.text()
            config['LAST']['BeyondCompare'] = self._ui.editBCompare.text()
            config['LAST']['Filter'] = self._ui.editFilter.text()
            config['LAST']['Neighbor'] = str(self._ui.spinBox.value())
            infofile = os.path.join(SELFPATH, 'last.ini')
            with open(infofile, 'w') as fh:
                config.write(fh)

if __name__ == '__main__':
        app = QtGui.QApplication(sys.argv)
        # 根据当前系统的默认语言，选择语言包
        # 语言包文件放在当前路径中，文件名是"test_语言名.qm"
        locale = QtCore.QLocale.system()
        trans = QtCore.QTranslator()
        trans.load("fc_{}.qm".format(locale.name()))
        app.installTranslator(trans)
        # 启动程序
        mw  = MainDialog()
        mw.setupUi()
        mw.show()
        app.exec_()
