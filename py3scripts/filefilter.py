# -*- coding:utf-8 -*-
# VERSION: 0.1
import os
import re
import shutil
import logutil

LOGNAME = 'FileFilter'

class FileFilter(object):
    def __init__(self):
        self._srcdir = ''                   # Property:srcdir
        self._filterin = []
        self._filterex = []
        self._fileall   = set()               # Property(Read):fileall, Relative path of all files in the self._srcdir
        self._fileex    = set()               # Property(Read):fileall, Relative path of all files in the self._srcdir
        self._filehit   = set()               # Property(Read):filehit/fileother, Subset of self._filehit, which contains items that meet self._filter
        self._fileunhit = set()               # Property(Read):filehit/fileother, Subset of self._filehit, which contains items that meet self._filter
        self._logger = logutil.LogUtil().logger(LOGNAME)
        self._logger.log(20, 'New Object')
    def getSrcdir(self):
        return self._srcdir
    def setSrcdir(self, srcdir):
        ret = True
        fullpath = self._checkdir(srcdir)
        if not fullpath:
            ret = False
        else:
            if fullpath != self._srcdir:
                self._srcdir = fullpath
                # update filelist
                skiplength = len(self._srcdir) + 1
                self._fileall   = set()
                self._fileex    = set()
                self._filehit   = set()
                self._fileunhit = set()
                for dirpath, dirnames, filenames in os.walk(self._srcdir):
                    for filename in filenames:
                        fullpath = os.path.normpath(os.path.join(dirpath, filename))
                        self._fileall.add(fullpath[skiplength:])
        return ret
    def addIncludePattern(self, regex):
        return self._addPattern(regex, self._filterin)
    def addExcludePattern(self, regex):
        return self._addPattern(regex, self._filterex)
    def getIncludePattern(self, idx):
        return self._getPattern(idx, self._filterin)
    def getExcludePattern(self, idx):
        return self._getPattern(idx, self._filterex)
    def clearIncludePattern(self):
        self._filterin = []
    def clearExcludePattern(self):
        self._filterex = []
    def getAllFiles(self):
        return tuple(self._fileall)
    def getExcludeFiles(self):
        return tuple(self._fileex)
    def getIncludeFiles(self):
        return tuple(self._filehit + self._fileunhit)
    def getHitFiles(self):
        return tuple(self._filehit)
    def getUnHitFiles(self):
        return tuple(self._fileunhit)
    def checkFiles(self):
        for fitem in self._fileall:
            for item in self._filterex:
                if item.search(fitem):
                    self._fileex.add(fitem)
                    break
            else:
                for item in self._filterin:
                    if item.search(fitem):
                        self._filehit.add(fitem)
                        break
                else:
                    self._fileunhit.add(fitem)
    def _addPattern(self, regex, group):
        ret = True
        try:
            newptn = re.compile(regex)
            for item in group:
                if newptn.pattern == item.pattern:
                    break
            else:
                group.append(newptn)
        except Exception as e:
            self._logger.log(30, "RegEx Error:" + str(e))
            ret = False
        return ret
    def _getPattern(self, idx, group):
        if idx >= len(group) or idx < -len(group):
            return group[idx].pattern
        else:
            return ''
    @staticmethod
    def _checkdir(path):
        fullpath = os.path.abspath(path)
        if os.path.isdir(fullpath):
            return os.path.normpath(fullpath)
        else:
            return ''

