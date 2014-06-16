from PyQt4 import QtCore
import dnsshr_util

class DNSSHRThread(QtCore.QThread):
    def __init__(self,parent=None):
        super(DNSSHRThread,self).__init__(parent)
        self._username=''
        self._passwd=''
        self._year=-1
        self._month=-1
        self._cardtime=None
        self._overtime=None
        self._leavetime=None
    def setAccount(self,username,passwd):
        self._username=username
        self._passwd=passwd
    def setDate(self,year,month):
        self._year=year
        self._month=month
    def run(self):
        hr=dnsshr_util.DNSSHR()
        self.emit(QtCore.SIGNAL("threadStatus(const QString&)"),"Loging in...")
        x=hr.login(self._username,self._passwd)
        if x:
            self.emit(QtCore.SIGNAL("threadStatus(const QString&)"),"Retriving CardTime...")
            self._cardtime=hr.record(self._year,self._month)
            self.emit(QtCore.SIGNAL("threadStatus(const QString&)"),"Retriving OverTime...")
            self._overtime=hr.overtime(self._year,self._month)
            self.emit(QtCore.SIGNAL("threadStatus(const QString&)"),"Retriving LeaveTime...")
            self._leavetime=hr.leavetime(self._year,self._month)
            self.emit(QtCore.SIGNAL("threadStatus(const QString&)"),"Done.")
        else:
            self.emit(QtCore.SIGNAL("threadStatus(const QString&)"),"Account Error.")
    def cardtime(self):
        return self._cardtime
    def overtime(self):
        return self._overtime
    def leavetime(self):
        return self._leavetime
