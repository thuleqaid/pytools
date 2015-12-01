# -*- coding:utf-8 -*-
import os
from .logutil import LogUtil, registerLogger
from .tagparser import CscopeParser
from .ctokens import CTokens
from .guess import guessEncode

LOGNAME = "CTest"
registerLogger(LOGNAME)

class CTest(object):
    def __init__(self, tagpath):
        self._log = LogUtil().logger(LOGNAME)
        self.rootpath = tagpath
        self.parser = CscopeParser(os.path.join(tagpath,'cscope.out'))
        self.token  = CTokens()
    def inject(self, funclist):
        # funclist: [{'function':function-name,'dummy':[(org-function-name, dmy-function-name),...]},...]
        injectinfo = {} # key:relpath
                        # value:{function-name:[FunctionInfo, renamelist]}
        appendfunclist = []
        # 根据输入参数，整理代码注入信息
        for funcitem in funclist:
            infolist = self.parser.getFuncInfo(funcitem['function'])
            if len(infolist) > 0:
                for funcinfo in infolist:
                    subfuncs = list(self.parser.getFuncCall_asdict(funcinfo).keys())
                    renamelist = []
                    for dmy in funcitem['dummy']:
                        if dmy[0] in subfuncs:
                            renamelist.append(tuple(dmy))
                            subfuncs.remove(dmy[0])
                        else:
                            pass
                    injectinfo.setdefault(funcinfo.relpath, {})
                    injectinfo[funcinfo.relpath][funcinfo.name] = [funcinfo, tuple(renamelist)]
                    # 没有dummy化的子函数，也要进行代码注入
                    for subf in subfuncs:
                        appendfunclist.append({'function':subf, 'dummy':[]})
            else:
                self._log.log(30, 'Function[{}] not found.'.format(funcitem['function']))
        for funcitem in appendfunclist:
            infolist = self.parser.getFuncInfo(funcitem['function'])
            if len(infolist) > 0:
                for funcinfo in infolist:
                    injectinfo.setdefault(funcinfo.relpath, {})
                    injectinfo[funcinfo.relpath].setdefault(funcinfo.name, [funcinfo, ()])
            else:
                self._log.log(30, 'Function[{}] not found.'.format(funcitem['function']))
        # 文件单位进行注入
        dspnames = []
        for fname in injectinfo.keys():
            fullpath = os.path.join(self.rootpath, fname)
            self.token.parse_file(fullpath)
            inputlist = []
            linelist = set()
            for funcname in injectinfo[fname].keys():
                inputlist.append({'function':funcname,'dummy':injectinfo[fname][funcname][1]})
                linelist |= set(range(int(injectinfo[fname][funcname][0].startline),
                                      int(injectinfo[fname][funcname][0].stopline)+1))
            encode = guessEncode(fullpath, 'cp932', 'cp936')[0]
            if not encode:
                encode = 'utf_8_sig'
            # 保存原始文件
            os.rename(fullpath, fullpath+'.org')
            # 注入
            self.token.inject(fullpath, encode, inputlist)
            # 提取注入内容到新文件用于后期显示
            fh = open(fullpath, 'r', encoding=encode)
            lines = fh.readlines()
            fh.close()
            dspname = os.path.basename(fullpath)
            if dspname in dspnames:
                fh = open(os.path.basename(fullpath), 'a', encoding='utf-8')
            else:
                fh = open(os.path.basename(fullpath), 'w', encoding='utf-8')
                dspnames.append(dspname)
            for idx, line in enumerate(lines):
                if idx+1 in linelist:
                    fh.write(line)
            fh.close()
