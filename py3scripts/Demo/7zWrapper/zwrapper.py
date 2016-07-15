# -*- coding:utf-8 -*-
import os
import sys
import datetime
from argparse import ArgumentParser
import subprocess
from collectscript import logutil, guess, multiprocess

if hasattr(sys,'frozen'):
    SELFPATH = logutil.scriptPath(sys.executable)
else:
    SELFPATH = logutil.scriptPath(__file__)
LOGCONFIG = os.path.join(SELFPATH, 'logging.conf')

LOGNAME = "ZWrapper"
logutil.registerLogger(LOGNAME)

class ZWrapper(object):
    def __init__(self):
        self._log = logutil.LogUtil().logger(LOGNAME)
        exename = '7z.exe'
        self._7z = os.path.join(guess.findExe(exename),exename)
        self._mp = multiprocess.MultiProcess()

    def pack(self, filelist, password=''):
        abspath = [os.path.abspath(x) for x in filelist]
        if len(abspath) == 1:
            rootdir = os.path.dirname(abspath[0])
        else:
            rootdir = os.path.commonpath(abspath)
        self._log.log(10, 'Root Path:{}'.format(rootdir))
        os.chdir(rootdir)
        items = [os.path.relpath(x, rootdir) for x in abspath]
        self._log.log(10, 'FileList:[{}]'.format('], ['.join(items)))
        commands = [self._7z, '-bso0', '-bse0', '-bsp0', 'a']
        now = datetime.datetime.now()
        archname = now.strftime('%Y%m%d-%H%M%S.zip')
        commands.append(archname)
        commands.extend(items)
        pwd = '-p{}'.format(password.strip())
        if len(pwd) > 2:
            commands.append(pwd)
            self._log.log(10, 'Create archive:{} with password'.format(archname))
        else:
            self._log.log(10, 'Create archive:{} without password'.format(archname))
        retcode = self._mp.call(commands)

    def isEncrypted(self, archive):
        commands = [self._7z, 'l', archive, '-slt']
        ret = self._mp.run(commands, stdout=subprocess.PIPE)
        newline = b'\r\n'
        encrypt_mask = newline + b'Encrypted = +' + newline
        maskpos = ret.stdout.find(encrypt_mask)
        ret = False
        if maskpos >= 0:
            ret = True
        else:
            ret = False
        return ret

    def testPassword(self, archive, password):
        commands = [self._7z, 't', archive, '-p{}'.format(password)]
        ret = self._mp.run(commands)
        if ret.returncode != 0:
            return False
        else:
            return True

    def extract(self, archive, destpath, password=''):
        commands = [self._7z, 'x', archive, '-o{}'.format(destpath), '-p{}'.format(password)]
        ret = self._mp.run(commands)
        if ret.returncode != 0:
            return False
        else:
            return True


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-l','--log',dest='flag_log',action='store_true',default=False,help='generate log config')
    parser.add_argument('-p', '--password', dest='password', action='store', default='12345678')
    parser.add_argument('--nopassword', action='store_true', default=False)
    parser.add_argument('files', nargs='+')
    options=parser.parse_args()
    if options.flag_log:
        logutil.newConf(LOGCONFIG)
    logutil.LogUtil(LOGCONFIG)

    zw = ZWrapper()
    if options.nopassword:
        password = ''
    else:
        password = options.password
    zw.pack(options.files, password)
