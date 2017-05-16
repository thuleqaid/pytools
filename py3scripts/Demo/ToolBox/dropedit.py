# -*- coding: utf-8 -*-
try:
    from PyQt4 import QtGui,QtCore
    from PyQt4.QtGui import QLineEdit
except:
    from PyQt5 import QtGui,QtCore
    from PyQt5.QtWidgets import QLineEdit
class DropEdit(QLineEdit):
    def __init__(self, parent):
        super(DropEdit, self).__init__(parent)
        self.setAcceptDrops(True)
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super(DropEdit, self).dragEnterEvent(event)
    def dragMoveEvent(self, event):
        super(DropEdit, self).dragMoveEvent(event)
    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            urllist = event.mimeData().urls()
            self.setText(urllist[0].toLocalFile())
            event.acceptProposedAction()
        else:
            super(DropEdit,self).dropEvent(event)

