import sys
import os

from PyQt4 import QtGui

import encodeentry
import vimentry
import dnsshrentry

class ToolkitsWindow(QtGui.QMainWindow):
    def setupUi(self,ui=None):
        if ui:
            self._ui=ui
        else:
            import toolkits_ui
            self._ui=toolkits_ui.Ui_MainWindow()
        self._ui.setupUi(self)
        self.addTab(vimentry.MainWidget(),'Vim')
        self.addTab(encodeentry.MainWidget(),'Encode')
        self.addTab(dnsshrentry.MainWidget(),'DNSSHR')
    def onTabChanged(self,index):
        pass
    def addTab(self,widget,tabname):
        widget.setupUi()
        self._ui.tabWidget.addTab(widget,tabname)

if __name__ == '__main__':
    app=QtGui.QApplication(sys.argv)
    mw=ToolkitsWindow(None)
    mw.setupUi()
    mw.show()
    app.exec_()
