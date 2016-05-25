# -*- coding:utf-8 -*-
# VERSION: 0.1
import re
import sys
import os
import collections
import pickle
import threading
import queue
from .logutil import LogUtil, registerLogger, scriptPath
from .guess import openTextFile, guessEncode, unescape, setDefaultEncode
from .multithread import MultiThread
from .multiprocess import MultiProcess

# Usage:
#   cscopeout = 'file path of cscope.out'
#   cp = tagparser.CscopeParser(cscopeout, sourceparser=tagparser.cscopeSourceParserEPS)
#   funcinfo = cp.outputFuncInfo(OUTFILE_FUNCTION, ['Path', 'HeaderLine', 'StartLine', 'StopLine', 'SubName', 'Loop', 'Prototype', 'FunctionName', 'FunctionID', 'Inline'])
#   ctags = 'file path of tags'
#   cp2 = tagparser.CtagsParser(ctags)
#   macroinfo = cp2.outputMacro(OUTFILE_MACRO, ['Path', 'Line', 'Scope', 'Value', 'Comment'])
#   varinfo = cp2.outputVar(OUTFILE_VAR, ['Path', 'Line', 'Scope', 'Type', 'Comment'])
#   sinfo,minfo,tinfo = cp2.outputType(OUTFILE_STRUCT, ['Path', 'Line', 'Scope', 'Comment'],
#                                      OUTFILE_MEMBER, ['Path', 'Line', 'Scope', 'Parent', 'Type', 'Comment'],
#                                      OUTFILE_TYPEDEF, ['Path', 'Line', 'Scope', 'Category', 'Type', 'Comment'])

LOGNAME = 'CscopeParser'
LOGNAME2 = 'CtagsParser'
LOGNAME3 = 'FormatSource'
registerLogger(LOGNAME)
registerLogger(LOGNAME2)
registerLogger(LOGNAME3)

def cacheCheck(latestfile, *otherfiles):
    logger = LogUtil().logger(LOGNAME)
    latestfile = os.path.normpath(os.path.abspath(latestfile))
    otherfiles = [os.path.normpath(os.path.abspath(x)) for x in otherfiles]
    logger.log(20, 'Test file[{}] in files[{}]'.format(latestfile, ','.join(otherfiles)))
    # 检查latestfile是不是追后生成的文件
    ret = False
    if os.path.isfile(latestfile):
        ctime = os.path.getmtime(latestfile)
        for otherfile in otherfiles:
            if os.path.getmtime(otherfile) > ctime:
                logger.log(10, 'Failed at file[{}]'.format(otherfile))
                break
        else:
            ret = True
    else:
        logger.log(10, 'File[{}] does not exist'.format(latestfile))
    return ret

class CscopeParser(object):
    PAT_FILE = re.compile(r'^\t@(?P<filename>\S+)$')
    PAT_LINE = re.compile(r'^(?P<lineno>\d+)\s*(?P<extra>.*)$')
    PAT_FUNCSTART = re.compile(r'^\t\$(?P<funcname>\S+)$')
    PAT_FUNCSTOP = re.compile(r'^\}$')
    PAT_FUNCCALL = re.compile(r'^\t`(?P<funcname>\S+)$')
    PAT_IF = re.compile(r'(?<!#)\bif\b')
    PAT_FOR = re.compile(r'\bfor\b')
    PAT_WHILE = re.compile(r'\bwhile\b')
    WORK_COUNT = 3
    # 函数情报类型 extra是从代码中读出的注释情报，其他的数据是从cscope.out中取得
    FuncInfo = collections.namedtuple('FuncInfo',['name','relpath','startline','stopline','calls','countif','countfor','countwhile','static', 'prototype', 'extra'])
    def __init__(self, cscopeout, encoding=None, sourceparser=None):
        # 初始化log
        self._log = LogUtil().logger(LOGNAME)
        if callable(sourceparser):
            self._cbfunc = sourceparser
        else:
            self._cbfunc = None
        # cscope.out文件的生成方法：cscope -Rbcu
        fullpath = os.path.normpath(os.path.abspath(cscopeout))
        self._root, self._cscope = os.path.split(fullpath)
        # 设置文件编码列表
        self._testcodes = ['cp932','cp936']
        if encoding and (encoding not in self._testcodes):
            self._testcodes.insert(0, encoding)
            setDefaultEncode(self._testcodes)
        self._log.log(20, 'New object[{},{}]'.format(self._root, self._cscope))
        if hasattr(sys,'frozen'):
            selffile = sys.executable
        else:
            selffile = __file__
        if not os.path.isfile(fullpath):
            # 自动生成cscope.out
            curdir = os.path.abspath('.')
            os.chdir(self._root)
            if os.name == 'nt':
                if sys.maxsize > 4294967296: # 2**32
                    self._log.log(10, "Generating tag file in Win64")
                    exename = os.path.join(scriptPath(), 'bin', 'cscope_64.exe')
                else:
                    self._log.log(10, "Generating tag file in Win32")
                    exename = os.path.join(scriptPath(), 'bin', 'cscope.exe')
            else:
                self._log.log(10, "Generating tag file in Unix")
                exename = 'cscope'
            params = [exename, '-Rbcu']
            mp = MultiProcess()
            mp_ret = mp.call(params)
            os.chdir(curdir)
            if mp_ret:
                self._log.log(50, "Error in generating tag file")
                self._funcs = []
                return
        if cacheCheck(os.path.join(self._root,'cscope.cache'), selffile, fullpath):
            self._log.log(10, 'Read Cache')
            self._readCache()   # 从cache文件读入分析结果
        else:
            if self._cbfunc:
                self._worker = MultiThread(3)
                self._worker.register(self._readSource)
                self._worker.start()
            self._parse()       # 分析cscope.out文件，同时把要解析的源代码文件加入到队列中
            if self._cbfunc:
                self._worker.join()
            self._writeCache()  # 将分析结果写入cache文件
            self._log.log(10, 'Write Cache')
    def getFuncInfo(self, *funcnames):
        # 根据函数名查找函数情报
        outlist = []
        for item in self._funcs:
            if item.name in funcnames:
                outlist.append(item)
        return outlist
    def getFuncByFile(self, filename, fullpath=False):
        self._log.log(10, "[{}][{}]".format(filename, fullpath))
        if fullpath:
            abspath = os.path.normpath(os.path.abspath(filename))
        else:
            abspath = os.path.normpath(os.path.abspath(os.path.join(self._root, filename)))
        if abspath.startswith(self._root):
            targetfile = abspath[len(self._root)+1:].replace('\\','/')
        else:
            targetfile = ''
        self._log.log(10, "  Target file[{}]".format(targetfile))
        outlist = [x for x in self._funcs if x.relpath == targetfile]
        return outlist

    def outputFuncInfo(self, outfile, fields, funclist=None):
        outdata = [['#Function']]
        for field in fields:
            if field == 'Path':
                outdata[0].append('Path')
            elif field == 'StartLine':
                outdata[0].append('StartLine')
            elif field == 'StopLine':
                outdata[0].append('StopLine')
            elif field == 'SubCount':
                outdata[0].append('SubFunctionCallCount')
            elif field == 'SubName':
                outdata[0].append('SubFunctionName')
            elif field == 'Condition':
                outdata[0].append('ConditionCount')
            elif field == 'Loop':
                outdata[0].append('LoopCount')
            elif field == 'Scope':
                outdata[0].append('Scope')
            elif field == 'Prototype':
                outdata[0].append('Prototype')
            else:
                outdata[0].append(field)
        if not funclist:
            funclist = self._funcs
        for item in funclist:
            outdata.append([item.name])
            self._log.log(10, item.name)
            for field in fields:
                if field == 'Path':
                    outdata[-1].append(item.relpath)
                elif field == 'StartLine':
                    outdata[-1].append(item.startline)
                elif field == 'StopLine':
                    outdata[-1].append(item.stopline)
                elif field == 'SubCount':
                    outdata[-1].append(len(item.calls))
                elif field == 'SubName':
                    outdata[-1].append(','.join(item.calls))
                elif field == 'Condition':
                    outdata[-1].append(item.countif)
                elif field == 'Loop':
                    outdata[-1].append(item.countfor+item.countwhile)
                elif field == 'Scope':
                    if item.static:
                        outdata[-1].append('Local')
                    else:
                        outdata[-1].append('Global')
                elif field == 'Prototype':
                    outdata[-1].append(item.prototype)
                else:
                    outdata[-1].append(item.extra.get(field,''))
        self._log.log(10, "[{}][{}]".format(outfile, ','.join(fields)))
        if outfile:
            # 输出函数列表
            fh=open(outfile,'w',encoding='utf-8')
            for idx,item in enumerate(outdata):
                if idx == 0:
                    colidx = '#No'
                else:
                    colidx = idx
                fh.write('{}\t{}\n'.format(colidx, '\t'.join([str(x) for x in item])))
            fh.close()
        return outdata
    @classmethod
    def getFuncCall_asdict(cls, funcinfo):
        # 输出调用的函数列表，key是函数名，value是函数出现的index(从0开始)数组(一个函数可能被多次调用)
        outdict = collections.OrderedDict()
        for idx,func in enumerate(funcinfo.calls):
            outdict.setdefault(func,[]).append(idx)
        return outdict
    def _parse(self):
        # 读取cscope.out文件，提取函数情报
        fh = open(os.path.join(self._root, self._cscope), 'r', errors='ignore')
        lines = fh.readlines()
        fh.close()
        excludenames = ['VOID', 'FLAG', 'defined'] # 可能错误识别成函数的标示
        curfile = ''
        curline = ''
        curfunc = ''
        curfunc_startline = -1
        self._funcs = []
        lastfile = ''
        startidx = -1
        pat_static = re.compile(r'\bstatic\b',re.I)
        pat_space = re.compile(r'\s+')
        linemax = len(lines)
        for idx,line in enumerate(lines):
            line = line.rstrip()
            ret0 = self.PAT_FILE.search(line)
            ret1 = self.PAT_LINE.search(line)
            ret2 = self.PAT_FUNCSTART.search(line)
            ret3 = self.PAT_FUNCSTOP.search(line)
            ret4 = self.PAT_FUNCCALL.search(line)
            ret5 = self.PAT_IF.search(line)
            ret6 = self.PAT_FOR.search(line)
            ret7 = self.PAT_WHILE.search(line)
            if ret0:
                curfile = ret0.group('filename')
                self._log.log(5, 'Match filename[{}] at line [{}]'.format(curfile,idx+1))
            elif ret1:
                curline = ret1.group('lineno')
                #self._log.log(5, 'Match lineno[{}] at line [{}]'.format(curline,idx+1))
                if ret5:
                    if curfunc:
                        count_if += 1
                elif ret6:
                    if curfunc:
                        count_for += 1
                elif ret7:
                    if curfunc:
                        count_while += 1
            elif ret2:
                if ret2.group('funcname') not in excludenames:
                    curfunc = ret2.group('funcname')
                    callfuncs = []
                    count_if = 0
                    count_for = 0
                    count_while = 0
                    self._log.log(5, 'Match function[{}] start at line [{}]'.format(curfunc,idx+1))
                    # parse function prototype
                    funcproto = ''
                    # function return type
                    subidx = idx - 1
                    while subidx >= 0:
                        subline = lines[subidx].rstrip()
                        subret1 = self.PAT_LINE.search(subline)
                        if not subret1:
                            testpart = subline.strip()
                        else:
                            curfunc_startline = subret1.group('lineno')
                            testpart = subret1.group('extra').strip()
                        if '}' in testpart:
                            funcproto = testpart[testpart.find('}')+1:] + ' ' + funcproto
                            break
                        if testpart != '':
                            funcproto = testpart + ' ' + funcproto
                        if subret1 and funcproto != '':
                            break
                        subidx = subidx - 1
                    if pat_static.search(funcproto):
                        static_func = True
                    else:
                        static_func = False
                    funcproto = funcproto + curfunc
                    # function params
                    bpair = [0, 0, 0]
                    subidx = idx + 1
                    while subidx < linemax:
                        subline = lines[subidx].rstrip()
                        subret1 = self.PAT_LINE.search(subline)
                        if not subret1:
                            testpart = subline.strip()
                        else:
                            testpart = subret1.group('extra').strip()
                        if testpart != '':
                            funcproto += ' '
                            for ch in testpart:
                                funcproto += ch
                                if ch == '{':
                                    bpair[0] += 1
                                elif ch == '}':
                                    bpair[0] -= 1
                                elif ch == '[':
                                    bpair[1] += 1
                                elif ch == ']':
                                    bpair[1] -= 1
                                elif ch == '(':
                                    bpair[2] += 1
                                elif ch == ')':
                                    bpair[2] -= 1
                                    if sum(bpair) == 0:
                                        break
                            if sum(bpair) == 0:
                                break
                            if len(funcproto) > 400:
                                # 函数宣言分多行时，cscope解析结果会漏掉结束的“)”，导致无限循环
                                break
                        subidx += 1
                    if sum(bpair) == 0:
                        funcproto = pat_space.sub(' ', funcproto)
                    else:
                        funcproto = ''
            elif ret3:
                if curfunc:
                    if curfile != lastfile:
                        if lastfile and self._cbfunc:
                            self._worker.addJob((startidx, len(self._funcs)))
                        lastfile = curfile
                        startidx = len(self._funcs)
                    self._funcs.append(self.FuncInfo(name=curfunc, relpath=curfile,
                                                     startline=curfunc_startline, stopline=curline,
                                                     calls=callfuncs, countif=count_if, countfor=count_for,
                                                     countwhile=count_while, static=static_func, prototype=funcproto,extra={}))
                    curfunc = ''
                    curfunc_startline = -1
                    self._log.log(5, 'Match function stop at line [{}]'.format(idx+1))
            elif ret4:
                if curfunc and (ret4.group('funcname') not in excludenames):
                    callfuncs.append(ret4.group('funcname'))
                    self._log.log(5, 'Match funccall[{}] at line [{}]'.format(ret4.group('funcname'), idx+1))
        if self._cbfunc:
            self._worker.addJob((startidx, len(self._funcs)))
    def _readSource(self, param):
        startidx, stopidx = param[0:2]
        curfile = self._funcs[startidx].relpath
        fullpath = os.path.join(self._root, curfile)
        fh = openTextFile(fullpath, 'r')
        lines = fh.readlines()
        fh.close()
        startline = 0
        self._log.log(5, 'Open source file[{}]'.format(curfile))
        for idx in range(startidx, stopidx):
            item = self._funcs[idx]
            # 从上一个函数的结束到当前函数的开始范围内，查找机能名和函数ID
            curline = int(item.startline) - 1
            stopline = int(item.stopline) - 1
            self._log.log(5, 'Check function[{}] in the range {}-{}-{}'.format(item.name, startline+1, curline+1, stopline+1))
            item.extra.update(self._cbfunc(fullpath, lines, item.name, startline, curline, stopline))
            startline = stopline
    def _readCache(self):
        fh = open(os.path.join(self._root, 'cscope.cache'), 'rb')
        self._funcs = [self.FuncInfo(**x) for x in pickle.load(fh)]
        fh.close()
    def _writeCache(self):
        fh = open(os.path.join(self._root, 'cscope.cache'), 'wb')
        pickle.dump([x._asdict() for x in self._funcs], fh)
        fh.close()

class CtagsParser(object):
    TagInfo = collections.namedtuple('TagInfo', ['token', 'path', 'line', 'cate', 'extra', 'scope','info'])
    #PAT_RECORD = re.compile(r'^(?P<token>\S+?)\t(?P<path>[^\t]+)\t(?P<line>(?:\d+|.+?));"\t(?P<cate>.)(\t(?P<extra>.+))?$')
    PAT_RECORD = re.compile(r'^(?P<token>\S+?)\t(?P<path>[^\t]+)\t(?P<line>\d+);"\t(?P<cate>.)(\t(?P<extra>.+))?$')
    PAT_TYPEDEF = re.compile(r'\btypedef\b')
    PAT_COMMENT1 = re.compile(r'//.*')
    PAT_COMMENT2 = re.compile(r'/\*(.|\n)+?\*/')
    PAT_EMPTYLINE = re.compile(r'^\s*$')
    PAT_SRC_MACRO = re.compile('^\s*#\s*define\s+(?P<name>\S+)\s+(?P<value>\S.*?)(\s*/\*\s*(?P<cmt>\S.*?)\s*\*/\s*)?$')
    def __init__(self, tagfile, encoding=None):
        # 初始化log
        self._log = LogUtil().logger(LOGNAME2)
        # tags文件的生成方法：ctags -R
        fullpath = os.path.normpath(os.path.abspath(tagfile))
        self._root, self._tag = os.path.split(fullpath)
        # 设置文件编码列表
        self._testcodes = ['cp932','cp936']
        if encoding and (encoding not in self._testcodes):
            self._testcodes.insert(0, encoding)
        self._log.log(20, 'New object[{},{}]'.format(self._root, self._tag))
        if hasattr(sys,'frozen'):
            selffile = sys.executable
        else:
            selffile = __file__
        if not os.path.isfile(fullpath):
            # 自动生成tags
            curdir = os.path.abspath('.')
            os.chdir(self._root)
            if os.name == 'nt':
                self._log.log(10, "Generating tag file in WinNT")
                exename = os.path.join(scriptPath(), 'bin', 'ctags.exe')
            else:
                self._log.log(10, "Generating tag file in Unix")
                exename = 'ctags'
            params = [exename, '-R', '--sort=no', '--excmd=number']
            mp = MultiProcess()
            mp_ret = mp.call(params)
            os.chdir(curdir)
            if mp_ret:
                self._log.log(50, "Error in generating tag file")
                self._info = []
                return
        if cacheCheck(os.path.join(self._root,'tags.cache'), selffile, fullpath):
            self._log.log(10, 'Read Cache')
            self._readCache()   # 从cache文件读入分析结果
        else:
            self._worker = MultiThread(3)
            self._worker.register(self._readSource)
            self._worker.start()
            self._info = []
            self._parse()       # 分析tags文件，同时把要解析的源代码文件加入到队列中
            self._worker.join()
            self._writeCache()  # 将分析结果写入cache文件
            self._log.log(10, 'Write Cache')
    def outputMacro(self, outfile, fields):
        outdata = [['#Macro']]
        for item in fields:
            if item == 'Path':
                outdata[-1].append('Path')
            elif item == 'Line':
                outdata[-1].append('Line')
            elif item == 'Scope':
                outdata[-1].append('Scope')
            elif item == 'Value':
                outdata[-1].append('Value')
            elif item == 'Comment':
                outdata[-1].append('Comment')
        for tok in self._info:
            if tok.cate == 'd':
                outdata.append([tok.token])
                for item in fields:
                    if item == 'Path':
                        outdata[-1].append(tok.path)
                    elif item == 'Line':
                        outdata[-1].append(tok.line)
                    elif item == 'Scope':
                        if tok.scope:
                            outdata[-1].append('Global')
                        else:
                            outdata[-1].append('Local')
                    elif item == 'Value':
                        outdata[-1].append(tok.info.get('value',''))
                    elif item == 'Comment':
                        outdata[-1].append(tok.info.get('comment',''))
        if outfile:
            fh = open(outfile, 'w', encoding='utf-8')
            for idx,item in enumerate(outdata):
                if idx == 0:
                    colidx = '#No'
                else:
                    colidx = idx
                fh.write('{}\t{}\n'.format(colidx, '\t'.join([str(x) for x in item])))
            fh.close()
        return outdata
    def outputVar(self, outfile, fields):
        outdata = [['#Var']]
        for item in fields:
            if item == 'Path':
                outdata[-1].append('Path')
            elif item == 'Line':
                outdata[-1].append('Line')
            elif item == 'Scope':
                outdata[-1].append('Scope')
            elif item == 'Type':
                outdata[-1].append('Type')
            elif item == 'Comment':
                outdata[-1].append('Comment')
        for tok in self._info:
            if tok.cate == 'v':
                outdata.append([tok.token])
                for item in fields:
                    if item == 'Path':
                        outdata[-1].append(tok.path)
                    elif item == 'Line':
                        outdata[-1].append(tok.line)
                    elif item == 'Scope':
                        if tok.scope:
                            outdata[-1].append('Global')
                        else:
                            outdata[-1].append('Local')
                    elif item == 'Type':
                        outdata[-1].append(tok.info.get('type',''))
                    elif item == 'Comment':
                        outdata[-1].append(tok.info.get('comment',''))
        if outfile:
            fh = open(outfile, 'w', encoding='utf-8')
            for idx,item in enumerate(outdata):
                if idx == 0:
                    colidx = '#No'
                else:
                    colidx = idx
                fh.write('{}\t{}\n'.format(colidx, '\t'.join([str(x) for x in item])))
            fh.close()
        return outdata
    def outputType(self, outfile1, fields1, outfile2, fields2, outfile3, fields3):
        outdata1 = [['#Struct']]
        for item in fields1:
            if item == 'Path':
                outdata1[-1].append('Path')
            elif item == 'Line':
                outdata1[-1].append('Line')
            elif item == 'Scope':
                outdata1[-1].append('Scope')
            elif item == 'Comment':
                outdata1[-1].append('Comment')
        outdata2 = [['#Member']]
        for item in fields2:
            if item == 'Path':
                outdata2[-1].append('Path')
            elif item == 'Line':
                outdata2[-1].append('Line')
            elif item == 'Scope':
                outdata2[-1].append('Scope')
            elif item == 'Comment':
                outdata2[-1].append('Comment')
            elif item == 'Parent':
                outdata2[-1].append('Parent')
            elif item == 'Type':
                outdata2[-1].append('Type')
        outdata3 = [['#Struct']]
        for item in fields3:
            if item == 'Path':
                outdata3[-1].append('Path')
            elif item == 'Line':
                outdata3[-1].append('Line')
            elif item == 'Scope':
                outdata3[-1].append('Scope')
            elif item == 'Comment':
                outdata3[-1].append('Comment')
            elif item == 'Category':
                outdata3[-1].append('Category')
            elif item == 'Type':
                outdata3[-1].append('Type')
        for tok in self._info:
            if tok.cate in ('s','g'):
                outdata1.append([tok.token])
                for item in fields1:
                    if item == 'Path':
                        outdata1[-1].append(tok.path)
                    elif item == 'Line':
                        outdata1[-1].append(tok.line)
                    elif item == 'Scope':
                        if tok.scope:
                            outdata1[-1].append('Global')
                        else:
                            outdata1[-1].append('Local')
                    elif item == 'Comment':
                        outdata1[-1].append(tok.info.get('comment',''))
            elif tok.cate in ('m', 'e'):
                outdata2.append([tok.token])
                for item in fields2:
                    if item == 'Path':
                        outdata2[-1].append(tok.path)
                    elif item == 'Line':
                        outdata2[-1].append(tok.line)
                    elif item == 'Scope':
                        if tok.scope:
                            outdata2[-1].append('Global')
                        else:
                            outdata2[-1].append('Local')
                    elif item == 'Comment':
                        outdata2[-1].append(tok.info.get('comment',''))
                    elif item == 'Parent':
                        outdata2[-1].append(tok.extra)
                    elif item == 'Type':
                        outdata2[-1].append(tok.info.get('type',''))
            elif tok.cate == 't':
                outdata3.append([tok.token])
                for item in fields3:
                    parts = tok.extra.split(':',2)
                    if item == 'Path':
                        outdata3[-1].append(tok.path)
                    elif item == 'Line':
                        outdata3[-1].append(tok.line)
                    elif item == 'Scope':
                        if tok.scope:
                            outdata3[-1].append('Global')
                        else:
                            outdata3[-1].append('Local')
                    elif item == 'Comment':
                        outdata3[-1].append(tok.info.get('comment',''))
                    elif item == 'Category':
                        if len(parts) > 2:
                            outdata3[-1].append(parts[1])
                        else:
                            outdata3[-1].append(tok.extra)
                    elif item == 'Type':
                        if len(parts) > 2:
                            outdata3[-1].append(parts[2])
                        else:
                            outdata3[-1].append(tok.extra)
        if outfile1:
            fh = open(outfile1, 'w', encoding='utf-8')
            for idx,item in enumerate(outdata1):
                if idx == 0:
                    colidx = '#No'
                else:
                    colidx = idx
                fh.write('{}\t{}\n'.format(colidx, '\t'.join([str(x) for x in item])))
            fh.close()
        if outfile2:
            fh = open(outfile2, 'w', encoding='utf-8')
            for idx,item in enumerate(outdata2):
                if idx == 0:
                    colidx = '#No'
                else:
                    colidx = idx
                fh.write('{}\t{}\n'.format(colidx, '\t'.join([str(x) for x in item])))
            fh.close()
        if outfile3:
            fh = open(outfile3, 'w', encoding='utf-8')
            for idx,item in enumerate(outdata3):
                if idx == 0:
                    colidx = '#No'
                else:
                    colidx = idx
                fh.write('{}\t{}\n'.format(colidx, '\t'.join([str(x) for x in item])))
            fh.close()
        return outdata1,outdata2,outdata3
    def _parse(self):
        fullpath = os.path.join(self._root, self._tag)
        encoding = guessEncode(fullpath, *self._testcodes)[0]
        fh = open(fullpath ,'r', encoding=encoding, errors='ignore')
        lastfile = ''
        startidx = 0
        for line in fh.readlines():
            line = line.rstrip()
            patret = self.PAT_RECORD.match(line)
            if patret:
                token = patret.group('token')
                path = patret.group('path')
                lineno = patret.group('line')
                #lineno = unescape(lineno, encoding)
                cate = patret.group('cate')
                extra = patret.group('extra')
                scope = True
                if extra:
                    parts = extra.split('\t')
                    if parts[-1] == 'file:':
                        scope = False
                        parts.pop()
                else:
                    parts = []
                if path != lastfile:
                    if lastfile != '':
                        self._worker.addJob((startidx, len(self._info)))
                    startidx = len(self._info)
                    lastfile = path
                # in case of len(parts) == 2: define nested struct
                if len(parts) > 0:
                    for partitem in parts:
                        if partitem.startswith('typedef:'):
                            self._info.append(self.TagInfo(token=token,
                                                           path=path,
                                                           line=lineno,
                                                           cate='t',
                                                           extra=partitem,
                                                           scope=scope,
                                                           info={}))
                        else:
                            self._info.append(self.TagInfo(token=token,
                                                           path=path,
                                                           line=lineno,
                                                           cate=cate,
                                                           extra=partitem,
                                                           scope=scope,
                                                           info={}))
                        self._log.log(15, self._info[-1])
                else:
                    self._info.append(self.TagInfo(token=token,
                                                   path=path,
                                                   line=lineno,
                                                   cate=cate,
                                                   extra='',
                                                   scope=scope,
                                                   info={}))
                    self._log.log(15, self._info[-1])
            else:
                self._log.log(5, 'Miss Match:{}'.format(line))
        if lastfile != '':
            self._worker.addJob((startidx, len(self._info)))
        fh.close()
    def _readSource(self, param):
        startidx, stopidx = param[0:2]
        curfile = self._info[startidx].path
        fullpath = os.path.join(self._root, curfile)
        fh = openTextFile(fullpath, 'r')
        lines = fh.readlines()
        fh.close()
        self._log.log(5, 'Open source file[{}]'.format(curfile))
        for idx in range(startidx, stopidx):
            item = self._info[idx]
            lineidx = int(item.line) - 1
            cate = item.cate
            if cate in ('s', 'g'):
                # find startpos/endpos of struct/enum definition
                lineidx1 = lineidx
                cmtfree = self.PAT_COMMENT2.sub(lambda matchobj: ' ' * len(matchobj.group(0)), lines[lineidx1])
                linecol1 = cmtfree.index(item.token)
                paren = [0] * 3
                flag = True
                lineidx2 = lineidx1
                linecol2 = linecol1
                while flag or any(paren):
                    while linecol2 < len(cmtfree):
                        if cmtfree[linecol2] == '{':
                            paren[0] += 1
                            if paren[0] == 1:
                                flag = False
                        elif cmtfree[linecol2] == '}':
                            paren[0] -= 1
                            if not any(paren):
                                break
                        elif cmtfree[linecol2] == '[':
                            paren[1] += 1
                        elif cmtfree[linecol2] == ']':
                            paren[1] -= 1
                        elif cmtfree[linecol2] == '(':
                            paren[2] += 1
                        elif cmtfree[linecol2] == ')':
                            paren[2] -= 1
                        linecol2 += 1
                    else:
                        lineidx2 += 1
                        linecol2 = 0
                        cmtfree = self.PAT_COMMENT2.sub(lambda matchobj: ' ' * len(matchobj.group(0)), lines[lineidx2])
                cmt1 = cmt2 = cmt3 = ''
                # comment before start of struct/enum
                patret = re.search(r'^\s*/\*+(.*?)\*+/\s*$', lines[lineidx1 - 1])
                if patret:
                    cmt1 = patret.group(1).strip().replace('\t', '~\\t~')
                else:
                    patret = re.search(r'^\s*//(.*)', lines[lineidx1 - 1])
                    if patret:
                        cmt1 = patret.group(1).strip().replace('\t', '~\\t~')
                # comment at the end of startline of struct/enum
                patret = self.PAT_COMMENT2.search(lines[lineidx1][linecol1:])
                if patret:
                    cmt2 = patret.group(0)[2:-2].strip().replace('\t', '~\\t~')
                else:
                    patret = self.PAT_COMMENT1.search(lines[lineidx1][linecol1:])
                    if patret:
                        cmt2 = patret.group(0)[2:].strip().replace('\t', '~\\t~')
                # comment at the end of endline of struct/enum
                patret = self.PAT_COMMENT2.search(lines[lineidx2][linecol2:])
                if patret:
                    cmt3 = patret.group(0)[2:-2].strip().replace('\t', '~\\t~')
                else:
                    patret = self.PAT_COMMENT1.search(lines[lineidx2][linecol2:])
                    if patret:
                        cmt3 = patret.group(0)[2:].strip().replace('\t', '~\\t~')
                item.info['comment'] = cmt2 or cmt3 or cmt1
            elif cate == 'm':
                # member of struct
                curline = lines[lineidx]
                cmtfree = self.PAT_COMMENT2.sub(lambda matchobj: ' ' * len(matchobj.group(0)), curline)
                varidx = cmtfree.index(item.token)
                vartype = re.sub(r'\bstatic\b', r'', cmtfree[:varidx]).strip()
                vartype = re.sub(r'\s+', ' ', vartype)
                varidx += len(item.token)
                patret = self.PAT_COMMENT2.search(curline[varidx:])
                if patret:
                    cmt = patret.group(0)[2:-2].strip().replace('\t', '~\\t~')
                else:
                    patret = self.PAT_COMMENT1.search(curline[varidx:])
                    if patret:
                        cmt = patret.group(0)[2:].strip().replace('\t', '~\\t~')
                    else:
                        cmt = ''
                        self._log.log(5, 'Member{} in file[{}] at line[{}] without a comment'.format(item.token, item.path, item.line))
                item.info['type'] = vartype
                item.info['comment'] = cmt
            elif cate == 'e':
                # member of enum
                curline = lines[lineidx]
                cmtfree = self.PAT_COMMENT2.sub(lambda matchobj: ' ' * len(matchobj.group(0)), curline)
                varidx = cmtfree.index(item.token)
                varidx += len(item.token)
                patret = self.PAT_COMMENT2.search(curline[varidx:])
                if patret:
                    cmt = patret.group(0)[2:-2].strip().replace('\t', '~\\t~')
                else:
                    patret = self.PAT_COMMENT1.search(curline[varidx:])
                    if patret:
                        cmt = patret.group(0)[2:].strip().replace('\t', '~\\t~')
                    else:
                        cmt = ''
                        self._log.log(5, 'Member{} in file[{}] at line[{}] without a comment'.format(item.token, item.path, item.line))
                item.info['type'] = '__ENUM'
                item.info['comment'] = cmt
            elif cate == 't':
                # find startpos/endpos of typedef
                lineidx2 = lineidx
                cmtfree = self.PAT_COMMENT2.sub(lambda matchobj: ' ' * len(matchobj.group(0)), lines[lineidx2])
                linecol2 = cmtfree.index(item.token)
                paren = [0] * 3
                flag = True
                lineidx1 = lineidx2
                linecol1 = linecol2
                while flag or any(paren):
                    while linecol1 >= 0:
                        if cmtfree[linecol1] == '{':
                            paren[0] += 1
                            if not any(paren):
                                break
                        elif cmtfree[linecol1] == '}':
                            paren[0] -= 1
                            if paren[0] == -1:
                                flag = False
                        elif cmtfree[linecol1] == '[':
                            paren[1] += 1
                        elif cmtfree[linecol1] == ']':
                            paren[1] -= 1
                        elif cmtfree[linecol1] == '(':
                            paren[2] += 1
                        elif cmtfree[linecol1] == ')':
                            paren[2] -= 1
                        elif flag and cmtfree[linecol1] == ';':
                            # type rename without definition
                            # e.g. typedef int INT;
                            flag = False
                            lineidx1 = -1
                            break
                        linecol1 -= 1
                    else:
                        lineidx1 -= 1
                        linecol1 = 0
                        if lineidx1 < 0:
                            break
                        cmtfree = self.PAT_COMMENT2.sub(lambda matchobj: ' ' * len(matchobj.group(0)), lines[lineidx1])
                cmt1 = cmt2 = cmt3 = ''
                if lineidx1 < 0:
                    pass
                else:
                    if linecol1 == 0:
                        newlineidx1 = lineidx1 - 1
                    else:
                        newlineidx1 = lineidx1
                    # comment before start of struct/enum
                    patret = re.search(r'^\s*/\*+(.*?)\*+/\s*$', lines[newlineidx1 - 1])
                    if patret:
                        cmt1 = patret.group(1).strip().replace('\t', '~\\t~')
                    else:
                        patret = re.search(r'^\s*//(.*)', lines[newlineidx1 - 1])
                        if patret:
                            cmt1 = patret.group(1).strip().replace('\t', '~\\t~')
                    # comment at the end of startline of struct/enum
                    patret = self.PAT_COMMENT2.search(lines[newlineidx1][linecol1:])
                    if patret:
                        cmt2 = patret.group(0)[2:-2].strip().replace('\t', '~\\t~')
                    else:
                        patret = self.PAT_COMMENT1.search(lines[newlineidx1][linecol1:])
                        if patret:
                            cmt2 = patret.group(0)[2:].strip().replace('\t', '~\\t~')
                    # comment at the end of endline of struct/enum
                    patret = self.PAT_COMMENT2.search(lines[lineidx2][linecol2:])
                    if patret:
                        cmt3 = patret.group(0)[2:-2].strip().replace('\t', '~\\t~')
                    else:
                        patret = self.PAT_COMMENT1.search(lines[lineidx2][linecol2:])
                        if patret:
                            cmt3 = patret.group(0)[2:].strip().replace('\t', '~\\t~')
                item.info['comment'] = cmt2 or cmt3 or cmt1
            elif cate == 'd':
                # define
                lineidx1 = lineidx
                curline = lines[lineidx1]
                while curline.endswith('\\\n'):
                    lineidx1 += 1
                    curline = curline[:-2] + lines[lineidx1]
                patret = self.PAT_SRC_MACRO.search(curline)
                value = ''
                cmt = ''
                if patret:
                    value = re.sub(r'\s+', ' ', patret.group('value'))
                    if patret.group('name') != item.token:
                        # error macro
                        self._log.log(5, 'Macro[{}] in file[{}] at line[{}] with error'.format(item.token, item.path, item.line))
                    if patret.group('cmt'):
                        cmt = patret.group('cmt').replace('\t', '~\\t~')
                else:
                    # error macro
                    self._log.log(5, 'Macro[{}] in file[{}] at line[{}] without value'.format(item.token, item.path, item.line))
                item.info['value'] = value
                item.info['comment'] = cmt
            elif cate == 'v':
                # global variable
                curline = lines[lineidx]
                cmtfree = self.PAT_COMMENT2.sub(lambda matchobj: ' ' * len(matchobj.group(0)), curline)
                varidx = cmtfree.index(item.token)
                vartype = re.sub(r'\bstatic\b', r'', cmtfree[:varidx]).strip()
                vartype = re.sub(r'\s+', ' ', vartype)
                varidx += len(item.token)
                patret = self.PAT_COMMENT2.search(curline[varidx:])
                if patret:
                    cmt = patret.group(0)[2:-2].strip().replace('\t', '~\\t~')
                else:
                    patret = self.PAT_COMMENT1.search(curline[varidx:])
                    if patret:
                        cmt = patret.group(0)[2:].strip().replace('\t', '~\\t~')
                    else:
                        cmt = ''
                        self._log.log(5, 'Variable{} in file[{}] at line[{}] without a comment'.format(item.token, item.path, item.line))
                item.info['type'] = vartype
                item.info['comment'] = cmt
    def _readCache(self):
        fh = open(os.path.join(self._root, 'tags.cache'), 'rb')
        self._info = [self.TagInfo(**x) for x in pickle.load(fh)]
        fh.close()
    def _writeCache(self):
        fh = open(os.path.join(self._root, 'tags.cache'), 'wb')
        pickle.dump([x._asdict() for x in self._info], fh)
        fh.close()

class FormatSource(object):
    # 格式化代码
    # 制限：
    #   预编译语句不能出现在一行代码中间（如:根据预编译选项改变if的一个条件）
    #   字符串不能跨行，字符串中不能出现;{}[]()空白符号
    PAT_CMT1 = re.compile(r'//.*')
    PAT_CMT2 = re.compile(r'/\*(.|\n)*?\*/')
    PAT_SPACE = re.compile(r'[ \t]+')
    PAT_PRECOMPILE = re.compile(r'^#\s*(if|el|endif|define)')
    PAT_MULTILINE = re.compile(r'\\\n')
    PAT_OPENBRACE = re.compile(r'(;|\)|\belse|\bdo)\s*{$')
    def __init__(self):
        self._log = LogUtil().logger(LOGNAME3)
    def clean(self, txt):
        self._log.log(10, 'Input:[{}]'.format(txt))
        # 删除注释
        newtxt = self.PAT_CMT1.sub('', txt)
        newtxt = self.PAT_CMT2.sub('', newtxt)
        # 删除空行
        lines = []
        for line in newtxt.splitlines():
            line=line.strip()
            if line != '':
                lines.append(line)
        newtxt = '\n'.join(lines)
        # 合并手动跨行 "\"
        newtxt = self.PAT_MULTILINE.sub(' ', newtxt)
        # 插入/删除必要空白
        ## ++ -- 两侧去空白
        newtxt = re.sub(r'\s*(\+\+|--)\s*',r'\1',newtxt)
        ## [] 两侧去空白
        newtxt = re.sub(r'\s*\[\s*','[',newtxt)
        newtxt = re.sub(r'\s*\]\s*',']',newtxt)
        ## ( 左侧去空白，右侧加空白，if/for/while后加空白
        newtxt = re.sub(r'\s*\(\s*',r'( ',newtxt)
        newtxt = re.sub(r'\b(if|for|while|return)\(',r'\1 (', newtxt)
        ## ) 左侧加空白，右侧去空白
        newtxt = re.sub(r'\s*\)\s*',r' )',newtxt)
        ## {} 两侧加入空白
        newtxt = re.sub(r'\s*\{\s*',r' { ',newtxt)
        newtxt = re.sub(r'\s*\}\s*',r' } ',newtxt)
        ## = == <= <<= >= >>= < << > >> != &= &&= |= ||= & && | || 两侧加空白
        newtxt = re.sub(r'\s*(=+|<+=|>+=|>+|<+|!=|&+=|\|+=|&+|\|+)\s*',r' \1 ',newtxt)
        ## += -= *= /= ^= 两侧加空白
        newtxt = re.sub(r'\s*(\+=|-=|\*=|/=|^=)\s*',r' \1 ',newtxt)
        ## + - 两侧加空白
        newtxt = re.sub(r'\s*(?<!\+)\+(?!=|\+)\s*',' + ', newtxt)
        newtxt = re.sub(r'\s*(?<!-)-(?!=|-)\s*',' - ', newtxt)
        ## * / ^ 两侧加空白
        newtxt = re.sub(r'\s*(\*|/|^)(?!=)\s*',r' \1 ',newtxt)
        ## , 左侧去空白，右侧加空白
        newtxt = re.sub(r'\s*,\s*',r', ',newtxt)
        ## ; 左侧去空白，右侧加空白
        newtxt = re.sub(r'\s*;\s*',r'; ',newtxt)
        # 删除连续的空白
        newtxt = self.PAT_SPACE.sub(' ', newtxt)
        # 根据预编译行将代码分区
        lines = ''
        info = {'level1':0,'level2':0,'level3':0}
        fmttxt = ''
        for line in newtxt.splitlines():
            if self.PAT_PRECOMPILE.search(line):
                fmttxt += self._reformat(lines, info)
                fmttxt += ('\t' * info['level1']) + line
                lines = ''
            else:
                lines += line + ' '
        fmttxt += self._reformat(lines, info)
        # 删除空行
        lines = []
        for line in fmttxt.splitlines():
            line=line.rstrip()
            if line != '':
                lines.append(line)
        newtxt = '\n'.join(lines)
        self._log.log(10, 'Output:[{}]'.format(newtxt))
        return newtxt
    def _reformat(self, txt, info):
        # 格式化代码
        # 限制条件：传入的代码(txt)必须是全部由完整语句组成
        self._log.log(10, 'Input:[{}]'.format(txt))
        outtxt = ''
        lastidx = 0
        i = 0
        txtlen = len(txt)
        while i < txtlen:
            if txt[i] == ';':
                if info['level2'] == 0 and info['level3'] == 0:
                    # 语句结束符号
                    curline = txt[lastidx:(i+1)].strip()
                    outtxt += '\t' * info['level1'] + curline + '\n'
                    lastidx = i + 1
            elif txt[i] == '{':
                info['level1'] += 1
                if info['level2'] == 0 and info['level3'] == 0:
                    if self.PAT_OPENBRACE.search(txt[lastidx:(i+1)]):
                        # Block开始符号
                        curline = txt[lastidx:(i+1)].strip()
                        outtxt += '\t' * (info['level1']-1) + curline + '\n'
                        lastidx = i + 1
                    else:
                        # 变量初期化
                        j = i + 1
                        oldinfo = dict(info)
                        oldinfo['level1'] -= 1
                        # 查找语句结束符号";"
                        while j < txtlen and txt[j]!=';':
                            if txt[j] == '{':
                                info['level1'] += 1
                            elif txt[j] == '}':
                                info['level1'] -= 1
                            elif txt[j] == '[':
                                info['level2'] += 1
                            elif txt[j] == ']':
                                info['level2'] -= 1
                            elif txt[j] == '(':
                                info['level3'] += 1
                            elif txt[j] == ')':
                                info['level3'] -= 1
                            j += 1
                        curline = txt[lastidx:(j+1)].strip()
                        outtxt += '\t' * info['level1'] + curline + '\n'
                        lastidx = j + 1
                        i = j
                        for lvlkey in ('level1', 'level2', 'level3'):
                            if info[lvlkey] != oldinfo[lvlkey]:
                                self._log.log(10, 'exception in variable initialization')
                                break
            elif txt[i] == '}':
                info['level1'] -= 1
                if info['level2'] == 0 and info['level3'] == 0:
                    # Block结束符号
                    curline = txt[lastidx:(i+1)].strip()
                    outtxt += '\t' * info['level1'] + curline + '\n'
                    lastidx = i + 1
            elif txt[i] == '[':
                info['level2'] += 1
            elif txt[i] == ']':
                info['level2'] -= 1
            elif txt[i] == '(':
                info['level3'] += 1
            elif txt[i] == ')':
                info['level3'] -= 1
            else:
                pass
            i += 1
        # txt[lastidx-1] 是一个完整语句的结束（;/{/}），txt[lastidx:]后面是无效内容
        self._log.log(10, 'Dropped:[{}]'.format(txt[lastidx:]))
        self._log.log(10, 'Output:[{}]'.format(outtxt))
        return outtxt

def cscopeSourceParserEPS(filename, lines, funcname, lastendline, startline, endline):
    logger = LogUtil().logger(LOGNAME)
    PAT_JPNAME = re.compile(r'^\s+機能名\s*(:|：)\s*(?P<jpname>\S.*?)\s*$')
    PAT_FUNCNO = re.compile(r'^\s+関数番号\s*(:|：)\s*(?P<funcno>\S+)')
    PAT_COMMENT1 = re.compile(r'//.*')
    PAT_COMMENT2 = re.compile(r'/\*(.|\n)+?\*/')
    PAT_EMPTYLINE = re.compile(r'^\s*$')
    # extract function name in words, function id
    curline = startline
    info = {}
    flag1 = False
    flag2 = False
    while curline > lastendline:
        ret1 = PAT_JPNAME.search(lines[curline])
        ret2 = PAT_FUNCNO.search(lines[curline])
        if ret1:
            if flag1:
                break
            else:
                info['FunctionName'] = ret1.group('jpname').replace('\t','~\\t~')
                flag1 = True
                logger.log(5, 'Found JPName at line[{}]'.format(curline+1))
        if ret2:
            if flag2:
                break
            else:
                info['FunctionID'] = ret2.group('funcno')
                flag2 = True
                logger.log(5, 'Found FuncNo at line[{}]'.format(curline+1))
        if flag1 and flag2:
            break
        curline -= 1
    # extract source count
    tempcode = ''.join(lines[startline:endline+1])
    tempcode = PAT_COMMENT1.sub('',tempcode)
    tempcode = PAT_COMMENT2.sub('',tempcode)
    linecount = 0
    for templine in tempcode.splitlines():
        if not PAT_EMPTYLINE.search(templine):
            linecount += 1
    info['SourceCount']=linecount
    # locate function header(comment) startline
    if lastendline > 0:
        # 2nd~nth function in the file
        curline = lastendline + 1
        while PAT_EMPTYLINE.search(lines[curline]):
            curline += 1
    else:
        # 1st function in the file
        curline = startline - 1
        # skip empty lines between header section/inline section and code section
        while curline>=0 and PAT_EMPTYLINE.search(lines[curline]):
            curline -= 1
        # check first non-empty line before the function
        testline = curline
        while testline>=0 and (not PAT_EMPTYLINE.search(lines[testline])):
            testline -= 1
        tempcode = ''.join(lines[:curline+1])
        # check first comment before the function
        for tempret in PAT_COMMENT2.finditer(tempcode):
            testline1 = tempcode[:tempret.start(0)].count('\n')
            testline2 = tempcode[:tempret.end(0)].count('\n')
        if testline1 < testline < testline2:
            curline = testline1
        else:
            curline = testline
    info['HeaderLine'] = str(curline + 1)
    # inline check
    lastendline = int(info['HeaderLine']) - 1
    tempcode = ''.join(lines[lastendline:startline+1])
    tempcode = PAT_COMMENT1.sub('',tempcode)
    tempcode = PAT_COMMENT2.sub('',tempcode)
    PAT_INLINE = re.compile(r'\binline\b|\b_inline_\b|\b__inline__\b')
    if PAT_INLINE.search(tempcode):
        info['Inline'] = 1
    else:
        info['Inline'] = 0
    return info

