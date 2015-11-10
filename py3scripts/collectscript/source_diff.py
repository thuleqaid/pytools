# -*- coding: utf-8 -*-
import sys
import os
import re
import tempfile
import subprocess
from .logutil import LogUtil, scriptPath, registerLogger
#from .multithread import multithread
from .guess import guessEncode
from .tagparser import CscopeParser

LOGNAME = 'SourceDiff'
registerLogger(LOGNAME)

class SourceDiff(object):
    DIFFBIN = os.path.join(scriptPath(),'bin','diff.exe')
    PAT_DIFF = re.compile(r'^Files\s+(?P<file1>.+?)\s+and\s+(?P<file2>.+?)\s+differ$')
    PAT_ORPHAN = re.compile(r'^Only\s+in\s+(?P<path>.+?):\s+(?P<file>.+?)$')
    PAT_COMMENT1 = re.compile(r'//.*')
    PAT_COMMENT2 = re.compile(r'/\*(.|\n)+?\*/')
    PAT_DIFFLINE = re.compile(r'^(?P<line1>\d+)(,(?P<line2>\d+))?(?P<act>[acd])(?P<line3>\d+)(,(?P<line4>\d+))?$')
    def __init__(self, oldsrcdir, newsrcdir):
        self._log = LogUtil().logger(LOGNAME)
        self._log.log(20, 'Create Object:[{}] vs [{}]'.format(oldsrcdir, newsrcdir))
        # load tag info
        self._tag = CscopeParser(os.path.join(newsrcdir,'cscope.out'))
        # get diff files
        self._getBriefDiff(oldsrcdir, newsrcdir)
        # compare diff files
        self._results = {}
        for item in self._diffpair:
            self._diff2Files(item[0],item[1])
    def getDiffFuncs(self):
        outdict = {}
        for key,value in self._results.items():
            outdict[key] = value['funcs']
        return outdict
    def getDiffLines(self):
        outdict = {}
        for key,value in self._results.items():
            outdict[key] = sorted(value['lines'])
        return outdict
    def getDiffFiles(self):
        outlist = [[],[]]
        for item in self._diffpair:
            outlist[0].append(item[0])
            outlist[1].append(item[1])
        return outlist
    def getOrphanFiles(self):
        outlist = [[],[]]
        for item in self._orphan1:
            outlist[0].append(os.path.join(item[0],item[1]))
        for item in self._orphan2:
            outlist[1].append(os.path.join(item[0],item[1]))
        return outlist
    def report(self, reportfile):
        rootpath = self._tag._root
        fh = open(reportfile, 'w', encoding='utf_8_sig')
        difffile = self.getDiffFiles()
        difffunc = self.getDiffFuncs()
        diffline = self.getDiffLines()
        for key in sorted(difffile[1]):
            lines = diffline[key]
            funcs = difffunc[key]
            lineidx = 0
            funcidx = 0
            relpath = key[len(rootpath)+1:]
            while lineidx < len(lines) and funcidx < len(funcs):
                if lines[lineidx] < int(funcs[funcidx].startline):
                    fh.write("{0}\t{2}\t{1}\n".format(relpath, 'ToDo', lines[lineidx]))
                    lineidx += 1
                else:
                    fh.write("{0}\t{2}\t{1}\t{3}\n".format(relpath, funcs[funcidx].name, funcs[funcidx].startline, funcs[funcidx].stopline))
                    funcidx += 1
            while funcidx < len(funcs):
                fh.write("{0}\t{2}\t{1}\t{3}\n".format(relpath, funcs[funcidx].name, funcs[funcidx].startline, funcs[funcidx].stopline))
                funcidx += 1
            while lineidx < len(lines):
                fh.write("{0}\t{2}\t{1}\n".format(relpath, 'ToDo', lines[lineidx]))
                lineidx += 1
    def _getBriefDiff(self, oldsrcdir, newsrcdir):
        path1 = os.path.normpath(os.path.abspath(oldsrcdir))
        path2 = os.path.normpath(os.path.abspath(newsrcdir))
        params = [self.DIFFBIN, '-rq', path1, path2]
        try:
            outputs = subprocess.check_output(params)
        except subprocess.CalledProcessError as e:
            outputs = e.output.decode('cp936').splitlines()
        self._diffpair = []
        self._orphan1 = []
        self._orphan2 = []
        for line in outputs:
            ret1 = self.PAT_DIFF.search(line)
            if ret1:
                self._diffpair.append((ret1.group('file1'), ret1.group('file2')))
            else:
                ret2 = self.PAT_ORPHAN.search(line)
                if ret2:
                    if ret2.group('path').startswith(path1):
                        self._orphan1.append((ret2.group('path'),ret2.group('file')))
                    elif ret2.group('path').startswith(path2):
                        self._orphan2.append((ret2.group('path'),ret2.group('file')))
                    else:
                        self._log.log(50, 'Unknow orphan file: [{}]'.format(line))
                else:
                    self._log.log(50, 'Unknow result pattern: [{}]'.format(line))
    def _diff2Files(self, file1, file2):
        fh = tempfile.NamedTemporaryFile(delete=False)
        fh11name = fh.name
        fh.close()
        fh = tempfile.NamedTemporaryFile(delete=False)
        fh21name = fh.name
        fh.close()
        #fh = tempfile.NamedTemporaryFile(delete=False)
        #fh12name = fh.name
        #fh.close()
        #fh = tempfile.NamedTemporaryFile(delete=False)
        #fh22name = fh.name
        #fh.close()
        fh12name = ''
        fh22name = ''

        self._commentFree(file1, fh12name, fh11name)
        self._commentFree(file2, fh22name, fh21name)
        ## compare comment free version
        #params = [self.DIFFBIN, '-wbB', fh12name, fh22name]
        #try:
            #outputs = subprocess.check_output(params)
        #except subprocess.CalledProcessError as e:
            #outputs = e.output.decode('utf-8').splitlines()
        #fh = open(fh22name,'r',encoding='utf_8_sig',errors='ignore')
        #lines = fh.readlines()
        #fh.close()
        #os.remove(fh12name)
        #os.remove(fh22name)
        #diff_src = set()
        #for line in outputs:
            #ret = self.PAT_DIFFLINE.search(line)
            #if ret:
                #line3 = int(ret.group('line3'))
                #line4 = ret.group('line4')
                #act   = ret.group('act')
                #if act == 'a':
                    ## skip empty lines for add mode
                    #if line4:
                        #for lineidx in range(line3,int(line4)+1):
                            #if lines[lineidx - 1].strip() != '':
                                #diff_src.add(lineidx)
                    #else:
                        #if lines[line3 - 1].strip() != '':
                            #diff_src.add(line3)
                #else:
                    #if line4:
                        #diff_src |= set(range(line3,int(line4)+1))
                    #else:
                        #diff_src.add(line3)
        # compare full version
        params = [self.DIFFBIN, '-wbB', fh11name, fh21name]
        try:
            outputs = subprocess.check_output(params)
        except subprocess.CalledProcessError as e:
            outputs = e.output.decode('utf-8').splitlines()
        os.remove(fh11name)
        os.remove(fh21name)
        diff_all = set()
        for line in outputs:
            ret = self.PAT_DIFFLINE.search(line)
            if ret:
                line3 = int(ret.group('line3'))
                line4 = ret.group('line4')
                if line4:
                    diff_all |= set(range(line3,int(line4)+1))
                else:
                    diff_all.add(line3)
        modfuncs = []
        for item in self._tag.getFuncByFile(file2, True):
            lineset = set(range(int(item.startline), int(item.stopline)+1))
            if not lineset.isdisjoint(diff_all):
                diff_all -= lineset
                #diff_src -= lineset
                modfuncs.append(item)
        self._results[file2] = {'funcs':modfuncs, 'lines':diff_all}

    def _commentFree(self, infile, outfile1='', outfile2=''):
        encode = guessEncode(infile, 'cp932','cp936')[0]
        if encode:
            fh = open(infile, 'r', encoding=encode, errors='ignore')
        else:
            fh = open(infile, 'r', errors='ignore')
        data = fh.read()
        fh.close()
        if outfile2:
            fh = open(outfile2, 'w', encoding='utf_8_sig', errors='ignore')
            fh.write(data)
            fh.close()
        if outfile1:
            lastidx = 0
            newdata = ''
            for cmt in self.PAT_COMMENT2.finditer(data):
                matchtxt = cmt.group()
                matchpos = cmt.span()
                linecnt = matchtxt.count('\n')
                newdata = newdata + data[lastidx:matchpos[0]] + ('\n' * linecnt)
                lastidx = matchpos[1]
            newdata = newdata + data[lastidx:]
            newdata = self.PAT_COMMENT1.sub('', newdata)
            fh = open(outfile1, 'w', encoding='utf_8_sig', errors='ignore')
            for line in newdata.splitlines():
                fh.write(line.rstrip())
                fh.write("\n")
            fh.close()

if __name__ == '__main__':
    oldsrcdir = 'd:/Fragrans/03IMPLEMENT/0303UnitTest/14_20150921_VSA_AB0100/02_Task/04_SourceCode/01_C0C1/AB0100_SRC_utf8_6608'
    newsrcdir = 'd:/Fragrans/03IMPLEMENT/0303UnitTest/14_20150921_VSA_AB0100/02_Task/04_SourceCode/01_C0C1/AB0100_SRC_utf8_6671'
    sd = SourceDiff(oldsrcdir, newsrcdir)
    difffile = sd.getDiffFiles()
    difffunc = sd.getDiffFuncs()
    diffline = sd.getDiffLines()
    for key in sorted(difffile[1]):
        lines = diffline[key]
        funcs = difffunc[key]
        lineidx = 0
        funcidx = 0
        while lineidx < len(lines) and funcidx < len(funcs):
            if lines[lineidx] < int(funcs[funcidx].startline):
                print("{}\tToDo\t{}".format(key, lines[lineidx]))
                lineidx += 1
            else:
                print("{}\t{}\t{}\t{}".format(key, funcs[funcidx].name, funcs[funcidx].startline, funcs[funcidx].stopline))
                funcidx += 1
        while funcidx < len(funcs):
            print("{}\t{}\t{}\t{}".format(key, funcs[funcidx].name, funcs[funcidx].startline, funcs[funcidx].stopline))
            funcidx += 1
        while lineidx < len(lines):
            print("{}\tToDo\t{}".format(key, lines[lineidx]))
            lineidx += 1
