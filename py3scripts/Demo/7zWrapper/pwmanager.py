# -*- coding:utf-8 -*-
import os
import sys
import collections
from collectscript import logutil
# sqlite3 implementation
import sqlite3

if hasattr(sys,'frozen'):
    SELFPATH = logutil.scriptPath(sys.executable)
else:
    SELFPATH = logutil.scriptPath(__file__)
LOGCONFIG = os.path.join(SELFPATH, 'logging.conf')

LOGNAME = "PasswordManager"
logutil.registerLogger(LOGNAME)

class IPasswordManager(object):
    PWInfo = collections.namedtuple('PWInfo', ['label', 'password', 'dirty'])
    def __init__(self, dbfile=os.path.join(SELFPATH,'passwd')):
        self._log = logutil.LogUtil().logger(LOGNAME)
        self._defaultpw = 'master-code'
        self._dbfile = dbfile
        self._checkDB()
        self._send = [] # password list for create archive
        self._receive = [] # password list for extract archive
    def openDB(self, password=''):
        if not password:
            password = self._defaultpw
        self._send = [] # password list for create archive
        self._receive = [] # password list for extract archive
        # verify password
        if self._verifyPassword(password):
            self._log.log(10, 'Password Matched')
            # load data
            self._loadData(password)
            ret = True
        else:
            self._log.log(10, 'Wrong Password')
            ret = False
        return ret
    def getPassword(self, sect, label):
        # sect: send/receive
        # label: unique in the sect
        sect = sect.upper()
        if sect == 'SEND':
            plist = self._send
        elif sect == 'RECEIVE':
            plist = self._receive
        else:
            plist = []
        passwd = ''
        for item in plist:
            if item.label == label:
                passwd = item.dirty[-1]
                break
        return passwd
    def getPasswords(self, sect):
        # sect: send/receive
        sect = sect.upper()
        if sect == 'SEND':
            plist = self._send
        elif sect == 'RECEIVE':
            plist = self._receive
        else:
            plist = []
        return [(x.label, x.dirty[-1]) for x in plist]
    def setPassword(self, sect, label, password):
        # sect: send/receive
        # label: unique in the sect
        sect = sect.upper()
        if sect == 'SEND':
            plist = self._send
        elif sect == 'RECEIVE':
            plist = self._receive
        else:
            return
        for item in plist:
            if item.label == label:
                if item.dirty[-1] != password:
                    item.dirty.append(password)
                break
        else:
            plist.append(self.PWInfo(label=label, password='', dirty=[password]))
    def writeDB(self, password=''):
        if not password:
            password = self._defaultpw
        # update database
        self._writeData(password)
    def _checkDB(self):
        # create database if not exists
        if os.path.isfile(self._dbfile):
            self._log.log(10, 'Open database file：{}'.format(self._dbfile))
        else:
            self._createDB()
            self._log.log(10, 'Create database file:{}'.format(self._dbfile))
    # To Be Implemented
    def _createDB(self):
        pass
    def _verifyPassword(self, password):
        pass
    def _loadData(self, password):
        pass
    def _writeData(self, password):
        pass

class PasswordManager(IPasswordManager):
    def __init__(self, dbfile=os.path.join(SELFPATH,'passwd')):
        super(PasswordManager, self).__init__(dbfile)
    def _createDB(self):
        con = sqlite3.connect(self._dbfile)
        cur = con.cursor()
        cur.execute('create table mastercode(code)')
        cur.execute('create table sendtable(label, code)')
        cur.execute('create table recvtable(label, code)')
        cur.execute('insert into mastercode(code) values (?)', (self._defaultpw,))
        con.commit()
        con.close()
    def _verifyPassword(self, password):
        con = sqlite3.connect(self._dbfile)
        cur = con.cursor()
        cur.execute('select code from mastercode')
        data = cur.fetchall()
        con.close()
        ret = False
        if data[0][0] == password:
            ret = True
        else:
            ret = False
        return ret
    def _loadData(self, password):
        con = sqlite3.connect(self._dbfile)
        cur = con.cursor()
        cur.execute('select label, code from sendtable')
        data1 = cur.fetchall()
        cur.execute('select label, code from recvtable')
        data2 = cur.fetchall()
        con.close()
        for item in data1:
            self._send.append(self.PWInfo(label=item[0], password=item[1], dirty=[item[1],]))
        for item in data2:
            self._receive.append(self.PWInfo(label=item[0], password=item[1], dirty=[item[1],]))
    def _writeData(self, password):
        con = sqlite3.connect(self._dbfile)
        cur = con.cursor()
        dirty = False
        for tobj,tname in ((self._send, 'sendtable'), (self._receive, 'recvtable')):
            for idx,item in enumerate(tobj):
                if item.password != '' and item.password != item.dirty[-1]:
                    # item changed
                    dirty = True
                    cur.execute('update {} set code=? where label=?'.format(tname), (item.dirty[-1], item.label))
                    tobj[idx] = tobj[idx]._replace(password=item.dirty[-1], dirty=[item.dirty[-1],])
                elif item.password == '' and item.dirty[-1] != '':
                    # new item
                    dirty = True
                    cur.execute('insert into {}(label, code) values (?,?)'.format(tname), (item.label, item.dirty[-1]))
                    tobj[idx] = tobj[idx]._replace(password=item.dirty[-1], dirty=[item.dirty[-1],])
        if dirty:
            con.commit()
        con.close()

if __name__ == '__main__':
    logutil.logConf(LOGCONFIG)
    logutil.LogUtil(LOGCONFIG)
    pm = PasswordManager()
    pm.openDB()
    pm.setPassword('send', 'ToXXX', '12345678')
    pm.setPassword('receive', 'FromXXX', '87654321')
    pm.writeDB()
