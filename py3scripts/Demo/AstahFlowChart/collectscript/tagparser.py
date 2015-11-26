# -*- coding:utf-8 -*-
# VERSION: 0.1
import re
import sys
import os
import collections
import pickle
import threading
import queue
from .logutil import LogUtil, registerLogger
from .guess import openTextFile
from .multithread import MultiThread

LOGNAME = 'TagParser'
LOGNAME2 = 'FormatSource'
registerLogger(LOGNAME)
registerLogger(LOGNAME2)

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
    PAT_JPNAME = re.compile(r'^\s+機能名\s*(:|：)\s*(?P<jpname>\S.*?)\s*$')
    PAT_FUNCNO = re.compile(r'^\s+関数番号\s*(:|：)\s*(?P<funcno>\S+)')
    PAT_IF = re.compile(r'(?<!#)\bif\b')
    PAT_FOR = re.compile(r'\bfor\b')
    PAT_WHILE = re.compile(r'\bwhile\b')
    PAT_COMMENT1 = re.compile(r'//.*')
    PAT_COMMENT2 = re.compile(r'/\*(.|\n)+?\*/')
    PAT_EMPTYLINE = re.compile(r'^\s*$')
    WORK_COUNT = 3
    # 函数情报类型 extra是从代码中读出的注释情报，其他的数据是从cscope.out中取得
    FuncInfo = collections.namedtuple('FuncInfo',['name','relpath','startline','stopline','calls','countif','countfor','countwhile','extra'])
    def __init__(self, cscopeout, encoding=None):
        # 初始化log
        self._log = LogUtil().logger(LOGNAME)
        # cscope.out文件的生成方法：cscope -Rbcu
        fullpath = os.path.normpath(os.path.abspath(cscopeout))
        self._root, self._cscope = os.path.split(fullpath)
        # 设置文件编码列表
        self._testcodes = ['cp932','cp936']
        if encoding and (encoding not in self._testcodes):
            self._testcodes.insert(0, encoding)
        self._log.log(20, 'New object[{},{}]'.format(self._root, self._cscope))
        if hasattr(sys,'frozen'):
            selffile = sys.executable
        else:
            selffile = __file__
        if cacheCheck(os.path.join(self._root,'cscope.cache'), selffile, fullpath):
            self._log.log(10, 'Read Cache')
            self._readCache()   # 从cache文件读入分析结果
        else:
            self._worker = MultiThread(3)
            self._worker.register(self._readSource)
            self._worker.start()
            self._parse()       # 分析cscope.out文件，同时把要解析的源代码文件加入到队列中
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
        # 输出函数列表
        self._log.log(10, "[{}][{}]".format(outfile, ','.join(fields)))
        fh=open(outfile,'w',encoding='utf-8')
        fh.write("#Function")
        for field in fields:
            if field == 'Path':
                fh.write('\tPath')
            elif field == 'StartLine':
                fh.write('\tStartLine')
            elif field == 'StopLine':
                fh.write('\tStopLine')
            elif field == 'SubCount':
                fh.write('\tSubFunctionCallCount')
            elif field == 'SubName':
                fh.write('\tSubFunctionName')
            elif field == 'FunctionID':
                fh.write('\tFunctionID')
            elif field == 'FunctionName':
                fh.write('\tFunctionName')
            elif field == 'Condition':
                fh.write('\tConditionCount')
            elif field == 'Loop':
                fh.write('\tLoopCount')
            elif field == 'Lines':
                fh.write('\tLines')
        fh.write('\n')
        if not funclist:
            funclist = self._funcs
        for item in funclist:
            fh.write(item.name)
            self._log.log(10, item.name)
            for field in fields:
                if field == 'Path':
                    fh.write('\t{}'.format(item.relpath))
                elif field == 'StartLine':
                    fh.write('\t{}'.format(item.startline))
                elif field == 'StopLine':
                    fh.write('\t{}'.format(item.stopline))
                elif field == 'SubCount':
                    fh.write('\t{}'.format(len(item.calls)))
                elif field == 'SubName':
                    fh.write('\t{}'.format(','.join(self.getFuncCall_asdict(item).keys())))
                elif field == 'FunctionID':
                    fh.write('\t{}'.format(item.extra.get('funcno','')))
                elif field == 'FunctionName':
                    fh.write('\t{}'.format(item.extra.get('jpname','')))
                elif field == 'Condition':
                    fh.write('\t{}'.format(item.countif))
                elif field == 'Loop':
                    fh.write('\t{}'.format(item.countfor + item.countwhile))
                elif field == 'Lines':
                    fh.write('\t{}'.format(item.extra.get('lines',0)))
            fh.write('\n')
        fh.close()
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
                    curfunc_startline = curline
                    count_if = 0
                    count_for = 0
                    count_while = 0
                    self._log.log(5, 'Match function[{}] start at line [{}]'.format(curfunc,idx+1))
            elif ret3:
                if curfunc:
                    if curfile != lastfile:
                        if lastfile:
                            self._worker.addJob((startidx, len(self._funcs)))
                        lastfile = curfile
                        startidx = len(self._funcs)
                    self._funcs.append(self.FuncInfo(name=curfunc, relpath=curfile,
                                                     startline=curfunc_startline, stopline=curline,
                                                     calls=callfuncs, countif=count_if, countfor=count_for,
                                                     countwhile=count_while, extra={}))
                    curfunc = ''
                    curfunc_startline = -1
                    self._log.log(5, 'Match function stop at line [{}]'.format(idx+1))
            elif ret4:
                if curfunc and (ret4.group('funcname') not in excludenames):
                    callfuncs.append(ret4.group('funcname'))
                    self._log.log(5, 'Match funccall[{}] at line [{}]'.format(ret4.group('funcname'), idx+1))
        self._worker.addJob((startidx, len(self._funcs)))
    def _readSource(self, param):
        startidx, stopidx = param[0:2]
        curfile = self._funcs[startidx].relpath
        fullpath = os.path.join(self._root, curfile)
        fh = openTextFile(self._testcodes, fullpath, 'r')
        lines = fh.readlines()
        fh.close()
        startline = 0
        self._log.log(5, 'Open source file[{}]'.format(curfile))
        for idx in range(startidx, stopidx):
            item = self._funcs[idx]
            # 从上一个函数的结束到当前函数的开始范围内，查找机能名和函数ID
            curline = int(item.startline) - 1
            flag1 = False
            flag2 = False
            self._log.log(5, 'Check function[{}] in the range {}-{}'.format(item.name, startline+1, curline+1))
            while curline > startline:
                ret1 = self.PAT_JPNAME.search(lines[curline])
                ret2 = self.PAT_FUNCNO.search(lines[curline])
                if ret1:
                    if flag1:
                        break
                    else:
                        item.extra['jpname'] = ret1.group('jpname')
                        flag1 = True
                        self._log.log(5, 'Found JPName at line[{}]'.format(curline+1))
                if ret2:
                    if flag2:
                        break
                    else:
                        item.extra['funcno'] = ret2.group('funcno')
                        flag2 = True
                        self._log.log(5, 'Found FuncNo at line[{}]'.format(curline+1))
                if flag1 and flag2:
                    break
                curline -= 1
            startline = int(item.stopline) - 1
            tempcode = ''.join(lines[int(item.startline)-1:int(item.stopline)])
            tempcode = self.PAT_COMMENT1.sub('',tempcode)
            tempcode = self.PAT_COMMENT2.sub('',tempcode)
            linecount = 0
            for templine in tempcode.splitlines():
                if not self.PAT_EMPTYLINE.search(templine):
                    linecount += 1
            item.extra['lines']=linecount
    def _readCache(self):
        fh = open(os.path.join(self._root, 'cscope.cache'), 'rb')
        self._funcs = [self.FuncInfo(**x) for x in pickle.load(fh)]
        fh.close()
    def _writeCache(self):
        fh = open(os.path.join(self._root, 'cscope.cache'), 'wb')
        pickle.dump([x._asdict() for x in self._funcs], fh)
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
        self._log = LogUtil().logger(LOGNAME2)
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

if __name__ == '__main__':
    cp = CscopeParser('cscope.out')
    # 例子：查找指定函数所调用的所有函数
    info = cp.getFuncInfo('Input_FSP1_IF', 'API_Renewal_InfoFail')
    fh = open('out.txt','w',encoding='utf-8')
    for item in info:
        # 输出指定的函数
        fh.write(item.name+'\t'+item.extra.get('funcno','')+'\t'+item.extra.get('jpname','')+'\n')
        info2 = cp.getFuncInfo(*item.calls)
        for func in CscopeParser.getFuncCall_asdict(item).keys():
            fh.write(func)
            for item2 in info2:
                if item2.name == func:
                    fh.write('\t'+item2.extra.get('jpname',''))
                    break
            fh.write('\n')
        fh.write('\n')
    fh.close()
    # 例子：输出函数列表
    cp.outputFuncInfo('out.txt')
