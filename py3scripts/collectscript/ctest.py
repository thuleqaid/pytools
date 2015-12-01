# -*- coding:utf-8 -*-
import os
import html
import re
from .logutil import LogUtil, registerLogger
from .tagparser import CscopeParser
from .ctokens import CTokens
from .guess import guessEncode

LOGNAME = "CTest"
LOGNAME2 = "CResult"
registerLogger(LOGNAME)
registerLogger(LOGNAME2)

class CTest(object):
    def __init__(self, tagpath):
        self._log = LogUtil().logger(LOGNAME)
        self.rootpath = tagpath
        self.parser = CscopeParser(os.path.join(tagpath,'cscope.out'))
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
            token  = CTokens()
            token.parse_file(fullpath)
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
            token.inject(fullpath, encode, inputlist)
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

class CResult(object):
    PTN_COND = re.compile(r'\(DMYCOND\((?P<cond>.+?),&quot;(?P<level>.{2})&quot;\)\)')
    PTN_BLOCK = re.compile(r'(DMYBOOL )?__tmp__ = DMYBLOCK\(&quot;(&lt;(?P<filename>.+?):(?P<funcname>.+?)&gt;|(?P<blockno>.{3}))&quot;\);')
    def __init__(self):
        self._log = LogUtil().logger(LOGNAME2)
    def _htmlcode(self, cfiles):
        tabtitle = []
        tabcontent = []
        for idx,cfile in enumerate(cfiles):
            if idx == 0:
                tabtitle.append('<li class="active"><a href="#tab{index}" data-toggle="tab">{title}</a></li>'.format(index=idx, title=cfile))
                tabcontent.append('<div class="tab-pane active" id="tab{index}"><pre class="bg-danger">{content}</pre></div>'.format(index=idx, content=self._html_block(cfile)))
            else:
                tabtitle.append('<li><a href="#tab{index}" data-toggle="tab">{title}</a></li>'.format(index=idx, title=cfile))
                tabcontent.append('<div class="tab-pane" id="tab{index}"><pre class="bg-danger">{content}</pre></div>'.format(index=idx, content=self._html_block(cfile)))
        outtext = '<div>\n\t<ul class="nav nav-tabs">\n\t\t'+'\n\t\t'.join(tabtitle)+'\n\t</ul>\n\t<div class="tab-content">\n\t\t'+'\n\t\t'.join(tabcontent)+'\n\t</div>\n</div>'
        return outtext
    def _html_block(self, cfile):
        fh = open(cfile, 'r', encoding='utf_8_sig')
        source = fh.read()
        fh.close()
        source = html.escape(source)
        lastidx = 0
        outline = ''
        funcline = ''
        lastfilename = ''
        lastfuncname = ''
        for matchblock in self.PTN_BLOCK.finditer(source):
            blockno = matchblock.group('blockno')
            filename = matchblock.group('filename')
            funcname = matchblock.group('funcname')
            if blockno:
                blockno = blockno[1:]
            else:
                if lastfilename != '':
                    # 第二个以及后面的函数开始
                    outline += self._html_condition(funcline,'cond_{0}_{1}_'.format(lastfilename, lastfuncname)) + '</span>'
                    funcline = ''
                # 第一个函数开始
                lastfilename = filename.replace('.','_')
                lastfuncname = funcname
                blockno = '00'
            bid = 'block_{0}_{1}_{2}'.format(lastfilename, lastfuncname, blockno)
            if blockno == '00':
                funcline += source[lastidx:matchblock.span()[0]] + '<span id="{0}">'.format(bid)
            else:
                funcline += source[lastidx:matchblock.span()[0]] + '</span><span id="{0}">'.format(bid)
            lastidx = matchblock.span()[1]
        outline += self._html_condition(funcline,'cond_{0}_{1}_'.format(lastfilename, lastfuncname)) + '</span>'
        outline += source[lastidx:]
        return outline
    def _html_condition(self, text, idprefix):
        lastidx = 0
        newline = ''
        for matchcond in self.PTN_COND.finditer(text):
            level = matchcond.group('level')
            truecond = matchcond.group('cond')
            newline += text[lastidx:matchcond.span()[0]] + '<a href="#" class="btn-default" id="{2}{0}">{1}</a>'.format(level, truecond, idprefix)
            lastidx = matchcond.span()[1]
        newline += text[lastidx:]
        return newline
    def report(self, title, outfile, cfiles, resultfile=''):
        fhtml = open(outfile,'w',encoding='utf-8')
        fhtml.write('''<!DOCTYPE html>
<html>
	<head>
		<meta charset="UTF-8">
		<meta name="viewport" content="width=device-width, initial-scale=1">
		<title>{title}</title>
		<link type="text/css" href="lib/bootstrap/css/bootstrap.min.css" rel="stylesheet">
		<link type="text/css" href="lib/bootstrap/css/bootstrap-theme.min.css" rel="stylesheet">
		<script type="text/javascript" src="lib/jquery/jquery.min.js"></script>
		<script type="text/javascript" src="lib/bootstrap/js/bootstrap.min.js"></script>
		<link rel="stylesheet" type="text/css" href="lib/datatables/datatables.min.css">
		<script type="text/javascript" charset="utf8" src="lib/datatables/datatables.min.js"></script>
	</head>
	<body>
		<div class="container">
			<div class="row">
				<p class="col-sm-2"><strong>Route</strong></p>
				<span class="col-sm-2 bg-danger">Not Pass</span>
				<span class="col-sm-2 bg-success">Pass</span>
			</div>
			<div class="row">
				<p class="col-sm-2"><strong>Condition</strong></p>
				<a href="#" class="col-sm-2 btn-default">None</a>
				<a href="#" class="col-sm-2 btn-danger">False</a>
				<a href="#" class="col-sm-2 btn-success">True</a>
				<a href="#" class="col-sm-2 btn-primary">True/False</a>
			</div>
{sourcetab}
			<ul>
				<li class="col-sm-6"><a href="javascript:void(0)" onclick="toggleCase(true)">Check All</a></li>
				<li class="col-sm-6"><a href="javascript:void(0)" onclick="toggleCase(false)">Check None</a></li>
			</ul>
		</div>
	</body>
</html>'''.format(title=title, sourcetab=self._htmlcode(cfiles)))
        fhtml.close()
        pass
