# -*- coding:utf-8 -*-
import os
import re
import collections
import uuid
import configparser
import subprocess
from collectscript import logutil, tagparser, guess

LOGNAME = 'AstahInputCode'
LOGNAME2 = 'AstahMidCode'
LOGNAME3 = 'AstahFuncPos'
logutil.registerLogger(LOGNAME)
logutil.registerLogger(LOGNAME2)
logutil.registerLogger(LOGNAME3)
# 本文件3个class间关系的说明:
# 1. 使用[cscope -Rbcu]生成tag文件
# 2. 生成对象aic = AstahInputCode(tag文件所在路径)
# 3. 抽出并整理代码，然后返回整理后文件名列表flist = aic.outputFile(函数名, 输出文件名)
#    当存在同名函数时，len(flist)>1，文件名为输出文件名加上序号
#    当不存在同名函数时，len(flist)==1，文件名为输出文件名
# 4. 生成对象amc = AstahMidCode()
# 5. 输出中间文件并取得中间文件的文件名midfile = amc.fmtCode(flist[i])
#    中间文件可用于手动修改普通代码行的分组
# 6. 生成对象afp = AstahFuncPos()
# 7. 输出xml文件afp.analyze(midfile)
#    文件名为函数ID（可改成函数名）
class AstahInputCode(object):
    # 输出调整后的代码
    PAT_OPENBRACE = re.compile(r'\s*\{$')
    PAT_CLOSEBRACE = re.compile(r'^\s*\}$')
    def __init__(self, rootdir):
        self._log = logutil.LogUtil().logger(LOGNAME)
        self._root = rootdir
        self._parser = tagparser.CscopeParser(os.path.join(self._root,'cscope.out'))
        self._fmt = tagparser.FormatSource()
    def outputFile(self, funcname, outfile):
        # 输出代码情报到文件
        outlist = []
        funclist = self._getFuncInfo(funcname)
        funccnt = len(funclist)
        if funccnt > 1:
            fname,fext = os.path.splitext(outfile)
            for curidx in range(len(funclist)):
                curoutfile = '{}_{:0>2}{}'.format(fname,curidx+1,fext)
                fh = open(curoutfile, 'w', encoding='utf-8')
                fh.write(funclist[curidx]['funcno']+'\n')
                fh.write(funclist[curidx]['funcname'])
                fh.write('\n'.join(self._stripBrace(funclist[curidx]['code'])))
                fh.close()
                outlist.append(os.path.abspath(curoutfile))
        elif funccnt > 0:
            curidx = 0
            curoutfile = outfile
            fh = open(curoutfile, 'w', encoding='utf-8')
            fh.write(funclist[curidx]['funcno']+'\n')
            fh.write(funclist[curidx]['funcname'])
            fh.write('\n'.join(self._stripBrace(funclist[curidx]['code'])))
            fh.close()
            outlist.append(os.path.abspath(curoutfile))
        else:
            pass
        return outlist
    def _getFuncInfo(self, funcname):
        outlist = []
        info = self._parser.getFuncInfo(funcname)
        for func in info:
            funcname = func.name
            funcno = func.extra.get('funcno','')
            jpname = func.extra.get('jpname','')
            subfuncs = list(self._parser.getFuncCall_asdict(func).keys())
            fh = guess.openTextFile(('cp932','cp936'), os.path.join(self._root,func.relpath), 'r')
            lines = fh.readlines()
            fh.close()
            # 代码格式整理
            codes = self._fmt.clean('\n'.join(lines[int(func.startline)-1:int(func.stopline)]))
            outlist.append({'label': funcname,
                            'funcno': funcno,
                            'subfunc': subfuncs,
                            'funcname': jpname,
                            'code': codes})
        return outlist
    def _stripBrace(self, codes):
        # 删除{}
        lines = []
        for line in codes.splitlines():
            line = self.PAT_OPENBRACE.sub('',line)
            line = self.PAT_CLOSEBRACE.sub('',line)
            if line != '':
                lines.append(line)
        idx = lines[0].find('(')
        lines[0] = '%0A' + lines[0][lines[0].rfind(' ', 0, idx)+1:]
        return lines

class AstahMidCode(object):
    def __init__(self):
        self._log = logutil.LogUtil().logger(LOGNAME2)
    # 输出中间文件（可以修改中间文件来调整代码合并分组）
    def fmtCode(self, infile, outfile=None):
        # 输出代码情报到中间文件
        fh = open(infile, 'r', encoding='utf-8')
        lines = fh.readlines()
        fh.close()
        if not outfile:
            outfile = os.path.splitext(infile)[0]+'_mid.txt'
        fh = open(outfile, 'w', encoding='utf-8')
        fh.write(''.join(self._groupCode(lines)))
        fh.close()
        return os.path.abspath(outfile)
    def _groupCode(self, lines):
        # 调整输出格式：类型#序号#代码
        # 当相邻行的[类型#序号]一致时合并
        TYPE_START = 1
        TYPE_STATEMENT = 2
        TYPE_FUNCCALL = 3
        TYPE_COND = 4
        TYPE_LOOP = 5
        pat_func = re.compile(r'[a-zA-Z_][a-zA-Z0-9_]*\(')
        pat_cond = re.compile(r'\b(if|else)\b')
        pat_loop = re.compile(r'\b(for|while)\b')
        lines[1] = '{}#000#'.format(TYPE_START) + lines[1]
        lasttab = -1
        lastno = 1
        for idx in range(2, len(lines)):
            curtab = lines[idx].rfind('\t') + 1
            if pat_cond.search(lines[idx]):
                curtype = TYPE_COND
            elif pat_loop.search(lines[idx]):
                curtype = TYPE_LOOP
            elif pat_func.search(lines[idx]):
                lines[idx] = lines[idx].replace(';', '')
                curtype = TYPE_FUNCCALL
            else:
                lines[idx] = lines[idx].replace(';', '')
                curtype = TYPE_STATEMENT
            # 函数调用不合并
            if curtab != lasttab:
                lastno = 0
            if curtype == TYPE_FUNCCALL:
                lastno += 1
            else:
                lastno = 0
            lines[idx] = '{}#{}#'.format(curtype, curtab*100+lastno) + lines[idx]
            lasttab = curtab
        return lines

class AstahFuncPos(object):
    # FlowNode.nodeno   控件index
    # FlowNode.code     控件文字
    # FlowNode.nodetype 控件类型
    # FlowNode.x        控件坐标x
    # FlowNode.y        控件坐标y
    #                   控件坐标：左上第一个控件为(0,0)，右下方向为正方向，同一列紧接的下一个控件为(0,1)
    # FlowNode.nextnode 后续控件index的数组
    # FlowNode.drift    每一条分支的最大宽度（到第几列的第几层连接线），仅对分支类型控件有效
    FlowNode = collections.namedtuple('FlowNode', ['nodeno', 'code', 'nodetype', 'x', 'y', 'nextnode', 'drift'])
    PAT_SPLITCODE = re.compile('^(?P<prefix>\d+#\d+)#(?P<code>.*)$')
    PAT_FUNC = re.compile(r'[a-zA-Z_][a-zA-Z0-9_]*\(')
    COND_DOWN = 1 # [else if]分支块相对于前一个[else if]或者[if]的纵向增量，0则水平，1则是向右下的斜线
    CODESEP = '%0A' # 代码合并时，代码各行之间的分隔字符串
    #DEFAULT_SIZE保存各个nodetype的默认大小，key是nodetype名，value是宽和高
    DEFAULT_SIZE = {'start'      : (320, 101),
                    'end'        : (320, 101),
                    'normal'     : (320, 101),
                    'subroutine' : (320, 101),
                    'if'         : (460, 101),
                    'elif'       : (460, 101),
                    'loop start' : (320, 101),
                    'loop end'   : (320, 101),
                    }
    #DEFAULT_TOPCENTER保存第一个控件的上边中点
    DEFAULT_TOPCENTER = (300, 50)
    #DEFAULT_GRID保存区块大小，正常情况下一个区块保存一个控件，这样可以保证各个控件的左上角坐标均匀排列
    DEFAULT_GRID = (600, 200)
    #DEFAULT_HALFLINE保存else分支回到主线时，最后一段折线的高
    DEFAULT_HALFLINE = 50
    #DEFAULT_MINGAP保存两行控件之间的最小间距（必须大于DEFAULT_HALFLINE）
    DEFAULT_MINGAP = 60
    def __init__(self, settingdict=None):
        self._log = logutil.LogUtil().logger(LOGNAME3)
        if settingdict:
            settingdict=dict(settingdict)
            pat = re.compile(r'(?P<width>\d+),(?P<height>\d+)')
            for key in self.DEFAULT_SIZE.keys():
                tmpvalue = settingdict.get(key, '')
                ret = pat.search(tmpvalue)
                if ret:
                    newwidth = int(ret.group('width'))
                    newheight = int(ret.group('height'))
                    if newwidth != self.DEFAULT_SIZE[key][0] or newheight != self.DEFAULT_SIZE[key][1]:
                        self.DEFAULT_SIZE[key] = (newwidth, newheight)
            tmpvalue = settingdict.get('grid','')
            ret = pat.search(tmpvalue)
            if ret:
                newwidth = int(ret.group('width'))
                newheight = int(ret.group('height'))
                if newwidth != self.DEFAULT_GRID[0] or newheight != self.DEFAULT_GRID[1]:
                    self.DEFAULT_GRID = (newwidth, newheight)
            self.DEFAULT_MINGAP = int(settingdict.get('mingap',self.DEFAULT_MINGAP))
            self.DEFAULT_HALFLINE = int(settingdict.get('arrowheight',self.DEFAULT_HALFLINE))
        self._loadTemplate()
    def analyze(self, infile, outpath='.', outfile=None):
        self._log.log(20, infile)
        # 读取中间文件并合并普通代码行成一个代码段
        codes = self._getCodes(infile)
        # 分析各个代码段的控件坐标
        posinfo,y,x = self._getPos(codes[1:]) # posinfo是FlowNode的数组
        for item in posinfo:
            self._log.log(10, str(item))
        # 调整过高的代码段
        posinfo = self._spanBlock(posinfo)
        # 计算两列之间连接线的层数
        self._calcLinePos(posinfo)
        # 计算物理坐标并输出xml文件
        self._writeXML(codes[0], posinfo, outpath, outfile)
    def _guessBlockCount(self, flownode):
        # 计算当前控件需要的区块数
        width, height = self._guessWidgetSize(flownode)
        cnt = height // self.DEFAULT_GRID[1]
        while self.DEFAULT_GRID[1] * cnt - self.DEFAULT_MINGAP < height:
            cnt += 1
        return cnt
    def _guessWidgetSize(self, flownode):
        # 估算控件大小
        width, height = self.DEFAULT_SIZE[flownode.nodetype]
        if flownode.nodetype in ('normal', 'subroutine'):
            linecnt = flownode.code.count('%0A') + 1
            if linecnt * 14 + 3 > height:
                height = linecnt * 14 + 3
        elif flownode.nodetype in ('if', 'elif'):
            charlen = len(flownode.code) - flownode.code.count('%') * 2
            linecnt = (charlen + 51) // 52
            if linecnt * 14 + 3 > height:
                height = linecnt * 14 + 3
        return width, height
    def _spanBlock(self, posinfo):
        # 一行中最高的控件的高度 ≤ 区块个数 × 区块高度 － 最后一段折线的高 × 1.2
        adjdict = {}
        # 求每一行需要的最大区块个数
        for item in posinfo:
            blockcnt = self._guessBlockCount(item)
            # 判断当前控件与next的控件之间的间隔
            for nn in item.nextnode:
                if nn > 0:
                    tmprowspan = posinfo[nn].y - item.y
                    if tmprowspan <= blockcnt:
                        # 间隔不足
                        break
            else:
                # 间隔足够，不需要调整
                blockcnt = 1
            if blockcnt > adjdict.setdefault(item.y, 1):
                adjdict[item.y] = blockcnt
        # 求每一行纵坐标需要增加的量
        accumlate_span = 0
        for key in sorted(adjdict.keys()):
            tmp = adjdict[key]
            adjdict[key] = accumlate_span
            accumlate_span += tmp - 1
        # 变更纵坐标
        for idx,item in enumerate(posinfo):
            if adjdict[item.y] > 0:
                posinfo[idx] = item._replace(y=item.y+adjdict[item.y])
        return posinfo
    def _calcPointPos(self, col, row, drift):
        x = col * self.DEFAULT_GRID[0] + self.DEFAULT_TOPCENTER[0]
        y = row * self.DEFAULT_GRID[1] + self.DEFAULT_TOPCENTER[1]
        if drift > 0:
            pad = 10
            x += (self.DEFAULT_GRID[0] - self.colspan) / 2
            x += (self.colspan - pad * 2) * drift / (self.drift.setdefault(col, 0) + 1) + pad
        return x,y
    def _calcLinePos(self, posinfo):
        # 计算连接线坐标情报
        self.colspan = min([self.DEFAULT_GRID[0] - item[0] for item in self.DEFAULT_SIZE.values()])
        self.drift = {}
        for idx,item in enumerate(posinfo):
            self.drift.setdefault(item.x, 0)
            if len(item.drift) > 0:
                col = item.drift[0]
                drift = item.drift[1]
                if self.drift.setdefault(col,0) < drift:
                    self.drift[col] = drift
                col = item.drift[2]
                drift = item.drift[3]
                if self.drift.setdefault(col,0) < drift:
                    self.drift[col] = drift
    def _formathtmlstr(self, instr):
        output = instr
        output = output.replace('%','%25')
        output = output.replace('~','%7E')
        output = output.replace('!','%21')
        output = output.replace('&','%26')
        output = output.replace('|','%7C')
        output = output.replace('#','%23')
        output = output.replace('+','%2B')
        output = output.replace('/','%2F')
        output = output.replace('>','%3E')
        output = output.replace('<','%3C')
        output = output.replace('(','%28')
        output = output.replace(')','%29')
        output = output.replace('[','%5B')
        output = output.replace(']','%5D')
        output = output.replace(',','%2C')
        output = output.replace(';','%3B')
        output = output.replace("'",'%27')
        output = output.replace(';','%3B')
        output = output.replace('"','%22')
        output = output.replace('?','%3F')
        output = output.replace('%250A','%0A')
        output = output.replace(' ','+')
        return output
    def _loadTemplate(self, basedir='tpl'):
        # 读取模板文件
        self.tpl_whole = []
        self.tpl_subvertex = {}
        self.tpl_stereotype = {}
        self.tpl_presentations = {}
        for i in range(5):
            fh = open(os.path.join(basedir, 'tpl_whole{}.txt'.format(i)), 'r', encoding='utf-8')
            self.tpl_whole.append(fh.read())
            fh.close()
        for finfo in (('start','start'),
                      ('end','end'),
                      ('normal','normal'),
                      ('subroutine','subroutine'),
                      ('if','if'),
                      ('elif','elif'),
                      ('loop start','loopstart'),
                      ('loop end','loopend'),
                      ):
            fpath = os.path.join(basedir, 'tpl_subvertex_{}.txt'.format(finfo[1]))
            if os.path.isfile(fpath):
                fh = open(fpath, 'r', encoding='utf-8')
                self.tpl_subvertex[finfo[0]] = fh.read()
                fh.close()
            fpath = os.path.join(basedir, 'tpl_stereotype_{}.txt'.format(finfo[1]))
            if os.path.isfile(fpath):
                fh = open(fpath, 'r', encoding='utf-8')
                self.tpl_stereotype[finfo[0]] = fh.read()
                fh.close()
            fpath = os.path.join(basedir, 'tpl_presentations_{}.txt'.format(finfo[1]))
            if os.path.isfile(fpath):
                fh = open(fpath, 'r', encoding='utf-8')
                self.tpl_presentations[finfo[0]] = fh.read()
                fh.close()
        fh = open(os.path.join(basedir, 'tpl_text_presentation.txt'.format(i)), 'r', encoding='utf-8')
        self.tpl_text_presentation = fh.read()
        fh.close()
        self.tpl_line_transition = ''
        self.tpl_line_presentation = []
        fh = open(os.path.join(basedir, 'tpl_line_transition.txt'.format(i)), 'r', encoding='utf-8')
        self.tpl_line_transition = fh.read()
        fh.close()
        for i in range(4):
            fh = open(os.path.join(basedir, 'tpl_line_presentation{}.txt'.format(i)), 'r', encoding='utf-8')
            self.tpl_line_presentation.append(fh.read())
            fh.close()
        fh = open(os.path.join(basedir, 'tpl_line_incoming.txt'.format(i)), 'r', encoding='utf-8')
        tmp = fh.read()
        self.tpl_line_incoming = tmp.splitlines()
        fh.close()
        fh = open(os.path.join(basedir, 'tpl_line_outgoing.txt'.format(i)), 'r', encoding='utf-8')
        tmp = fh.read()
        self.tpl_line_outgoing = tmp.splitlines()
        fh.close()
        fh = open(os.path.join(basedir, 'tpl_line_client.txt'.format(i)), 'r', encoding='utf-8')
        tmp = fh.read()
        self.tpl_line_client = tmp.splitlines()
        fh.close()
    def _writeXML(self, funcid, posinfo, outpath='.', outfile=None):
        baseuuid    = uuid.uuid4().hex
        # 文件ID
        root_id     = '7f-'+baseuuid
        # FlowChartID
        module_id0  = 'bn-'+baseuuid
        module_id1  = 'bo-'+baseuuid
        module_id2  = 'bm-'+baseuuid
        module_id3  = 'bp-'+baseuuid
        module_name = funcid
        # 控件ID
        format_id0  = '{:0>3}-00000000000000000000000000000000'
        format_id1  = '{:0>3}-00000000000000000000000000000001'
        format_id2  = '{:0>3}-00000000000000000000000000000002'
        format_id3  = '{:0>3}-00000000000000000000000000000003'
        # 连接线ID
        format_id4  = '{:0>3}-00000000000000000000000000000004'
        format_id5  = '{:0>3}-00000000000000000000000000000005'
        format_id6  = '{:0>3}-00000000000000000000000000000006'
        # 文本框ID
        format_id7  = '{:0>3}-00000000000000000000000000000007'
        # 最大深度（为了正确处理控件重合问题，要求所有控件深度不同，深度小的在上面）
        depth = 2147483636
        # 控件情报设置
        xmlinfo = []
        for idx,item in enumerate(posinfo):
            # 控件大小
            width, height = self._guessWidgetSize(item)
            # 控件位置
            x, y = self._calcPointPos(item.x, item.y, 0)
            x -= width/2
            # 控件情报
            xmlinfo.append({'info':item,
                            'depth':depth,
                            'width':width,
                            'height':height,
                            'x':x,
                            'y':y,
                            'id0':format_id0.format(idx),
                            'id1':format_id1.format(idx),
                            'id2':format_id2.format(idx),
                            'id3':format_id3.format(idx),
                            'label':self._formathtmlstr(item.code),
                            })
            if item.nodetype in ('start', 'end'):
                # 连接线情报设置处理时，需要每个控件的最后一个id
                # start/end空间只有id0~id2这3个id有用
                xmlinfo[-1]['id3'] = xmlinfo[-1]['id2']
            depth -= 1
            if item.nodetype in self.tpl_subvertex:
                testline = self.tpl_subvertex[item.nodetype].format(module0 = module_id0,
                                                                    module1 = module_id1,
                                                                    module2 = module_id2,
                                                                    module3 = module_id3,
                                                                    **xmlinfo[-1])
                xmlinfo[-1]['txt1'] = testline
            if item.nodetype in self.tpl_stereotype:
                testline = self.tpl_stereotype[item.nodetype].format(module0 = module_id0,
                                                                     module1 = module_id1,
                                                                     module2 = module_id2,
                                                                     module3 = module_id3,
                                                                     **xmlinfo[-1])
                xmlinfo[-1]['txt2'] = testline
            if item.nodetype in self.tpl_presentations:
                testline = self.tpl_presentations[item.nodetype].format(module0 = module_id0,
                                                                        module1 = module_id1,
                                                                        module2 = module_id2,
                                                                        module3 = module_id3,
                                                                        **xmlinfo[-1])
                xmlinfo[-1]['txt3'] = testline
        # 连接线和文本框情报设置
        links                 = [] # 连接线情报数组
        links_in              = {} # key:目标控件idx，value:(源控件idx,连接线情报idx)
        links_out             = {} # key:源控件idx，value:(目标控件idx,连接线情报idx)
        linkcnt               = 0  # 连接线数量
        outline_transitions   = '' # Transition部分文本
        outline_presentations = '' # TransitionPresentation部分文本
        txtcnt                = 0  # 文本框数量
        text_presentations    = '' # TextPresentation部分文本
        for idx,item in enumerate(xmlinfo):
            for idx2, nn in enumerate(item['info'].nextnode):
                if nn >= 0:  # end类型的控件没有nextnode，程序会设成[-1]
                    links.append({'id0':format_id4.format(linkcnt),
                                  'id1':format_id5.format(linkcnt),
                                  'id2':format_id6.format(linkcnt),
                                  'node1_id0':item['id0'],
                                  'node1_id3':item['id3'],
                                  'node2_id0':xmlinfo[nn]['id0'],
                                  'node2_id3':xmlinfo[nn]['id3'],
                                  'depth':depth,
                                  'pointx':[],
                                  'pointy':[],
                                  })
                    depth -= 1
                    if idx2 == 0:
                        # 向下的连接线
                        startx = item['x']+item['width']/2
                        starty = item['y']+item['height']
                        if item['info'].x == xmlinfo[nn]['info'].x:
                            # 直线
                            pass
                        else:
                            # 折线 3段
                            # 当前控件下方的点
                            links[-1]['pointx'].append(item["x"]+item["width"]/2)
                            links[-1]['pointy'].append(xmlinfo[nn]["y"]-self.DEFAULT_HALFLINE)
                            # 目标控件上方的点
                            links[-1]['pointx'].append(xmlinfo[nn]["x"]+xmlinfo[nn]["width"]/2)
                            links[-1]['pointy'].append(xmlinfo[nn]["y"]-self.DEFAULT_HALFLINE)
                        if len(item['info'].nextnode) > 1:
                            # 插入True分支文字
                            textid = format_id7.format(txtcnt)
                            text_presentations += self.tpl_text_presentation.format(id0=textid,
                                                                                    label="TRUE",
                                                                                    pointx=startx,
                                                                                    pointy=starty,
                                                                                    depth=depth,
                                                                                    module2=module_id2)
                            depth -= 1
                            txtcnt += 1
                    else:
                        # 向右的连接线
                        startx = item['x']+item['width']
                        starty = item['y']+item['height']/2
                        if item['info'].x < xmlinfo[nn]['info'].x:
                            # 折线 2段
                            # 当前控件右方、目标控件上方的点
                            links[-1]['pointx'].append(xmlinfo[nn]["x"]+xmlinfo[nn]["width"]/2)
                            links[-1]['pointy'].append(item["y"]+item["height"]/2)
                        else:
                            # 折线 4段
                            x, y = self._calcPointPos(item['info'].drift[2], item['info'].y, item['info'].drift[3])
                            # 当前控件右方的点
                            links[-1]['pointx'].append(x)
                            links[-1]['pointy'].append(item["y"]+item["height"]/2)
                            # 前一点下方的点
                            links[-1]['pointx'].append(x)
                            links[-1]['pointy'].append(xmlinfo[nn]["y"]-self.DEFAULT_HALFLINE)
                            # 目标控件上方的点
                            links[-1]['pointx'].append(xmlinfo[nn]["x"]+xmlinfo[nn]["width"]/2)
                            links[-1]['pointy'].append(xmlinfo[nn]["y"]-self.DEFAULT_HALFLINE)
                        # 插入False分支文字
                        textid = format_id7.format(txtcnt)
                        text_presentations += self.tpl_text_presentation.format(id0=textid,
                                                                                label="FALSE",
                                                                                pointx=startx,
                                                                                pointy=starty - 25,
                                                                                depth=depth,
                                                                                module2=module_id2)
                        depth -= 1
                        txtcnt += 1
                    if idx not in links_out:
                        links_out[idx] = []
                    if nn not in links_in:
                        links_in[nn] = []
                    links_out[idx].append((nn, linkcnt))
                    links_in[nn].append((idx, linkcnt))
                    linkcnt += 1
                    outline_transitions += self.tpl_line_transition.format(module0 = module_id0,
                                                                           **links[-1])
                    outline_presentations += self.tpl_line_presentation[0].format(module0 = module_id0,
                                                                                  module1 = module_id1,
                                                                                  module2 = module_id2,
                                                                                  module3 = module_id3,
                                                                                  startx = startx,
                                                                                  starty = starty,
                                                                                  **links[-1])
                    tmpline = ''
                    if len(links[-1]['pointx']) > 0:
                        for idx3 in range(len(links[-1]['pointx'])):
                            tmpline += self.tpl_line_presentation[3].format(pointx=links[-1]['pointx'][idx3],
                                                                            pointy=links[-1]['pointy'][idx3])
                    outline_presentations += tmpline
                    outline_presentations += self.tpl_line_presentation[1]
                    outline_presentations += tmpline
                    outline_presentations += self.tpl_line_presentation[2]
        # 连接线情报插入各个控件
        for idx,item in enumerate(xmlinfo):
            inlink = links_in.get(idx, [])
            outlink = links_out.get(idx, [])
            outlines_subvertex = []     # 插入subvertex中的文字
            outlines_presentations = [] # 插入presentations中的文字
            if len(inlink) > 0:
                outlines_subvertex.append(self.tpl_line_incoming[0])
                for linkitem in inlink:
                    outlines_subvertex.append(self.tpl_line_incoming[1].format(**links[linkitem[1]]))
                    outlines_presentations.append(self.tpl_line_client[1].format(**links[linkitem[1]]))
                outlines_subvertex.append(self.tpl_line_incoming[2])
            if len(outlink) > 0:
                outlines_subvertex.append(self.tpl_line_outgoing[0])
                for linkitem in outlink:
                    outlines_subvertex.append(self.tpl_line_outgoing[1].format(**links[linkitem[1]]))
                    outlines_presentations.append(self.tpl_line_client[1].format(**links[linkitem[1]]))
                outlines_subvertex.append(self.tpl_line_outgoing[2])
            parts = item['txt1'].splitlines()
            for tmpline in outlines_subvertex:
                parts.insert(-1, tmpline)
            item['txt1'] = '\n'.join(parts) + '\n'
            if len(outlines_presentations) > 0:
                parts = item['txt3'].splitlines()
                parts.insert(-1, self.tpl_line_client[0])
                for tmpline in outlines_presentations:
                    parts.insert(-1, tmpline)
                parts.insert(-1, self.tpl_line_client[2])
                item['txt3'] = '\n'.join(parts) + '\n'
        # 输出xml文件
        if outfile:
            fh = open(os.path.join(outpath, os.path.splitext(outfile)[0]+'.xml'), 'w', encoding='utf-8')
        else:
            fh = open(os.path.join(outpath, funcid+'.xml'), 'w', encoding='utf-8')
        fh.write(self.tpl_whole[0].format(baseuuid,module_name))
        for item in xmlinfo:
            if item["info"].nodetype in self.tpl_subvertex:
                fh.write(item['txt1'])
        fh.write(self.tpl_whole[1].format(baseuuid,module_name))
        if outline_transitions != '':
            fh.write('          <UML:StateMachine.transitions>\n')
            fh.write(outline_transitions)
            fh.write('          </UML:StateMachine.transitions>\n')
        fh.write(self.tpl_whole[2].format(baseuuid,module_name))
        for item in xmlinfo:
            if item["info"].nodetype in self.tpl_stereotype:
                fh.write(item['txt2'])
        fh.write(self.tpl_whole[3].format(baseuuid,module_name))
        for item in xmlinfo:
            if item["info"].nodetype in self.tpl_presentations:
                fh.write(item['txt3'])
        fh.write(text_presentations)
        fh.write(outline_presentations)
        fh.write(self.tpl_whole[4].format(baseuuid,module_name))
        fh.close()
    def _getCodes(self, fname):
        # 读取中间文件
        fh = open(fname, 'r', encoding='utf-8')
        lines = fh.readlines()
        fh.close()
        outline = [lines[0].rstrip(),]
        lastprefix = ''
        for line in lines[1:]:
            ret = self.PAT_SPLITCODE.search(line)
            if ret:
                prefix = ret.group('prefix')
                code = ret.group('code')
                if prefix == lastprefix:
                    code = code.lstrip('\t')
                    outline[-1] = outline[-1] + self.CODESEP + code
                else:
                    outline.append(code)
                lastprefix = prefix
        return outline
    def _getPos(self, codes):
        # 计算代码的坐标以及连线
        posinfo,y,x,d = self._setxy(codes[1:], 1, 0, 1)
        # 插入开始Block
        posinfo.insert(0, self.FlowNode(nodeno=0,code=codes[0],nodetype='start',x=0, y=0, nextnode=[1], drift=[]))
        # 插入结束Block
        nodecnt = len(posinfo)
        for nodei in range(nodecnt):
            for nodej in range(len(posinfo[nodei].nextnode)):
                if posinfo[nodei].nextnode[nodej] == -1:
                    posinfo[nodei].nextnode[nodej] = nodecnt
        posinfo.append(self.FlowNode(nodeno=nodecnt,code='End',nodetype='end',x=0, y=y, nextnode=[-1], drift=[]))
        return posinfo, y+1, x
    def _setxy(self, codes, startrow, startcol, nodeidx):
        if len(codes) > 0:
            self._log.log(10, 'CodeLen={0}, StartRow={1}, StartCol={2}, NodeIdx={3}, Code[0]=[{4}]'.format(len(codes), startrow, startcol, nodeidx, codes[0].strip()))
        else:
            self._log.log(10, 'CodeLen={0}, StartRow={1}, StartCol={2}, NodeIdx={3}, Code[0]=[]'.format(len(codes), startrow, startcol, nodeidx))
        poslist = []
        curnodeidx = nodeidx
        maxrow = startrow
        maxcol = startcol
        maxdrift = 0
        idx = 0
        maxidx = len(codes)
        pat = re.compile(r'^else\b')
        while idx < maxidx:
            line = codes[idx]
            tabs = line.rfind('\t') + 1
            line = line[tabs:]
            if line.startswith('if '):
                # if分块
                sects = []
                sectidx = idx
                tmpidx = idx + 1
                while tmpidx < len(codes):
                    tmpline = codes[tmpidx]
                    tmptabs = tmpline.rfind('\t') + 1
                    if tmptabs == tabs:
                        if pat.search(tmpline[tmptabs:]):
                            sects.append((sectidx, tmpidx - 1))
                            sectidx = tmpidx
                        else:
                            break
                    elif tmptabs < tabs:
                        break
                    tmpidx += 1
                sects.append((sectidx, tmpidx - 1))
                self._log.log(10, 'if sections:{0}'.format(str(sects)))
                for nodei in range(curnodeidx-nodeidx):
                    for nodej in range(len(poslist[nodei].nextnode)):
                        if poslist[nodei].nextnode[nodej] == -1:
                            poslist[nodei].nextnode[nodej] = curnodeidx
                lastcondidx = -1
                # if块
                poslist.append(self.FlowNode(nodeno=curnodeidx,code=line,nodetype='if',x=startcol, y=startrow, nextnode=[-1, -1], drift=[-1,-1,-1,-1]))
                curnodeidx += 1
                tmpstartcode = sects[0][0] + 1
                tmpendcode = sects[0][1] + 1
                tmpposlist, tmpmaxrow, tmpmaxcol, tmpmaxdrift = self._setxy(codes[tmpstartcode:tmpendcode], startrow + 1, startcol, curnodeidx)
                poslist[-1].drift[0] = tmpmaxcol
                poslist[-1].drift[1] = tmpmaxdrift
                if maxrow < tmpmaxrow:
                    maxrow = tmpmaxrow
                addnode = len(tmpposlist)
                curnodeidx += addnode
                if len(sects) > 1:
                    poslist[-1].nextnode[1] = curnodeidx
                    lastcondidx = len(poslist) - 1
                    poslist[-1].drift[2] = tmpmaxcol + 1
                    poslist[-1].drift[3] = 0
                else:
                    poslist[-1].drift[2] = poslist[-1].drift[0]
                    poslist[-1].drift[3] = poslist[-1].drift[1] + 1
                    tmpmaxdrift += 1
                if addnode > 0:
                    poslist[-1].nextnode[0] = tmpposlist[0].nodeno
                poslist.extend(tmpposlist)
                startrow += self.COND_DOWN
                # else if块
                for item in sects[1:-1]:
                    poslist.append(self.FlowNode(nodeno=curnodeidx,code=codes[item[0]].lstrip('\t'),nodetype='elif',x=tmpmaxcol+1, y=startrow, nextnode=[-1, -1], drift=[-1, -1, -1, -1]))
                    curnodeidx += 1
                    tmpstartcode = item[0] + 1
                    tmpendcode = item[1] + 1
                    tmpposlist, tmpmaxrow, tmpmaxcol, tmpmaxdrift = self._setxy(codes[tmpstartcode:tmpendcode], startrow + 1, tmpmaxcol + 1, curnodeidx)
                    poslist[-1].drift[0] = tmpmaxcol
                    poslist[-1].drift[1] = tmpmaxdrift
                    poslist[-1].drift[2] = tmpmaxcol + 1
                    poslist[-1].drift[3] = 0
                    if maxrow < tmpmaxrow:
                        maxrow = tmpmaxrow
                    addnode = len(tmpposlist)
                    curnodeidx += addnode
                    poslist[-1].nextnode[1] = curnodeidx
                    lastcondidx = len(poslist) - 1
                    if addnode > 0:
                        poslist[-1].nextnode[0] = tmpposlist[0].nodeno
                    poslist.extend(tmpposlist)
                    startrow += self.COND_DOWN
                if len(sects) > 1:
                    tmpstartcode = sects[-1][0] + 1
                    tmpendcode = sects[-1][1] + 1
                    if 'else if ' in codes[sects[-1][0]]:
                        # else if块
                        poslist.append(self.FlowNode(nodeno=curnodeidx,code=codes[sects[-1][0]].lstrip('\t'),nodetype='elif',x=tmpmaxcol+1, y=startrow, nextnode=[-1, -1], drift=[-1, -1, -1, -1]))
                        curnodeidx += 1
                        tmpposlist, tmpmaxrow, tmpmaxcol, tmpmaxdrift = self._setxy(codes[tmpstartcode:tmpendcode], startrow + 1, tmpmaxcol + 1, curnodeidx)
                        poslist[-1].drift[0] = tmpmaxcol
                        poslist[-1].drift[1] = tmpmaxdrift
                        poslist[-1].drift[2] = tmpmaxcol
                        poslist[-1].drift[3] = tmpmaxdrift + 1
                        tmpmaxdrift += 1
                        if maxrow < tmpmaxrow:
                            maxrow = tmpmaxrow
                        addnode = len(tmpposlist)
                        curnodeidx += addnode
                        if addnode > 0:
                            poslist[-1].nextnode[0] = tmpposlist[0].nodeno
                        poslist.extend(tmpposlist)
                        startrow += self.COND_DOWN
                    else:
                        # else块
                        tmpposlist, tmpmaxrow, tmpmaxcol, tmpmaxdrift = self._setxy(codes[tmpstartcode:tmpendcode], startrow + 1 - self.COND_DOWN, tmpmaxcol + 1, curnodeidx)
                        if maxrow < tmpmaxrow:
                            maxrow = tmpmaxrow
                        addnode = len(tmpposlist)
                        curnodeidx += addnode
                        poslist.extend(tmpposlist)
                        if addnode <= 0:
                            tmpmaxcol -= 1
                            poslist[lastcondidx].nextnode[1] = -1
                            poslist[lastcondidx].drift[2] = poslist[lastcondidx].drift[0]
                            poslist[lastcondidx].drift[3] = poslist[lastcondidx].drift[1] + 1
                            tmpmaxdrift = poslist[lastcondidx].drift[3]
                        else:
                            poslist[lastcondidx].drift[2] = tmpmaxcol
                            poslist[lastcondidx].drift[3] = tmpmaxdrift
                idx = sects[-1][1] + 1
                if maxcol < tmpmaxcol:
                    maxcol = tmpmaxcol
                    maxdrift = tmpmaxdrift
                elif maxcol == tmpmaxcol and maxdrift < tmpmaxdrift:
                    maxdrift = tmpmaxdrift
            elif line.startswith('for ') or line.startswith('while '):
                tmpidx = idx + 1
                while tmpidx < len(codes):
                    tmpline = codes[tmpidx]
                    tmptabs = tmpline.rfind('\t') + 1
                    if tmptabs <= tabs:
                        break
                    tmpidx += 1
                for nodei in range(curnodeidx-nodeidx):
                    for nodej in range(len(poslist[nodei].nextnode)):
                        if poslist[nodei].nextnode[nodej] == -1:
                            poslist[nodei].nextnode[nodej] = curnodeidx
                poslist.append(self.FlowNode(nodeno=curnodeidx,code=line,nodetype='loop start',x=startcol, y=startrow, nextnode=[-1], drift=[]))
                curnodeidx += 1
                startrow += 1
                tmpstartcode = idx + 1
                tmpendcode = tmpidx
                tmpposlist, tmpmaxrow, tmpmaxcol, tmpmaxdrift = self._setxy(codes[tmpstartcode:tmpendcode], startrow, startcol, curnodeidx)
                if maxrow < tmpmaxrow:
                    maxrow = tmpmaxrow
                if maxcol < tmpmaxcol:
                    maxcol = tmpmaxcol
                    maxdrift = tmpmaxdrift
                elif maxcol == tmpmaxcol and maxdrift < tmpmaxdrift:
                    maxdrift = tmpmaxdrift
                addnode = len(tmpposlist)
                curnodeidx += addnode
                if addnode > 0:
                    poslist[-1].nextnode[0] = tmpposlist[0].nodeno
                poslist.extend(tmpposlist)
                for nodei in range(curnodeidx-nodeidx):
                    for nodej in range(len(poslist[nodei].nextnode)):
                        if poslist[nodei].nextnode[nodej] == -1:
                            poslist[nodei].nextnode[nodej] = curnodeidx
                startrow = maxrow
                poslist.append(self.FlowNode(nodeno=curnodeidx,code='',nodetype='loop end',x=startcol, y=startrow, nextnode=[-1], drift=[]))
                curnodeidx += 1
                maxrow += 1
                idx = tmpidx
            else:
                for nodei in range(curnodeidx-nodeidx):
                    for nodej in range(len(poslist[nodei].nextnode)):
                        if poslist[nodei].nextnode[nodej] == -1:
                            poslist[nodei].nextnode[nodej] = curnodeidx
                if self.PAT_FUNC.search(line):
                    poslist.append(self.FlowNode(nodeno=curnodeidx,code=line,nodetype='subroutine',x=startcol, y=startrow, nextnode=[-1], drift=[]))
                else:
                    poslist.append(self.FlowNode(nodeno=curnodeidx,code=line,nodetype='normal',x=startcol, y=startrow, nextnode=[-1], drift=[]))
                curnodeidx += 1
                maxrow += 1
                idx += 1
            startrow = maxrow
        self._log.log(10, 'CodeLen={0}, MaxRow={1}, MaxCol={2}, MaxDrift={3}'.format(len(codes), maxrow, maxcol, maxdrift))
        return poslist, maxrow, maxcol, maxdrift

if __name__ == '__main__':
    logutil.logConf()
    cp = configparser.ConfigParser()
    cp.read_file(open('xmlconf.ini'))
    act1 = cp.get('action_input_file','act')
    act2 = cp.get('action_mid_file','act')
    act3 = cp.get('action_xml_file','act')
    if act1 == '1':
        # 执行功能1：抽出目标函数代码
        print("Extract source code files...")
        cscopeout = cp.get('action_input_file','indir')
        if not os.path.isfile(os.path.join(cscopeout, 'cscope.out')):
            # 初次执行功能1时，生成tag文件
            print("  Generate tag files...")
            curdir = os.path.abspath('.')
            os.chdir(cscopeout)
            params=[os.path.join(logutil.scriptPath(), 'bin', 'cscope.exe'), '-Rbcu']
            try:
                subprocess.check_call(params)
            except subprocess.CalledProcessError as e:
                print(e)
                sys.exit(1)
            os.chdir(curdir)
        funclist = cp.get('action_input_file','functions').split(',')
        aic = AstahInputCode(cscopeout)
        opath = cp.get('action_input_file','outdir')
        for func in funclist:
            aic.outputFile(func, os.path.join(opath, func+'.txt'))
    if act2 == '1':
        # 执行功能2：生成中间文件
        print("Generate middle files...")
        amc = AstahMidCode()
        ipath = cp.get('action_mid_file','indir')
        opath = cp.get('action_mid_file','outdir')
        for fname in os.listdir(ipath):
            if fname.endswith('.txt'):
                # 取得indir目录中的*.txt文件
                amc.fmtCode(os.path.join(ipath, fname), os.path.join(opath, os.path.splitext(fname)[0]+'.mid'))
    if act3 == '1':
        # 执行功能3：生成xml文件
        print("Generate xml files...")
        afp = AstahFuncPos(cp.items('setting'))
        ipath = cp.get('action_xml_file','indir')
        opath = cp.get('action_xml_file','outdir')
        for fname in os.listdir(ipath):
            if fname.endswith('.mid'):
                # 取得indir目录中的*.mid文件
                afp.analyze(os.path.join(ipath, fname), opath)
