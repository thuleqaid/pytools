# -*- coding:utf-8 -*-
import os
from .logutil import LogUtil, registerLogger
from .guess import openTextFile
from .ply import lex
from .ply.lex import TOKEN

LOGNAME = "CTokens"
registerLogger(LOGNAME)

class CTokens(object):
    def __init__(self):
        self._log = LogUtil().logger(LOGNAME)
        self.dmyblock = {'BLOCK1':'DMYBOOL __tmp__ = DMYBLOCK("#{:0>2}");',
                         'BLOCK2':'__tmp__ = DMYBLOCK("#{:0>2}");',
                         'BLOCK3':'{{DMYBOOL __tmp__ = DMYBLOCK("#{:0>2}");',
                         'BLOCK4':'}}__tmp__ = DMYBLOCK("#{:0>2}");',
                         'BLOCK5':'DMYBOOL __tmp__ = DMYBLOCK("<{}>");',
                         'BLOCK6':'__tmp__ = DMYBLOCK("@{:0>2}");',
                         'COND1': '(DMYCOND(',
                         'COND2': ',"{}"))',
                        }
    def find_tok_column(self, token):
        last_cr = self.lexer.lexdata.rfind('\n', 0, token.lexpos)
        return token.lexpos - last_cr
    def parse_file(self, filepath, tagname=''):
        fh = openTextFile(('cp932', 'cp936'), filepath, 'r')
        text = fh.read()
        fh.close()
        if not tagname:
            tagname = os.path.basename(filepath)
        self.parse(text, tagname)
    def parse(self, text, tagname=''):
        self.tagname = tagname
        self.lexer = lex.lex(object=self)
        self.lexer.input(text)
        self.tokens = list(self.lexer)
        self.toklen = len(self.tokens)
        self.funcinfo = []  # set in inject()
        for idx, tok in enumerate(self.tokens):
            self._log.log(10, 'idx:{0} {1} col:{2}'.format(idx, str(tok), self.find_tok_column(tok)))
    def format(self):
        lines = self._format(0, self.toklen, 0)
        return lines
    def _format(self, startidx, stopidx, indent):
        lines = []
        i = self._next(startidx-1)
        while 0 <= i < stopidx:
            self._log.log(20, 'start:{0} stop:{1} current:{2}'.format(startidx, stopidx, i))
            if self.tokens[i].type == 'PPHASH':
                j = i
                j = self._next(i, 'NEWLINE', ignore_newline=False)
                lines.append(self._oneline(self.tokens[i:j], indent))
                self._log.log(10, 'PPHASH {0}-{1}'.format(i,j))
                i = self._next(j)
            elif self.tokens[i].type == 'IF':
                sects = []
                # if以及条件
                cond_stop = self._pair_next(i, 'RPAREN')
                sects.append((i, cond_stop))
                nextidx = self._next(cond_stop)
                if self.tokens[nextidx].type == 'LBRACE':
                    # if:True的处理是Block
                    cond_stop = self._pair_next(nextidx, 'RBRACE')
                    sects.append((nextidx, cond_stop))
                else:
                    # if:True的处理是一条语句
                    cond_stop = self._pair_next(nextidx, 'SEMI')
                    sects.append((nextidx, cond_stop))
                nextidx = self._next(cond_stop)
                while nextidx < stopidx and self.tokens[nextidx].type == 'ELSE':
                    nextidx2 = self._next(nextidx)
                    if self.tokens[nextidx2].type == 'IF':
                        # else if以及条件
                        cond_stop = self._pair_next(nextidx, 'RPAREN')
                        sects.append((nextidx, cond_stop))
                        nextidx = self._next(cond_stop)
                        if self.tokens[nextidx].type == 'LBRACE':
                            # else if:True的处理是Block
                            cond_stop = self._pair_next(nextidx, 'RBRACE')
                            sects.append((nextidx, cond_stop))
                        else:
                            # else if:True的处理是一条语句
                            cond_stop = self._pair_next(nextidx, 'SEMI')
                            sects.append((nextidx, cond_stop))
                    else:
                        # else
                        sects.append((nextidx, nextidx))
                        nextidx = self._next(nextidx)
                        if self.tokens[nextidx].type == 'LBRACE':
                            # else的处理是Block
                            cond_stop = self._pair_next(nextidx, 'RBRACE')
                            sects.append((nextidx, cond_stop))
                        else:
                            # else的处理是一条语句
                            cond_stop = self._pair_next(nextidx, 'SEMI')
                            sects.append((nextidx, cond_stop))
                        break
                    nextidx = self._next(cond_stop)
                self._log.log(10, 'IF {0}'.format(str(sects)))
                i = self._next(sects[-1][1])
                # if语句
                tmpline = self._oneline(self.tokens[sects[0][0]:sects[0][1]+1], indent) + ' {'
                lines.append(tmpline)
                # if的处理
                if self.tokens[sects[1][0]].type == 'LBRACE':
                    lines.extend(self._format(self._next(sects[1][0]), sects[1][1], indent + 1))
                else:
                    lines.extend(self._format(sects[1][0], sects[1][1]+1, indent + 1))
                lines.append('\t'*indent + '}')
                j = 2
                while j < len(sects):
                    # else[ if]语句
                    tmpline = ' ' + self._oneline(self.tokens[sects[j][0]:sects[j][1]+1], 0) + ' {'
                    lines[-1] += tmpline
                    # else[ if]的处理
                    if self.tokens[sects[j+1][0]].type == 'LBRACE':
                        lines.extend(self._format(self._next(sects[j+1][0]),sects[j+1][1], indent + 1))
                    else:
                        lines.extend(self._format(sects[j+1][0],sects[j+1][1]+1, indent + 1))
                    lines.append('\t'*indent + '}')
                    j += 2
            elif self.tokens[i].type == 'SWITCH':
                sects = []
                # switch以及条件
                cond_stop = self._pair_next(i, 'RPAREN')
                sects.append((i, cond_stop))
                # switch的范围
                lbrace = self._next(cond_stop)
                rbrace = self._pair_next(lbrace, 'RBRACE')
                # 下一个case/default的位置
                nextidx1 = self._pair_next(lbrace + 1, 'CASE')
                nextidx2 = self._pair_next(lbrace + 1, 'DEFAULT')
                if nextidx1 < 0:
                    nextidx1 = rbrace
                if nextidx2 < 0:
                    nextidx2 = rbrace
                nextidx = min(nextidx1, nextidx2)
                cond_stop = self._pair_next(nextidx, 'COLON')
                while 0 <= cond_stop < rbrace:
                    # case/default语句
                    sects.append((nextidx, cond_stop))
                    # case/default的处理
                    nextidx1 = self._pair_next(cond_stop + 1, 'CASE')
                    nextidx2 = self._pair_next(cond_stop + 1, 'DEFAULT')
                    if nextidx1 < 0:
                        nextidx1 = rbrace
                    if nextidx2 < 0:
                        nextidx2 = rbrace
                    nextidx = min(nextidx1, nextidx2)
                    if nextidx < rbrace:
                        sects.append((self._next(cond_stop), nextidx))
                        cond_stop = self._pair_next(nextidx + 1, 'COLON')
                    else:
                        sects.append((self._next(cond_stop), self._prev(rbrace)))
                        cond_stop = nextidx
                self._log.log(10, 'SWITCH {0}'.format(str(sects)))
                i = self._next(rbrace)
                # switch语句
                tmpline = self._oneline(self.tokens[sects[0][0]:sects[0][1]+1], indent) + ' {'
                lines.append(tmpline)
                j = 1
                while j < len(sects):
                    # case/default语句
                    tmpline = self._oneline(self.tokens[sects[j][0]:sects[j][1]], indent + 1) + ':'
                    lines.append(tmpline)
                    # case/default的处理
                    lines.extend(self._format(sects[j+1][0],sects[j+1][1]+1, indent + 2))
                    j += 2
                tmpline = '\t'*indent + '}'
                lines.append(tmpline)
            elif self.tokens[i].type in ('FOR', 'WHILE'):
                sects = []
                # for以及条件
                cond_stop = self._pair_next(i, 'RPAREN')
                sects.append((i, cond_stop))
                nextidx = self._next(cond_stop)
                if self.tokens[nextidx].type == 'LBRACE':
                    # for的处理是Block
                    cond_stop = self._pair_next(nextidx, 'RBRACE')
                    sects.append((nextidx, cond_stop))
                else:
                    # for的处理是一条语句
                    cond_stop = self._pair_next(nextidx, 'SEMI')
                    sects.append((nextidx, cond_stop))
                self._log.log(10, '{1} {0}'.format(str(sects), self.tokens[i].type))
                i = self._next(sects[-1][1])
                # for语句
                tmpline = self._oneline(self.tokens[sects[0][0]:sects[0][1]+1], indent) + ' {'
                lines.append(tmpline)
                # for的处理
                if self.tokens[sects[1][0]].type == 'LBRACE':
                    lines.extend(self._format(self._next(sects[1][0]),sects[1][1], indent + 1))
                else:
                    lines.extend(self._format(sects[1][0],sects[1][1]+1, indent + 1))
                lines.append('\t'*indent + '}')
            elif self.tokens[i].type == 'DO':
                sects = []
                # do
                sects.append((i, i))
                nextidx = self._next(i)
                if self.tokens[nextidx].type == 'LBRACE':
                    # do的处理是Block
                    cond_stop = self._pair_next(nextidx, 'RBRACE')
                    sects.append((nextidx, cond_stop))
                else:
                    # do的处理是一条语句
                    cond_stop = self._pair_next(nextidx, 'SEMI')
                    sects.append((nextidx, cond_stop))
                # while
                nextidx = self._next(cond_stop)
                cond_stop = self._pair_next(nextidx, 'SEMI')
                sects.append((nextidx, cond_stop))
                self._log.log(10, '{1} {0}'.format(str(sects), self.tokens[i].type))
                i = self._next(sects[-1][1])
                # do语句
                tmpline = self._oneline(self.tokens[sects[0][0]:sects[0][1]+1], indent) + ' {'
                lines.append(tmpline)
                # do的处理
                if self.tokens[sects[1][0]].type == 'LBRACE':
                    lines.extend(self._format(self._next(sects[1][0]),sects[1][1], indent + 1))
                else:
                    lines.extend(self._format(sects[1][0],sects[1][1]+1, indent + 1))
                tmpline = '\t'*indent + '} ' + self._oneline(self.tokens[sects[2][0]:sects[2][1]+1], 0)
                lines.append(tmpline)
            else:
                sects = []
                j = i
                while j < stopidx and (self.tokens[j].type != 'SEMI' and self.tokens[j].type != 'LBRACE'):
                    j += 1
                if j >= stopidx:
                    break
                if self.tokens[j].type == 'SEMI':
                    # 一行语句
                    sects.append((i,j))
                    self._log.log(10, 'Normal {0}'.format(str(sects)))
                    i = self._next(j)
                    lines.append(self._oneline(self.tokens[sects[0][0]:sects[0][1]+1], indent))
                else:
                    if self.tokens[self._prev(j)].type == 'EQUALS':
                        # 变量初期化
                        j = self._next(j, 'SEMI')
                        sects.append((i,j))
                        self._log.log(10, 'Normal {0}'.format(str(sects)))
                        i = self._next(j)
                        lines.append(self._oneline(self.tokens[sects[0][0]:sects[0][1]+1], indent))
                    else:
                        # 函数/Block
                        nextidx = self._pair_next(j, 'RBRACE')
                        sects.append((i,self._prev(j)))
                        sects.append((j,nextidx))
                        self._log.log(10, 'Block {0}'.format(str(sects)))
                        i = self._next(nextidx)
                        # 函数/Block申明
                        lines.append(self._oneline(self.tokens[sects[0][0]:sects[0][1]+1], indent))
                        lines.append(self._oneline(self.tokens[sects[1][0]:sects[1][0]+1], indent))
                        # 函数/Block处理
                        lines.extend(self._format(self._next(sects[1][0]), sects[1][1], indent + 1))
                        lines.append(self._oneline(self.tokens[sects[1][1]:sects[1][1]+1], indent))
        return lines
    def _funcinfo(self, bracepair):
        k = bracepair[2]
        funcname = self.tokens[k].value
        # 查找参数列表
        i = self._next(k, 'LPAREN')
        j = self._pair_next(i, 'RPAREN')
        h = self._pair_next(i+1, 'COMMA')
        if h < 0:
            h = j
        if h >= j:
            cnt = 0
            while i < j:
                i = self._next(i)
                cnt += 1
            if cnt > 1:
                paramcnt = 1 # 有1个参数
            else:
                paramcnt = 0 # 没有参数
        else:
            paramcnt = 2 # 有2个及以上参数
        paramlist = []
        paramtxt = ''
        if paramcnt > 0:
            i = self._next(i, ignore_space=False)
            while i < j:
                if i == h:
                    paramtxt = paramtxt.strip()
                    paramlist.append((paramname, paramtxt))
                    paramtxt = ''
                    h = self._pair_next(h+1, 'COMMA')
                    if h < 0:
                        h = j
                elif i < h:
                    if self.tokens[i].type == 'ID':
                        paramname = self.tokens[i].value
                    paramtxt += self.tokens[i].value
                i = self._next(i, ignore_space=False)
        paramtxt = paramtxt.strip()
        paramlist.append((paramname, paramtxt))
        # 查找函数类型
        h = self._prev(k, 'PPHASH')
        if h >= 0:
            h = self._next(h, 'NEWLINE', ignore_newline=False)
        else:
            h = 0
        k = self._prev(k)
        functype = ''
        while k >= h:
            if self.tokens[k].type in ('RBRACE', 'SEMI'):
                break
            else:
                functype = self.tokens[k].value + ' ' + functype
            k = self._prev(k)
        functype = functype.strip()
        paramlist.insert(0, (funcname, functype))
        return paramlist
    def inject(self, outfile='out.c', encode='utf-8', funclist=None):
        # funclist: [{'function':function-name,'dummy':[(org-function-name, dmy-function-name),...]},...]
        # 查找函数
        bracepair = []
        i = 0
        while 0 <= i < self.toklen:
            i = self._next(i, 'LBRACE')
            if 0 <= i < self.toklen:
                k = self._prev(i)
                if k >= 0 and self.tokens[k].type == 'EQUALS':
                    # 变量初期化
                    pass
                else:
                    k = self._pair_prev(i-1,'LPAREN')
                    k = self._prev(k, 'ID')
                    j = self._pair_next(i, 'RBRACE')
                    if funclist:
                        # 只注入指定函数
                        for funcitem in funclist:
                            if funcitem['function'] == self.tokens[k].value:
                                bracepair.append((i, j, k, funcitem['dummy']))
                                break
                    else:
                        # 注入全部函数
                        bracepair.append((i, j, k))
                i = j + 1
        fh = open(outfile, 'w', encoding=encode)
        lasttokidx = 0
        # 遍历需要注入的函数
        self.funcinfo = []
        for item in bracepair:
            self.funcinfo.append(self._funcinfo(item))
            injectlist = []
            blocklist = self._inject(item[0] + 1, item[1], [0])
            # 函数开始的'{'后加入口log
            blocklist.insert(0, (item[0]+1, 'BLOCK5', '{0}:{1}'.format(self.tagname, self.tokens[item[2]].value)))
            # 函数中所有'return'前加返回log
            rcnt = 0
            for i in range(item[0],item[1]):
                if self.tokens[i].type == 'RETURN':
                    blocklist.append((i, 'BLOCK6'))
                    rcnt += 1
            # 函数结束的'}'前加返回log
            blocklist.append((item[1], 'BLOCK6'))
            bidx = 1
            for idx, bitem in enumerate(sorted(blocklist)):
                if bitem[1] in ('COND1', 'COND2'):
                    condkey = self._condkey(bitem[2]) + self._condkey(bitem[3])
                    injectlist.append((bitem[0], self.dmyblock[bitem[1]].format(condkey)))
                elif bitem[1] in ('BLOCK5',):
                    injectlist.append((bitem[0], self.dmyblock.get(bitem[1], bitem[1]).format(bitem[2])))
                else:
                    injectlist.append((bitem[0], self.dmyblock.get(bitem[1], bitem[1]).format(bidx)))
                    bidx += 1
            if funclist:
                # 指定函数的子函数名变换表
                replacedict = dict(item[3])
            else:
                replacedict = {}
            ipos = 0
            ilen = len(injectlist)
            # 输出到当前注入函数结尾为止
            while lasttokidx <= item[1]:
                # 注入内容
                while ipos < ilen and lasttokidx == injectlist[ipos][0]:
                    fh.write(injectlist[ipos][1])
                    ipos += 1
                if item[0] <= lasttokidx <= item[1]:
                    # 当前函数范围内，子函数名变换处理
                    if self.tokens[lasttokidx].type == 'ID':
                        fh.write(replacedict.get(self.tokens[lasttokidx].value, self.tokens[lasttokidx].value))
                    else:
                        fh.write(self.tokens[lasttokidx].value)
                else:
                    fh.write(self.tokens[lasttokidx].value)
                lasttokidx += 1
        # 输出最后一个注入函数之后到文件结尾的内容
        while lasttokidx < self.toklen:
            fh.write(self.tokens[lasttokidx].value)
            lasttokidx += 1
        fh.close()
    def _inject(self, startidx, stopidx, condidx):
        injectlist = []
        i = self._next(startidx-1)
        while 0 <= i < stopidx:
            self._log.log(20, 'start:{0} stop:{1} current:{2}'.format(startidx, stopidx, i))
            if self.tokens[i].type == 'PPHASH':
                j = i
                j = self._next(i, 'NEWLINE', ignore_newline=False)
                self._log.log(10, 'PPHASH {0}-{1}'.format(i,j))
                i = self._next(j)
            elif self.tokens[i].type == 'IF':
                sects = []
                # if以及条件
                cond_stop = self._pair_next(i, 'RPAREN')
                sects.append((i, cond_stop))
                nextidx = self._next(cond_stop)
                if self.tokens[nextidx].type == 'LBRACE':
                    # if:True的处理是Block
                    cond_stop = self._pair_next(nextidx, 'RBRACE')
                    sects.append((nextidx, cond_stop))
                else:
                    # if:True的处理是一条语句
                    cond_stop = self._pair_next(nextidx, 'SEMI')
                    sects.append((nextidx, cond_stop))
                nextidx = self._next(cond_stop)
                while nextidx < stopidx and self.tokens[nextidx].type == 'ELSE':
                    nextidx2 = self._next(nextidx)
                    if self.tokens[nextidx2].type == 'IF':
                        # else if以及条件
                        cond_stop = self._pair_next(nextidx, 'RPAREN')
                        sects.append((nextidx, cond_stop))
                        nextidx = self._next(cond_stop)
                        if self.tokens[nextidx].type == 'LBRACE':
                            # else if:True的处理是Block
                            cond_stop = self._pair_next(nextidx, 'RBRACE')
                            sects.append((nextidx, cond_stop))
                        else:
                            # else if:True的处理是一条语句
                            cond_stop = self._pair_next(nextidx, 'SEMI')
                            sects.append((nextidx, cond_stop))
                    else:
                        # else
                        sects.append((nextidx, nextidx))
                        nextidx = self._next(nextidx)
                        if self.tokens[nextidx].type == 'LBRACE':
                            # else的处理是Block
                            cond_stop = self._pair_next(nextidx, 'RBRACE')
                            sects.append((nextidx, cond_stop))
                        else:
                            # else的处理是一条语句
                            cond_stop = self._pair_next(nextidx, 'SEMI')
                            sects.append((nextidx, cond_stop))
                        break
                    nextidx = self._next(cond_stop)
                self._log.log(10, 'IF {0}'.format(str(sects)))
                i = self._next(sects[-1][1])
                j = 0
                while j < len(sects) - 2:
                    injectlist.extend(self._splitcond(sects[j][0], sects[j][1], condidx))
                    condidx[0] += 1
                    if self.tokens[sects[j+1][0]].type == 'LBRACE':
                        injectlist.append((sects[j+1][0]+1, 'BLOCK1'))
                        injectlist.extend(self._inject(self._next(sects[j+1][0]), sects[j+1][1], condidx))
                    else:
                        injectlist.append((sects[j+1][0], 'BLOCK3'))
                        injectlist.append((sects[j+1][1]+1, '}}'))
                    j += 2
                if sects[j][0] != sects[j][1]:
                    injectlist.extend(self._splitcond(sects[j][0], sects[j][1], condidx))
                    condidx[0] += 1
                if self.tokens[sects[j+1][0]].type == 'LBRACE':
                    injectlist.append((sects[j+1][0]+1, 'BLOCK1'))
                    injectlist.extend(self._inject(self._next(sects[j+1][0]), sects[j+1][1], condidx))
                    injectlist.append((sects[-1][1]+1,'BLOCK2'))
                else:
                    injectlist.append((sects[j+1][0], 'BLOCK3'))
                    injectlist.append((sects[j+1][1]+1, 'BLOCK4'))
            elif self.tokens[i].type == 'SWITCH':
                sects = []
                # switch以及条件
                cond_stop = self._pair_next(i, 'RPAREN')
                sects.append((i, cond_stop))
                # switch的范围
                lbrace = self._next(cond_stop)
                rbrace = self._pair_next(lbrace, 'RBRACE')
                # 下一个case/default的位置
                nextidx1 = self._pair_next(lbrace + 1, 'CASE')
                nextidx2 = self._pair_next(lbrace + 1, 'DEFAULT')
                if nextidx1 < 0:
                    nextidx1 = rbrace
                if nextidx2 < 0:
                    nextidx2 = rbrace
                nextidx = min(nextidx1, nextidx2)
                cond_stop = self._pair_next(nextidx, 'COLON')
                while 0 <= cond_stop < rbrace:
                    # case/default语句
                    sects.append((nextidx, cond_stop))
                    # case/default的处理
                    nextidx1 = self._pair_next(cond_stop + 1, 'CASE')
                    nextidx2 = self._pair_next(cond_stop + 1, 'DEFAULT')
                    if nextidx1 < 0:
                        nextidx1 = rbrace
                    if nextidx2 < 0:
                        nextidx2 = rbrace
                    nextidx = min(nextidx1, nextidx2)
                    if nextidx < rbrace:
                        sects.append((self._next(cond_stop), nextidx))
                        cond_stop = self._pair_next(nextidx + 1, 'COLON')
                    else:
                        sects.append((self._next(cond_stop), self._prev(rbrace)))
                        cond_stop = nextidx
                self._log.log(10, 'SWITCH {0}'.format(str(sects)))
                i = self._next(rbrace)
                j = 1
                while j < len(sects):
                    # case/default语句
                    injectlist.append((sects[j][1]+1, 'BLOCK2'))
                    # case/default的处理
                    injectlist.extend(self._inject(sects[j+1][0],sects[j+1][1]+1, condidx))
                    j += 2
            elif self.tokens[i].type in ('FOR', 'WHILE'):
                sects = []
                # for以及条件
                cond_stop = self._pair_next(i, 'RPAREN')
                sects.append((i, cond_stop))
                nextidx = self._next(cond_stop)
                if self.tokens[nextidx].type == 'LBRACE':
                    # for的处理是Block
                    cond_stop = self._pair_next(nextidx, 'RBRACE')
                    sects.append((nextidx, cond_stop))
                else:
                    # for的处理是一条语句
                    cond_stop = self._pair_next(nextidx, 'SEMI')
                    sects.append((nextidx, cond_stop))
                self._log.log(10, '{1} {0}'.format(str(sects), self.tokens[i].type))
                i = self._next(sects[-1][1])
                # for的处理
                if self.tokens[sects[1][0]].type == 'LBRACE':
                    injectlist.append((sects[1][0]+1, 'BLOCK1'))
                    injectlist.extend(self._inject(self._next(sects[1][0]),sects[1][1], condidx))
                    injectlist.append((sects[1][1]+1, 'BLOCK2'))
                else:
                    injectlist.append((sects[1][0], 'BLOCK3'))
                    injectlist.append((sects[1][1]+1, 'BLOCK4'))
            elif self.tokens[i].type == 'DO':
                sects = []
                # do
                sects.append((i, i))
                nextidx = self._next(i)
                if self.tokens[nextidx].type == 'LBRACE':
                    # do的处理是Block
                    cond_stop = self._pair_next(nextidx, 'RBRACE')
                    sects.append((nextidx, cond_stop))
                else:
                    # do的处理是一条语句
                    cond_stop = self._pair_next(nextidx, 'SEMI')
                    sects.append((nextidx, cond_stop))
                # while
                nextidx = self._next(cond_stop)
                cond_stop = self._pair_next(nextidx, 'SEMI')
                sects.append((nextidx, cond_stop))
                self._log.log(10, '{1} {0}'.format(str(sects), self.tokens[i].type))
                i = self._next(sects[-1][1])
                # do的处理
                if self.tokens[sects[1][0]].type == 'LBRACE':
                    injectlist.append((sects[1][0]+1, 'BLOCK1'))
                    injectlist.extend(self._inject(self._next(sects[1][0]),sects[1][1], condidx))
                    injectlist.append((sects[2][1]+1, 'BLOCK2'))
                else:
                    injectlist.append((sects[1][0], 'BLOCK3'))
                    injectlist.append((sects[1][1]+1, '}}'))
                    injectlist.append((sects[2][1]+1, 'BLOCK2'))
            else:
                sects = []
                j = i
                while j < stopidx and (self.tokens[j].type != 'SEMI' and self.tokens[j].type != 'LBRACE'):
                    j += 1
                if j >= stopidx:
                    break
                if self.tokens[j].type == 'SEMI':
                    # 一行语句
                    sects.append((i,j))
                    self._log.log(10, 'Normal {0}'.format(str(sects)))
                    i = self._next(j)
                else:
                    if self.tokens[self._prev(j)].type == 'EQUALS':
                        # 变量初期化
                        j = self._next(j, 'SEMI')
                        sects.append((i,j))
                        self._log.log(10, 'Normal {0}'.format(str(sects)))
                        i = self._next(j)
                    else:
                        # 函数/Block
                        nextidx = self._pair_next(j, 'RBRACE')
                        sects.append((i,self._prev(j)))
                        sects.append((j,nextidx))
                        self._log.log(10, 'Block {0}'.format(str(sects)))
                        i = self._next(nextidx)
                        ## 函数/Block处理
                        injectlist.append((sects[1][0]+1, 'BLOCK1'))
                        injectlist.extend(self._inject(self._next(sects[1][0]), sects[1][1], condidx))
                        injectlist.append((sects[1][1], 'BLOCK2'))
        return injectlist
    def _splitcond(self, startidx, stopidx, condidx):
        self._log.log(10, "SplitCondition: {}-{}@{}".format(startidx, stopidx, condidx[0]))
        condlist = []
        subidx = 0
        # 查找所有的'(',')','||','&&'
        ppair = []
        cpos = []
        curpos = self._next(startidx, 'LPAREN')
        paircount = 1
        ppair.append(('(', curpos, paircount))
        curpos += 1
        while paircount > 0:
            if self.tokens[curpos].type == 'LPAREN':
                paircount += 1
                ppair.append(('(', curpos, paircount))
            elif self.tokens[curpos].type == 'RPAREN':
                ppair.append((')', curpos, paircount))
                paircount -= 1
            elif self.tokens[curpos].type == 'LOR':
                cpos.append(len(ppair))
                ppair.append(('|', curpos, paircount))
            elif self.tokens[curpos].type == 'LAND':
                cpos.append(len(ppair))
                ppair.append(('&', curpos, paircount))
            curpos += 1
        self._log.log(10, "PPAIR:{} CPOS:{}".format(str(ppair), str(cpos)))
        # 删除无用的'('/')'对
        if len(cpos) > 0:
            if len(cpos) > 1:
                # 没有用'('/')'包住的中间条件
                i = len(cpos) - 2
                i1 = self._next(ppair[cpos[i]][1])
                i2 = self._prev(ppair[cpos[i+1]][1])
                if self.tokens[i2].type != 'RPAREN' or self.tokens[i1].type != 'LPAREN':
                    curpos = cpos[i+1] - 1
                    while curpos > cpos[i]:
                        ppair.pop(curpos)
                        curpos -= 1
                # 重置cpos
                cpos = []
                for cposidx, pairdata in enumerate(ppair):
                    if pairdata[0] in ('|', '&'):
                        cpos.append(cposidx)
            # 结尾部分
            curpos = cpos[-1]
            nextpos = self._next(ppair[curpos][1])
            if self.tokens[nextpos].type == 'LPAREN':
                level = ppair[curpos+1][2]
                curpos += 2
                while ppair[curpos][2] > level:
                    curpos += 1
            else:
                curpos = cpos[-1] + 1
                pcnt = 1
                while curpos < len(ppair):
                    if ppair[curpos][0] == '(':
                        pcnt += 1
                    elif ppair[curpos][0] == ')':
                        pcnt -= 1
                    if pcnt == 0:
                        break
                    curpos += 1
            curpos -= 1
            while curpos > cpos[-1] + 1:
                ppair.pop(curpos)
                curpos -= 1
            # 中间部分
            cposidx = len(cpos) - 2
            while cposidx >= 0:
                if cpos[cposidx] + 1 == cpos[cposidx+1]:
                    # 没有用'('/')'包住的中间条件
                    pass
                elif ppair[cpos[cposidx]+1][2] > ppair[cpos[cposidx+1]-1][2]:
                    level = ppair[cpos[cposidx]+1][2]
                    curpos = cpos[cposidx]+2
                    while ppair[curpos][2] > level:
                        curpos += 1
                    curpos -= 1
                    while curpos > cpos[cposidx] + 1:
                        ppair.pop(curpos)
                        curpos -= 1
                else:
                    level = ppair[cpos[cposidx+1]-1][2]
                    curpos = cpos[cposidx+1]-2
                    while ppair[curpos][2] > level:
                        ppair.pop(curpos)
                        curpos -= 1
                cposidx -= 1
            # 开始部分
            curpos = cpos[0]
            nextpos = self._prev(ppair[curpos][1])
            if self.tokens[nextpos].type == 'RPAREN':
                level = ppair[curpos-1][2]
                curpos -= 2
                while ppair[curpos][2] > level:
                    ppair.pop(curpos)
                    curpos -= 1
            else:
                curpos = cpos[0] - 1
                pcnt = -1
                while curpos >= 0:
                    if ppair[curpos][0] == '(':
                        pcnt += 1
                    elif ppair[curpos][0] == ')':
                        pcnt -= 1
                    if pcnt == 0:
                        break
                    curpos -= 1
                curpos += 1
                curpos2 = cpos[0] - 1
                while curpos2 >= curpos:
                    ppair.pop(curpos2)
                    curpos2 -= 1
            # 重置cpos
            cpos = []
            for cposidx, pairdata in enumerate(ppair):
                if pairdata[0] in ('|', '&'):
                    cpos.append(cposidx)
            self._log.log(10, "Adjusted PPAIR:{} CPOS:{}".format(str(ppair), str(cpos)))
            if ppair[cpos[0]-1][0] != ')':
                condlist.append((ppair[cpos[0]-1][1]+1, 'COND1', condidx[0], subidx))
                condlist.append((ppair[cpos[0]][1], 'COND2', condidx[0], subidx))
            else:
                condlist.append((ppair[cpos[0]-2][1]+1, 'COND1', condidx[0], subidx))
                condlist.append((ppair[cpos[0]-1][1], 'COND2', condidx[0], subidx))
            subidx += 1
            cposidx = 0
            while cposidx < len(cpos) - 1:
                if cpos[cposidx] + 1 == cpos[cposidx+1]:
                    # 没有用'('/')'包住的中间条件
                    condlist.append((ppair[cpos[cposidx]][1]+1, 'COND1', condidx[0], subidx))
                    condlist.append((ppair[cpos[cposidx+1]][1], 'COND2', condidx[0], subidx))
                elif ppair[cpos[cposidx]+1][2] > ppair[cpos[cposidx+1]-1][2]:
                    condlist.append((ppair[cpos[cposidx]+1][1]+1, 'COND1', condidx[0], subidx))
                    condlist.append((ppair[cpos[cposidx]+2][1], 'COND2', condidx[0], subidx))
                else:
                    condlist.append((ppair[cpos[cposidx+1]-2][1]+1, 'COND1', condidx[0], subidx))
                    condlist.append((ppair[cpos[cposidx+1]-1][1], 'COND2', condidx[0], subidx))
                subidx += 1
                cposidx += 1
            if ppair[cpos[-1]+1][0] != '(':
                condlist.append((ppair[cpos[-1]][1]+1, 'COND1', condidx[0], subidx))
                condlist.append((ppair[cpos[-1]+1][1], 'COND2', condidx[0], subidx))
            else:
                condlist.append((ppair[cpos[-1]+1][1]+1, 'COND1', condidx[0], subidx))
                condlist.append((ppair[cpos[-1]+2][1], 'COND2', condidx[0], subidx))
        else:
            # 单一条件
            condlist.append((ppair[0][1]+1, 'COND1', condidx[0], subidx))
            condlist.append((ppair[-1][1], 'COND2', condidx[0], subidx))
        return condlist
    def _condkey(self, idx):
        keylist = ['A','B','C','D','E','F','G',
                   'H','I','J','K','L','M','N',
                   'O','P','Q','R','S','T',
                   'U','V','W','X','Y','Z',
                   'a','b','c','d','e','f','g',
                   'h','i','j','k','l','m','n',
                   'o','p','q','r','s','t',
                   'u','v','w','x','y','z']
        return keylist[idx]
    def _next(self, startidx, target_type='', ignore_newline=True, ignore_space=True, ignore_comment=True):
        return self._find(1, startidx, target_type, ignore_newline, ignore_space, ignore_comment)
    def _prev(self, startidx, target_type='', ignore_newline=True, ignore_space=True, ignore_comment=True):
        return self._find(-1, startidx, target_type, ignore_newline, ignore_space, ignore_comment)
    def _find(self, step, startidx, target_type, ignore_newline, ignore_space, ignore_comment):
        j = startidx + step
        while j < self.toklen and j >= 0:
            if self.tokens[j].type == 'SPANLINE':
                pass
            elif ignore_newline and self.tokens[j].type == 'NEWLINE':
                pass
            elif ignore_space and self.tokens[j].type == 'SPACE':
                pass
            elif ignore_comment and self.tokens[j].type in ('COMMENT1', 'COMMENT2'):
                pass
            else:
                if target_type:
                    if self.tokens[j].type == target_type:
                        break
                    else:
                        pass
                else:
                    break
            j += step
        if j >= self.toklen:
            j = -1
        return j
    def _pair_next(self, startidx, target_type, ignore_newline=True, ignore_space=True, ignore_comment=True):
        return self._pair(1, startidx, target_type, ignore_newline, ignore_space, ignore_comment)
    def _pair_prev(self, startidx, target_type, ignore_newline=True, ignore_space=True, ignore_comment=True):
        return self._pair(-1, startidx, target_type, ignore_newline, ignore_space, ignore_comment)
    def _pair(self, step, startidx, findtype, ignore_newline, ignore_space, ignore_comment):
        j = startidx
        paren = [0, 0, 0]
        # 查找条件结束位置
        while 0 <= j < self.toklen:
            if self.tokens[j].type == 'LPAREN':
                paren[0] += 1
            elif self.tokens[j].type == 'RPAREN':
                paren[0] -= 1
            elif self.tokens[j].type == 'LBRACKET':
                paren[1] += 1
            elif self.tokens[j].type == 'RBRACKET':
                paren[1] -= 1
            elif self.tokens[j].type == 'LBRACE':
                paren[2] += 1
            elif self.tokens[j].type == 'RBRACE':
                paren[2] -= 1
            if not any(paren) and self.tokens[j].type == findtype:
                # 括号匹配，且找到目标种别时退出
                break
            j = self._find(step,j,'',ignore_newline,ignore_space,ignore_comment)
        return j
    def _oneline(self, tokens, indent):
        tmpline = '\t' * indent
        subtokens = [x for x in tokens if x.type not in ('NEWLINE', 'SPACE', 'COMMENT1', 'COMMENT2', 'SPANLINE')]
        ltrim = ('COMMA', 'SEMI')
        rtrim = ('ID', 'INT_CONST_DEC', 'INT_CONST_OCT', 'INT_CONST_HEX', 'INT_CONST_BIN', 'FLOAT_CONST')
        btrim = ('LBRACKET', 'RBRACKET', 'ARROW', 'PERIOD')
        if len(subtokens) > 0 and subtokens[0].type == 'PPHASH':
            # 预处理语句：'#'与预处理指令之间不加空格
            tmpline += '#'
            subtokens = subtokens[1:]
        for idx,item in enumerate(subtokens):
            if item.type in ltrim or item.type in btrim:
                if idx > 0:
                    # 前面不加空格
                    tmpline = tmpline[:-1] + item.value + ' '
                else:
                    tmpline += item.value + ' '
            elif item.type == 'LPAREN':
                if idx > 0 and subtokens[idx-1].type in ('ID',):
                    # '('前面是标识符时，认为是函数，中间不加空格
                    tmpline = tmpline[:-1] + item.value + ' '
                else:
                    tmpline += item.value + ' '
            else:
                if idx > 0 and subtokens[idx-1].type in ('RPAREN',):
                    if item.type in rtrim:
                        # ')'后面是标识符或常数时，中间不加空格
                        tmpline = tmpline[:-1] + item.value + ' '
                    else:
                        tmpline += item.value + ' '
                elif idx > 0 and subtokens[idx-1].type in btrim:
                    tmpline = tmpline[:-1] + item.value + ' '
                else:
                    tmpline += item.value + ' '
        return tmpline[:-1]

    ## Reserved keywords
    keywords = (
        '_BOOL', '_COMPLEX', 'AUTO', 'BREAK', 'CASE', 'CHAR', 'CONST',
        'CONTINUE', 'DEFAULT', 'DO', 'DOUBLE', 'ELSE', 'ENUM', 'EXTERN',
        'FLOAT', 'FOR', 'GOTO', 'IF', 'INLINE', 'INT', 'LONG',
        'REGISTER', 'OFFSETOF',
        'RESTRICT', 'RETURN', 'SHORT', 'SIGNED', 'SIZEOF', 'STATIC', 'STRUCT',
        'SWITCH', 'TYPEDEF', 'UNION', 'UNSIGNED', 'VOID',
        'VOLATILE', 'WHILE',
    )
    keyword_map = {}
    for keyword in keywords:
        if keyword == '_BOOL':
            keyword_map['_Bool'] = keyword
        elif keyword == '_COMPLEX':
            keyword_map['_Complex'] = keyword
        else:
            keyword_map[keyword.lower()] = keyword
    ## All the tokens recognized by the lexer
    tokens = keywords + (
        # Span line
        'SPANLINE',
        # Newlines
        'NEWLINE',
        # Comments
        'COMMENT1', 'COMMENT2',
        # SPACE
        'SPACE',
        # Identifiers
        'ID',
        # Type identifiers (identifiers previously defined as
        # types with typedef)
        'TYPEID',
        # constants
        'INT_CONST_DEC', 'INT_CONST_OCT', 'INT_CONST_HEX', 'INT_CONST_BIN',
        'FLOAT_CONST', 'HEX_FLOAT_CONST',
        'CHAR_CONST',
        'WCHAR_CONST',
        # String literals
        'STRING_LITERAL',
        'WSTRING_LITERAL',
        # Operators
        'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MOD',
        'OR', 'AND', 'NOT', 'XOR', 'LSHIFT', 'RSHIFT',
        'LOR', 'LAND', 'LNOT',
        'LT', 'LE', 'GT', 'GE', 'EQ', 'NE',
        # Assignment
        'EQUALS', 'TIMESEQUAL', 'DIVEQUAL', 'MODEQUAL',
        'PLUSEQUAL', 'MINUSEQUAL',
        'LSHIFTEQUAL','RSHIFTEQUAL', 'ANDEQUAL', 'XOREQUAL',
        'OREQUAL',
        # Increment/decrement
        'PLUSPLUS', 'MINUSMINUS',
        # Structure dereference (->)
        'ARROW',
        # Conditional operator (?)
        'CONDOP',
        # Delimeters
        'LPAREN', 'RPAREN',         # ( )
        'LBRACKET', 'RBRACKET',     # [ ]
        'LBRACE', 'RBRACE',         # { }
        'COMMA', 'PERIOD',          # . ,
        'SEMI', 'COLON',            # ; :
        # Ellipsis (...)
        'ELLIPSIS',
        # pre-processor
        'PPHASH',      # '#'
    )
    # valid C identifiers (K&R2: A.2.3), plus '$' (supported by some compilers)
    identifier = r'[a-zA-Z_$][0-9a-zA-Z_$]*'
    hex_prefix = '0[xX]'
    hex_digits = '[0-9a-fA-F]+'
    bin_prefix = '0[bB]'
    bin_digits = '[01]+'
    # integer constants (K&R2: A.2.5.1)
    integer_suffix_opt = r'(([uU]ll)|([uU]LL)|(ll[uU]?)|(LL[uU]?)|([uU][lL])|([lL][uU]?)|[uU])?'
    decimal_constant = '(0'+integer_suffix_opt+')|([1-9][0-9]*'+integer_suffix_opt+')'
    octal_constant = '0[0-7]*'+integer_suffix_opt
    hex_constant = hex_prefix+hex_digits+integer_suffix_opt
    bin_constant = bin_prefix+bin_digits+integer_suffix_opt
    # character constants (K&R2: A.2.5.2)
    simple_escape = r"""([a-zA-Z._~!=&\^\-\\?'"])"""
    decimal_escape = r"""(\d+)"""
    hex_escape = r"""(x[0-9a-fA-F]+)"""
    escape_sequence = r"""(\\("""+simple_escape+'|'+decimal_escape+'|'+hex_escape+'))'
    cconst_char = r"""([^'\\\n]|"""+escape_sequence+')'
    char_const = "'"+cconst_char+"'"
    wchar_const = 'L'+char_const
    # string literals (K&R2: A.2.6)
    string_char = r"""([^"\\\n]|"""+escape_sequence+')'
    string_literal = '"'+string_char+'*"'
    wstring_literal = 'L'+string_literal
    # floating constants (K&R2: A.2.5.3)
    exponent_part = r"""([eE][-+]?[0-9]+)"""
    fractional_constant = r"""([0-9]*\.[0-9]+)|([0-9]+\.)"""
    floating_constant = '(((('+fractional_constant+')'+exponent_part+'?)|([0-9]+'+exponent_part+'))[FfLl]?)'
    binary_exponent_part = r'''([pP][+-]?[0-9]+)'''
    hex_fractional_constant = '((('+hex_digits+r""")?\."""+hex_digits+')|('+hex_digits+r"""\.))"""
    hex_floating_constant = '('+hex_prefix+'('+hex_digits+'|'+hex_fractional_constant+')'+binary_exponent_part+'[FfLl]?)'
    def t_PPHASH(self, t):
        r'[ \t]*\#'
        t.type = 'PPHASH'
        return t
    t_SPACE = '[ \t]+'
    # Span lines
    def t_SPANLINE(self, t):
        r'\\\n'
        t.lexer.lineno += 1
        return t
    # Newlines
    def t_NEWLINE(self, t):
        r'\n+'
        t.lexer.lineno += t.value.count("\n")
        return t
    # Comments
    def t_COMMENT1(self, t):
        r'//(.*?\\\n)*.*'
        return t
    def t_COMMENT2(self, t):
        r'/\*(.|\n)*?\*/'
        t.lexer.lineno += t.value.count('\n')
        return t
    # Operators
    t_PLUS              = r'\+'
    t_MINUS             = r'-'
    t_TIMES             = r'\*'
    t_DIVIDE            = r'/'
    t_MOD               = r'%'
    t_OR                = r'\|'
    t_AND               = r'&'
    t_NOT               = r'~'
    t_XOR               = r'\^'
    t_LSHIFT            = r'<<'
    t_RSHIFT            = r'>>'
    t_LOR               = r'\|\|'
    t_LAND              = r'&&'
    t_LNOT              = r'!'
    t_LT                = r'<'
    t_GT                = r'>'
    t_LE                = r'<='
    t_GE                = r'>='
    t_EQ                = r'=='
    t_NE                = r'!='
    # Assignment operators
    t_EQUALS            = r'='
    t_TIMESEQUAL        = r'\*='
    t_DIVEQUAL          = r'/='
    t_MODEQUAL          = r'%='
    t_PLUSEQUAL         = r'\+='
    t_MINUSEQUAL        = r'-='
    t_LSHIFTEQUAL       = r'<<='
    t_RSHIFTEQUAL       = r'>>='
    t_ANDEQUAL          = r'&='
    t_OREQUAL           = r'\|='
    t_XOREQUAL          = r'\^='
    # Increment/decrement
    t_PLUSPLUS          = r'\+\+'
    t_MINUSMINUS        = r'--'
    # ->
    t_ARROW             = r'->'
    # ?
    t_CONDOP            = r'\?'
    # Delimeters
    t_LPAREN            = r'\('
    t_RPAREN            = r'\)'
    t_LBRACKET          = r'\['
    t_RBRACKET          = r'\]'
    t_COMMA             = r','
    t_PERIOD            = r'\.'
    t_SEMI              = r';'
    t_COLON             = r':'
    t_ELLIPSIS          = r'\.\.\.'
    @TOKEN(r'\{')
    def t_LBRACE(self, t):
        return t
    @TOKEN(r'\}')
    def t_RBRACE(self, t):
        return t
    t_STRING_LITERAL    = string_literal
    @TOKEN(floating_constant)
    def t_FLOAT_CONST(self, t):
        return t
    @TOKEN(hex_floating_constant)
    def t_HEX_FLOAT_CONST(self, t):
        return t
    @TOKEN(hex_constant)
    def t_INT_CONST_HEX(self, t):
        return t
    @TOKEN(bin_constant)
    def t_INT_CONST_BIN(self, t):
        return t
    @TOKEN(octal_constant)
    def t_INT_CONST_OCT(self, t):
        return t
    @TOKEN(decimal_constant)
    def t_INT_CONST_DEC(self, t):
        return t
    @TOKEN(char_const)
    def t_CHAR_CONST(self, t):
        return t
    @TOKEN(wchar_const)
    def t_WCHAR_CONST(self, t):
        return t
    @TOKEN(wstring_literal)
    def t_WSTRING_LITERAL(self, t):
        return t
    @TOKEN(identifier)
    def t_ID(self, t):
        t.type = self.keyword_map.get(t.value, "ID")
        return t
    def t_error(self, t):
        msg = 'Illegal character %s' % repr(t)
        self._log.log(40, msg)
