# -*- coding:utf-8 -*-
from .logutil import LogUtil, registerLogger
from .guess import openTextFile
from .ply import lex
from .ply.lex import TOKEN

LOGNAME = "CTokens"
registerLogger(LOGNAME)

class CTokens(object):
    def __init__(self):
        self._log = LogUtil().logger(LOGNAME)
        self.dmyblock = ['DMYBOOL __tmp__ = DMYBLOCK("#{:0>2}");',
                         '__tmp__ = DMYBLOCK("#{:0>2}");',
                         '{DMYBOOL __tmp__ = DMYBLOCK("#{:0>2}");',
                         '__tmp__ = DMYBLOCK("#{:0>2}");}',
                        ]
    def find_tok_column(self, token):
        last_cr = self.lexer.lexdata.rfind('\n', 0, token.lexpos)
        return token.lexpos - last_cr
    def parse_file(self, filepath):
        fh = openTextFile(('cp932', 'cp936'), filepath, 'r')
        text = fh.read()
        fh.close()
        self.parse(text)
    def parse(self, text):
        self.lexer = lex.lex(object=self)
        self.lexer.input(text)
        self.tokens = list(self.lexer)
    def format(self):
        cleantokens = self._cleanTokens()
        lines = self._format(cleantokens, 0)
        return lines
    def inject(self):
        toklen = len(self.tokens)
        # 查找函数
        bracepair = []
        i = 0
        while i < toklen:
            while i < toklen and self.tokens[i].type != 'LBRACE':
                i += 1
            if i < toklen:
                k = i - 1
                while k >= 0 and self.tokens[k].type in ('SPACE', 'NEWLINE', 'COMMENT1', 'COMMENT2'):
                    k -= 1
                if k >= 0 and self.tokens[k].type == 'EQUALS':
                    # 变量初期化
                    pass
                else:
                    j = self._pair(self.tokens, i, 'RBRACE')
                    bracepair.append((i, j))
                i = j + 1
        injectlist = []
        for item in bracepair:
            blocklist = self._inject(*item)
            blocklist.insert(0, (item[0]+1, 0))
            for idx, item in enumerate(sorted(blocklist)):
                injectlist.append((item[0], self.dmyblock[item[1]].format(idx+1)))
        fh = open('out.c', 'w', encoding='utf-8')
        ipos = 0
        ilen = len(injectlist)
        for idx, item in enumerate(self.tokens):
            if ipos < ilen and idx == injectlist[ipos][0]:
                fh.write(injectlist[ipos][1])
                ipos += 1
            fh.write(item.value)
        fh.close()
    def _inject(self, startidx, stopidx):
        # return [(insert-pos, insert-text), ...]
        outlist = []
        # 查找所有可以插入DMYBLOCK的'{'和'}'
        blocklist = []
        i = self._next(self.tokens, startidx + 1)
        toklen = stopidx + 1
        while i < toklen:
            if self.tokens[i].type == 'PPHASH':
                j = i
                while j < toklen and self.tokens[j].type != 'NEWLINE':
                    j += 1
                i = j + 1
            elif self.tokens[i].type == 'IF':
                sects = []
                # if以及条件
                cond_stop = self._pair(self.tokens, i, 'RPAREN')
                sects.append((i, cond_stop))
                nextidx = self._next(self.tokens, cond_stop + 1)
                if self.tokens[nextidx].type == 'LBRACE':
                    # if:True的处理是Block
                    cond_stop = self._pair(self.tokens, nextidx, 'RBRACE')
                    sects.append((nextidx, cond_stop))
                else:
                    # if:True的处理是一条语句
                    cond_stop = self._pair(self.tokens, nextidx, 'SEMI')
                    sects.append((nextidx, cond_stop))
                nextidx = self._next(self.tokens, cond_stop + 1)
                while nextidx < toklen and self.tokens[nextidx].type == 'ELSE':
                    nextidx2 = self._next(self.tokens, nextidx + 1)
                    if self.tokens[nextidx2].type == 'IF':
                        # else if以及条件
                        cond_stop = self._pair(self.tokens, i, 'RPAREN')
                        sects.append((nextidx, cond_stop))
                        nextidx = self._next(self.tokens, cond_stop + 1)
                        if self.tokens[nextidx].type == 'LBRACE':
                            # else if:True的处理是Block
                            cond_stop = self._pair(self.tokens, nextidx, 'RBRACE')
                            sects.append((nextidx, cond_stop))
                        else:
                            # else if:True的处理是一条语句
                            cond_stop = self._pair(self.tokens, nextidx, 'SEMI')
                            sects.append((nextidx, cond_stop))
                    else:
                        # else
                        sects.append((nextidx, nextidx))
                        nextidx = self._next(self.tokens, nextidx + 1)
                        if self.tokens[nextidx].type == 'LBRACE':
                            # else的处理是Block
                            cond_stop = self._pair(self.tokens, nextidx, 'RBRACE')
                            sects.append((nextidx, cond_stop))
                        else:
                            # else的处理是一条语句
                            cond_stop = self._pair(self.tokens, nextidx, 'SEMI')
                            sects.append((nextidx, cond_stop))
                        break
                    nextidx = self._next(self.tokens, cond_stop + 1)
                j = 0
                while j < len(sects):
                    if self.tokens[sects[j+1][0]].type == 'LBRACE':
                        blocklist.append((sects[j+1][0]+1, 0))
                        blocklist.extend(self._inject(sects[j+1][0], sects[j+1][1]))
                    else:
                        blocklist.append((sects[j+1][0]+1, 2))
                        blocklist.append((sects[j+1][1], 3))
                    j += 2
                blocklist.append((sects[-1][1]+1, 1))
                i = sects[-1][1] + 1
            elif self.tokens[i].type == 'SWITCH':
                # switch以及条件
                cond_stop = self._pair(self.tokens, i, 'RPAREN')
                # switch的范围
                lbrace = self._next(self.tokens, cond_stop + 1)
                rbrace = self._pair(self.tokens, lbrace, 'RBRACE')
                # 下一个case/default的位置
                nextidx1 = self._pair(self.tokens, lbrace + 1, 'CASE')
                nextidx2 = self._pair(self.tokens, lbrace + 1, 'DEFAULT')
                nextidx = min(nextidx1, nextidx2)
                cond_stop = self._pair(self.tokens, nextidx1 + 1, 'COLON')
                while cond_stop < rbrace:
                    # case/default语句
                    blocklist.append((cond_stop + 1, 1))
                    # case/default的处理
                    nextidx1 = self._pair(self.tokens, cond_stop + 1, 'CASE')
                    nextidx2 = self._pair(self.tokens, cond_stop + 1, 'DEFAULT')
                    nextidx = min(nextidx1, nextidx2)
                    if nextidx < rbrace:
                        blocklist.extend(self._inject(cond_stop, nextidx))
                        cond_stop = self._pair(self.tokens, nextidx + 1, 'COLON')
                    else:
                        blocklist.extend(self._inject(cond_stop, rbrace))
                        cond_stop = nextidx
                blocklist.append((rbrace+1, 1))
                i = rbrace + 1
            #elif tokens[i].type in ('FOR', 'WHILE'):
                #sects = []
                ## for以及条件
                #cond_stop = self._pair(tokens, i, 'RPAREN')
                #sects.append((i, cond_stop))
                #nextidx = self._next(tokens, cond_stop + 1)
                #if tokens[nextidx].type == 'LBRACE':
                    ## for的处理是Block
                    #cond_stop = self._pair(tokens, nextidx, 'RBRACE')
                    #sects.append((nextidx, cond_stop))
                #else:
                    ## for的处理是一条语句
                    #cond_stop = self._pair(tokens, nextidx, 'SEMI')
                    #sects.append((nextidx, cond_stop))
                ## for语句
                #tmpline = self._oneline(tokens[sects[0][0]:sects[0][1]+1], indent) + ' {'
                #lines.append(tmpline)
                ## for的处理
                #if tokens[sects[1][0]].type == 'LBRACE':
                    #lines.extend(self._format(tokens[sects[1][0]+1:sects[1][1]], indent + 1))
                #else:
                    #lines.extend(self._format(tokens[sects[1][0]:sects[1][1]+1], indent + 1))
                #lines.append('\t'*indent + '}')
                #i = sects[-1][1] + 1
            #elif tokens[i].type == 'DO':
                #sects = []
                ## do
                #sects.append((i, i))
                #nextidx = self._next(tokens, i + 1)
                #if tokens[nextidx].type == 'LBRACE':
                    ## do的处理是Block
                    #cond_stop = self._pair(tokens, nextidx, 'RBRACE')
                    #sects.append((nextidx, cond_stop))
                #else:
                    ## do的处理是一条语句
                    #cond_stop = self._pair(tokens, nextidx, 'SEMI')
                    #sects.append((nextidx, cond_stop))
                ## while
                #nextidx = self._next(tokens, cond_stop + 1)
                #cond_stop = self._pair(tokens, nextidx, 'SEMI')
                #sects.append((nextidx, cond_stop))
                ## do语句
                #tmpline = self._oneline(tokens[sects[0][0]:sects[0][1]+1], indent) + ' {'
                #lines.append(tmpline)
                ## do的处理
                #if tokens[sects[1][0]].type == 'LBRACE':
                    #lines.extend(self._format(tokens[sects[1][0]+1:sects[1][1]], indent + 1))
                #else:
                    #lines.extend(self._format(tokens[sects[1][0]:sects[1][1]+1], indent + 1))
                #tmpline = '\t'*indent + '} ' + self._oneline(tokens[sects[2][0]:sects[2][1]+1], 0)
                #lines.append(tmpline)
                #i = sects[-1][1] + 1
            else:
                j = i
                while j < toklen and (self.tokens[j].type != 'SEMI' and self.tokens[j].type != 'LBRACE'):
                    j += 1
                if j >= toklen:
                    break
                if self.tokens[j].type == 'SEMI':
                    # 一行语句
                    i = j + 1
                else:
                    if self.tokens[j-1].type == 'EQUALS':
                        # 变量初期化
                        while j < toklen and self.tokens[j].type != 'SEMI':
                            j += 1
                        i = j + 1
                    else:
                        # 函数
                        nextidx = self._pair(self.tokens, j, 'RBRACE')
                        ## 函数申明
                        #lines.append(self._oneline(tokens[i:j], indent))
                        #lines.append(self._oneline(tokens[j:j+1], indent))
                        ## 函数处理
                        #lines.extend(self._format(tokens[j+1:nextidx], indent + 1))
                        #lines.append(self._oneline(tokens[nextidx:nextidx+1], indent))
                        i = nextidx + 1
            i = self._next(self.tokens, i)
        return blocklist
    def _format(self, tokens, indent):
        lines = []
        toklen = len(tokens)
        i = 0
        while i < toklen:
            if tokens[i].type == 'PPHASH':
                j = i
                while j < toklen and tokens[j].type != 'NEWLINE':
                    j += 1
                lines.append(self._oneline(tokens[i:j], indent))
                i = j + 1
            elif tokens[i].type == 'IF':
                sects = []
                # if以及条件
                cond_stop = self._pair(tokens, i, 'RPAREN')
                sects.append((i, cond_stop))
                nextidx = self._next(tokens, cond_stop + 1)
                if tokens[nextidx].type == 'LBRACE':
                    # if:True的处理是Block
                    cond_stop = self._pair(tokens, nextidx, 'RBRACE')
                    sects.append((nextidx, cond_stop))
                else:
                    # if:True的处理是一条语句
                    cond_stop = self._pair(tokens, nextidx, 'SEMI')
                    sects.append((nextidx, cond_stop))
                nextidx = self._next(tokens, cond_stop + 1)
                while nextidx < toklen and tokens[nextidx].type == 'ELSE':
                    nextidx2 = self._next(tokens, nextidx + 1)
                    if tokens[nextidx2].type == 'IF':
                        # else if以及条件
                        cond_stop = self._pair(tokens, i, 'RPAREN')
                        sects.append((nextidx, cond_stop))
                        nextidx = self._next(tokens, cond_stop + 1)
                        if tokens[nextidx].type == 'LBRACE':
                            # else if:True的处理是Block
                            cond_stop = self._pair(tokens, nextidx, 'RBRACE')
                            sects.append((nextidx, cond_stop))
                        else:
                            # else if:True的处理是一条语句
                            cond_stop = self._pair(tokens, nextidx, 'SEMI')
                            sects.append((nextidx, cond_stop))
                    else:
                        # else
                        sects.append((nextidx, nextidx))
                        nextidx = self._next(tokens, nextidx + 1)
                        if tokens[nextidx].type == 'LBRACE':
                            # else的处理是Block
                            cond_stop = self._pair(tokens, nextidx, 'RBRACE')
                            sects.append((nextidx, cond_stop))
                        else:
                            # else的处理是一条语句
                            cond_stop = self._pair(tokens, nextidx, 'SEMI')
                            sects.append((nextidx, cond_stop))
                        break
                    nextidx = self._next(tokens, cond_stop + 1)
                # if语句
                tmpline = self._oneline(tokens[sects[0][0]:sects[0][1]+1], indent) + ' {'
                lines.append(tmpline)
                # if的处理
                if tokens[sects[1][0]].type == 'LBRACE':
                    lines.extend(self._format(tokens[sects[1][0]+1:sects[1][1]], indent + 1))
                else:
                    lines.extend(self._format(tokens[sects[1][0]:sects[1][1]+1], indent + 1))
                lines.append('\t'*indent + '}')
                j = 2
                while j < len(sects):
                    # else[ if]语句
                    tmpline = ' ' + self._oneline(tokens[sects[j][0]:sects[j][1]+1], 0) + ' {'
                    lines[-1] += tmpline
                    # else[ if]的处理
                    if tokens[sects[j+1][0]].type == 'LBRACE':
                        lines.extend(self._format(tokens[sects[j+1][0]+1:sects[j+1][1]], indent + 1))
                    else:
                        lines.extend(self._format(tokens[sects[j+1][0]:sects[j+1][1]+1], indent + 1))
                    lines.append('\t'*indent + '}')
                    j += 2
                i = sects[-1][1] + 1
            elif tokens[i].type == 'SWITCH':
                # switch以及条件
                cond_stop = self._pair(tokens, i, 'RPAREN')
                tmpline = self._oneline(tokens[i:cond_stop+1], indent) + ' {'
                lines.append(tmpline)
                # switch的范围
                lbrace = self._next(tokens, cond_stop + 1)
                rbrace = self._pair(tokens, lbrace, 'RBRACE')
                # 下一个case/default的位置
                nextidx1 = self._pair(tokens, lbrace + 1, 'CASE')
                nextidx2 = self._pair(tokens, lbrace + 1, 'DEFAULT')
                nextidx = min(nextidx1, nextidx2)
                cond_stop = self._pair(tokens, nextidx1 + 1, 'COLON')
                while cond_stop < rbrace:
                    # case/default语句
                    tmpline = self._oneline(tokens[nextidx:cond_stop], indent + 1) + ':'
                    lines.append(tmpline)
                    # case/default的处理
                    nextidx1 = self._pair(tokens, cond_stop + 1, 'CASE')
                    nextidx2 = self._pair(tokens, cond_stop + 1, 'DEFAULT')
                    nextidx = min(nextidx1, nextidx2)
                    if nextidx < rbrace:
                        lines.extend(self._format(tokens[cond_stop+1:nextidx], indent + 2))
                        cond_stop = self._pair(tokens, nextidx + 1, 'COLON')
                    else:
                        lines.extend(self._format(tokens[cond_stop+1:rbrace-1], indent + 2))
                        cond_stop = nextidx
                tmpline = '\t'*indent + '}'
                lines.append(tmpline)
                i = rbrace + 1
            elif tokens[i].type in ('FOR', 'WHILE'):
                sects = []
                # for以及条件
                cond_stop = self._pair(tokens, i, 'RPAREN')
                sects.append((i, cond_stop))
                nextidx = self._next(tokens, cond_stop + 1)
                if tokens[nextidx].type == 'LBRACE':
                    # for的处理是Block
                    cond_stop = self._pair(tokens, nextidx, 'RBRACE')
                    sects.append((nextidx, cond_stop))
                else:
                    # for的处理是一条语句
                    cond_stop = self._pair(tokens, nextidx, 'SEMI')
                    sects.append((nextidx, cond_stop))
                # for语句
                tmpline = self._oneline(tokens[sects[0][0]:sects[0][1]+1], indent) + ' {'
                lines.append(tmpline)
                # for的处理
                if tokens[sects[1][0]].type == 'LBRACE':
                    lines.extend(self._format(tokens[sects[1][0]+1:sects[1][1]], indent + 1))
                else:
                    lines.extend(self._format(tokens[sects[1][0]:sects[1][1]+1], indent + 1))
                lines.append('\t'*indent + '}')
                i = sects[-1][1] + 1
            elif tokens[i].type == 'DO':
                sects = []
                # do
                sects.append((i, i))
                nextidx = self._next(tokens, i + 1)
                if tokens[nextidx].type == 'LBRACE':
                    # do的处理是Block
                    cond_stop = self._pair(tokens, nextidx, 'RBRACE')
                    sects.append((nextidx, cond_stop))
                else:
                    # do的处理是一条语句
                    cond_stop = self._pair(tokens, nextidx, 'SEMI')
                    sects.append((nextidx, cond_stop))
                # while
                nextidx = self._next(tokens, cond_stop + 1)
                cond_stop = self._pair(tokens, nextidx, 'SEMI')
                sects.append((nextidx, cond_stop))
                # do语句
                tmpline = self._oneline(tokens[sects[0][0]:sects[0][1]+1], indent) + ' {'
                lines.append(tmpline)
                # do的处理
                if tokens[sects[1][0]].type == 'LBRACE':
                    lines.extend(self._format(tokens[sects[1][0]+1:sects[1][1]], indent + 1))
                else:
                    lines.extend(self._format(tokens[sects[1][0]:sects[1][1]+1], indent + 1))
                tmpline = '\t'*indent + '} ' + self._oneline(tokens[sects[2][0]:sects[2][1]+1], 0)
                lines.append(tmpline)
                i = sects[-1][1] + 1
            elif tokens[i].type == 'NEWLINE':
                i += 1
            #elif tokens[i].type == 'RBRACE':
                ## 不应该有多余的'}'
                #i += 1
            else:
                j = i
                while j < toklen and (tokens[j].type != 'SEMI' and tokens[j].type != 'LBRACE'):
                    j += 1
                if j >= toklen:
                    break
                if tokens[j].type == 'SEMI':
                    # 一行语句
                    lines.append(self._oneline(tokens[i:j+1], indent))
                    i = j + 1
                else:
                    if tokens[j-1].type == 'EQUALS':
                        # 变量初期化
                        while j < toklen and tokens[j].type != 'SEMI':
                            j += 1
                        lines.append(self._oneline(tokens[i:j+1], indent))
                        i = j + 1
                    else:
                        # 函数
                        nextidx = self._pair(tokens, j, 'RBRACE')
                        # 函数申明
                        lines.append(self._oneline(tokens[i:j], indent))
                        lines.append(self._oneline(tokens[j:j+1], indent))
                        # 函数处理
                        lines.extend(self._format(tokens[j+1:nextidx], indent + 1))
                        lines.append(self._oneline(tokens[nextidx:nextidx+1], indent))
                        i = nextidx + 1
        return lines
    def _next(self, tokens, startidx):
        toklen = len(tokens)
        j = startidx
        while j < toklen and tokens[j].type in ('NEWLINE', 'SPACE', 'COMMENT1', 'COMMENT2'):
            j += 1
        return j
    def _pair(self, tokens, startidx, findtype):
        toklen = len(tokens)
        j = startidx
        paren = [0, 0, 0]
        # 查找条件结束位置
        while j < toklen:
            if tokens[j].type == 'LPAREN':
                paren[0] += 1
            elif tokens[j].type == 'RPAREN':
                paren[0] -= 1
            elif tokens[j].type == 'LBRACKET':
                paren[1] += 1
            elif tokens[j].type == 'RBRACKET':
                paren[1] -= 1
            elif tokens[j].type == 'LBRACE':
                paren[2] += 1
            elif tokens[j].type == 'RBRACE':
                paren[2] -= 1
            if not any(paren) and tokens[j].type == findtype:
                # 括号匹配，且找到目标种别时退出
                break
            j += 1
        return j
    def _oneline(self, tokens, indent):
        tmpline = '\t' * indent
        subtokens = [x for x in tokens if x.type!='NEWLINE']
        if len(subtokens) > 0 and subtokens[0].type == 'PPHASH':
            # 预处理语句：'#'与预处理指令之间不加空格
            tmpline += '#'
            subtokens = subtokens[1:]
        for idx,item in enumerate(subtokens):
            if item.type in ('COMMA', 'SEMI'):
                if idx > 0:
                    # ',',';'前面不加空格
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
                    if item.type in ('ID', 'INT_CONST_DEC', 'INT_CONST_OCT', 'INT_CONST_HEX', 'INT_CONST_BIN', 'FLOAT_CONST'):
                        # ')'后面是标识符或常数时，中间不加空格
                        tmpline = tmpline[:-1] + item.value + ' '
                    else:
                        tmpline += item.value + ' '
                else:
                    tmpline += item.value + ' '
        return tmpline[:-1]
    def _cleanTokens(self):
        outlist = []
        for tok in self.tokens:
            if tok.type in ('COMMENT1', 'COMMENT2', 'SPANLINE', 'SPACE'):
                pass
            else:
                if tok.type == 'NEWLINE':
                    if len(outlist) > 0 and outlist[-1].type != 'NEWLINE':
                        outlist.append(tok)
                else:
                    outlist.append(tok)
        return outlist

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
