# -*- coding:utf-8 -*-
# VERSION: 0.1
import re
import sys
import os
import collections
import pickle
import threading
import queue
from .logutil import LogUtil
from .guess import openTextFile
from .multithread import MultiThread

LOGNAME = 'TagParser'

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
    PAT_LINE = re.compile(r'^(?P<lineno>\d+)\s+(?P<extra>.*)$')
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
    def outputFuncInfo(self, outfile, fields):
        # 输出函数列表
        self._log.log(10, outfile)
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
        self._log.log(10, 'Head')
        for item in self._funcs:
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
        self._funcs = [self.FuncInfo(*x) for x in pickle.load(fh)]
        fh.close()
    def _writeCache(self):
        fh = open(os.path.join(self._root, 'cscope.cache'), 'wb')
        pickle.dump([x._asdict() for x in self._funcs], fh)
        fh.close()

if __name__ == '__main__':
    # 生成log输出配置文件
    #logutil.newConf(('CscopeParser', 'EncodeChanger'))
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
