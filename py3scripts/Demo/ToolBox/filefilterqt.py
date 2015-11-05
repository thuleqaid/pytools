# -*- coding: utf-8 -*-
from PyQt4 import QtGui,QtCore
import os
import configparser
import re
import filefilter_ui
from collectscript import filefilter, logutil

class FileFilterQt(QtGui.QWidget):
    CONFIG_FILE = 'filefilter.ini'
    def __init__(self, parent=None):
        super(FileFilterQt, self).__init__(parent)
        self.setupUi()
    def setupUi(self):
        self._ui = filefilter_ui.Ui_FileFilterWidget()
        self._ui.setupUi(self)
        self._core = filefilter.FileFilter()
        self._conffile = os.path.join(logutil.scriptPath(),self.CONFIG_FILE)
        self._loadConfig()
    def onBtnSrcDir(self):
        self._ui.editSrcDir.setText(QtGui.QFileDialog.getExistingDirectory(self))
    def onBtnRefresh(self):
        self._core.setSrcdir(self._ui.editSrcDir.text())
        self._setList(self._core.getAllFiles(), self._ui.listAll)
        self._ui.tabWidget.setCurrentIndex(0)
    def onBtnPreview(self):
        self._core.clearExcludePattern()
        if self._ui.comboEx1.currentIndex() > 0:
            self._core.addExcludePattern(self._ui.editEx1.text())
        if self._ui.comboEx2.currentIndex() > 0:
            self._core.addExcludePattern(self._ui.editEx2.text())
        if self._ui.comboEx3.currentIndex() > 0:
            self._core.addExcludePattern(self._ui.editEx3.text())
        self._core.clearIncludePattern()
        if self._ui.comboIn1.currentIndex() > 0:
            self._core.addIncludePattern(self._ui.editIn1.text())
        if self._ui.comboIn2.currentIndex() > 0:
            self._core.addIncludePattern(self._ui.editIn2.text())
        if self._ui.comboIn3.currentIndex() > 0:
            self._core.addIncludePattern(self._ui.editIn3.text())
        self._core.checkFiles()
        self._setList(self._core.getHitFiles(), self._ui.listHit)
        self._setList(self._core.getUnHitFiles(), self._ui.listUnhit)
        self._setList(self._core.getExcludeFiles(), self._ui.listExclude)
        self._ui.tabWidget.setCurrentIndex(1)
    def onComboEx1(self, idx):
        self._onComboChanged(idx, self._ui.comboEx1, self._ui.editEx1)
    def onComboEx2(self, idx):
        self._onComboChanged(idx, self._ui.comboEx2, self._ui.editEx2)
    def onComboEx3(self, idx):
        self._onComboChanged(idx, self._ui.comboEx3, self._ui.editEx3)
    def onComboIn1(self, idx):
        self._onComboChanged(idx, self._ui.comboIn1, self._ui.editIn1)
    def onComboIn2(self, idx):
        self._onComboChanged(idx, self._ui.comboIn2, self._ui.editIn2)
    def onComboIn3(self, idx):
        self._onComboChanged(idx, self._ui.comboIn3, self._ui.editIn3)
    def onEditEx1(self, txt):
        self._onEditChanged(txt, self._ui.comboEx1, self._ui.editEx1)
    def onEditEx2(self, txt):
        self._onEditChanged(txt, self._ui.comboEx2, self._ui.editEx2)
    def onEditEx3(self, txt):
        self._onEditChanged(txt, self._ui.comboEx3, self._ui.editEx3)
    def onEditIn1(self, txt):
        self._onEditChanged(txt, self._ui.comboIn1, self._ui.editIn1)
    def onEditIn2(self, txt):
        self._onEditChanged(txt, self._ui.comboIn2, self._ui.editIn2)
    def onEditIn3(self, txt):
        self._onEditChanged(txt, self._ui.comboIn3, self._ui.editIn3)
    def _onComboChanged(self, idx, comboitem, edititem):
        if idx == 0:
            edititem.setText('')
        elif idx > 1:
            edititem.setText(comboitem.itemData(idx))
    def _onEditChanged(self, txt, comboitem, edititem):
        if len(txt.strip()) <= 0:
            comboitem.setCurrentIndex(0)
        else:
            comboitem.setCurrentIndex(1)
    def _setList(self, data, listitem):
        listitem.clear()
        for item in sorted(data):
            listitem.addItem(item)
    def _loadConfig(self):
        if not self._validConfig():
            self._initConfig()
        config = configparser.ConfigParser()
        with open(self._conffile, 'r', encoding='utf-8') as fh:
            config.read_file(fh)
        for item in config.items('ExcludePattern', raw=True):
            self._ui.comboEx1.addItem(item[0],item[1])
            self._ui.comboEx2.addItem(item[0],item[1])
            self._ui.comboEx3.addItem(item[0],item[1])
        for item in config.items('FilterPattern', raw=True):
            self._ui.comboIn1.addItem(item[0],item[1])
            self._ui.comboIn2.addItem(item[0],item[1])
            self._ui.comboIn3.addItem(item[0],item[1])
    def _validConfig(self):
        ret=True
        if os.path.isfile(self._conffile):
            config=configparser.ConfigParser()
            with open(self._conffile,'r',encoding='utf-8') as fh:
                config.read_file(fh)
            for sectname in ('ExcludePattern','FilterPattern'):
                if not config.has_section(sectname):
                    ret=False
                    break
        else:
            ret=False
        return ret
    def _initConfig(self):
        config=configparser.ConfigParser()
        config.add_section('ExcludePattern')
        sep = re.escape(os.sep)
        config.set('ExcludePattern','Version Control Files',r'(\.vss$|'+sep+r'.svn'+sep+r'|^'+r'.svn'+sep+r'|'+sep+r'.git'+sep+r'|^'+r'.git'+sep+r')')
        config.set('ExcludePattern','Python Compiled Files',r'\.pyc$')
        config.add_section('FilterPattern')
        config.set('FilterPattern','C/C++ Files',r'\.(c|c\+\+|cc|cp|cpp|cxx|h|h\+\+|hh|hp|hpp|hxx)$')
        config.set('FilterPattern','Python Files',r'\.(py|pyx|pxd|pxi|scons)$')
        with open(self._conffile,'w',encoding='utf-8') as fh:
            config.write(fh)

if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    # Change UI Language based on system
    locale = QtCore.QLocale.system()
    trans = QtCore.QTranslator()
    trans.load("filefilter_{}.qm".format(locale.name()))
    app.installTranslator(trans)

    mw  = FileFilterQt()
    mw.show()
    app.exec_()

