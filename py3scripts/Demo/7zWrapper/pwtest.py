# -*- coding:utf-8 -*-
import os
import sys
import datetime
from argparse import ArgumentParser
from collectscript import logutil
import zwrapper
import pwmanager

if hasattr(sys,'frozen'):
    SELFPATH = logutil.scriptPath(sys.executable)
else:
    SELFPATH = logutil.scriptPath(__file__)
LOGCONFIG = os.path.join(SELFPATH, 'logging.conf')

LOGNAME = "PWTest"
logutil.registerLogger(LOGNAME)

class PWTest(object):
    def __init__(self):
        self._log = logutil.LogUtil().logger(LOGNAME)
        self._zwrapper = zwrapper.ZWrapper()
        self._pwmanager = None
    def test(self, archive):
        password = ''
        flag = self._zwrapper.isEncrypted(archive)
        if flag:
            if not self._pwmanager:
                self._pwmanager = pwmanager.PasswordManager()
                self._pwmanager.openDB()
            allpw = self._pwmanager.getPasswords('send')
            allpw.extend(self._pwmanager.getPasswords('receive'))
            for item in allpw:
                if self._zwrapper.testPassword(archive, item[1]):
                    password = item[1]
                    break
        self._log.log(10, 'Test archive:{}, Encrypted:{}'.format(archive, flag))
        if (flag and password!='') or (not flag):
            rootdir = os.path.dirname(os.path.abspath(archive))
            os.chdir(rootdir)
            now = datetime.datetime.now()
            destpath = now.strftime('%Y%m%d-%H%M%S')
            self._zwrapper.extract(archive, destpath, password)
            expectdir = os.path.splitext(os.path.basename(archive))[0]
            subitems = os.listdir(destpath)
            if len(subitems) == 1:
                subpath = os.path.join(destpath, subitems[0])
                if os.path.isdir(subpath):
                    os.rename(subpath, subitems[0])
                    os.rmdir(destpath)
                else:
                    os.rename(destpath, expectdir)
            else:
                os.rename(destpath, expectdir)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-l','--log',dest='flag_log',action='store_true',default=False,help='generate log config')
    parser.add_argument('archive')
    options=parser.parse_args()
    if options.flag_log:
        logutil.newConf(LOGCONFIG)
    logutil.LogUtil(LOGCONFIG)

    pw = PWTest()
    pw.test(options.archive)
