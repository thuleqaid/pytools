# -*- coding:utf-8 -*-
import os
import html
import re
import json
import collections
import csv
from .logutil import LogUtil, registerLogger, scriptPath
from .tagparser import CscopeParser
from .ctokens import CTokens
from .guess import guessEncode, openTextFile

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
        self.funcdetail = {} # key:fullpath, value: CTokens.funcinfo
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
            self.funcdetail[fullpath] = token.funcinfo

class CResult(object):
    PTN_COND = re.compile(r'\(DMYCOND\((?P<cond>.+?),&quot;(?P<level>.{2})&quot;\)\)')
    PTN_BLOCK = re.compile(r'(DMYBOOL )?__tmp__ = DMYBLOCK\(&quot;(&lt;(?P<filename>.+?):(?P<funcname>.+?)&gt;|(?P<blockno>.{3}))&quot;\);')
    def __init__(self):
        self._log = LogUtil().logger(LOGNAME2)
    def report(self, title, outfile, cfiles, resultfile):
        # 生成结果报告
        self._initval = {}
        sourcetab=self._htmlcode(cfiles)
        initval=json.dumps(self._initval)
        casetable = self._htmlcase(resultfile)
        fhtml = open(outfile,'w',encoding='utf-8')
        fhtml.write('''<!DOCTYPE html>
<html>
	<head>
		<meta charset="UTF-8">
		<meta name="viewport" content="width=device-width, initial-scale=1">
		<title>''')
        fhtml.write(title);
        fhtml.write('''</title>
		<link type="text/css" href="lib/bootstrap/css/bootstrap.min.css" rel="stylesheet">
		<link type="text/css" href="lib/bootstrap/css/bootstrap-theme.min.css" rel="stylesheet">
		<script type="text/javascript" src="lib/jquery/jquery.min.js"></script>
		<script type="text/javascript" src="lib/bootstrap/js/bootstrap.min.js"></script>
		<link rel="stylesheet" type="text/css" href="lib/datatables/datatables.min.css">
		<script type="text/javascript" charset="utf8" src="lib/datatables/datatables.min.js"></script>
		<script type="text/javascript">
			function updateCss() {
				var result = ''')
        fhtml.write(initval)
        fhtml.write(''';
				var tmpvar, key;
				var chks = $('.caseswitch');
				for (var i=0; i<chks.length; i++) {
					if (chks[i].checked) {
						eval('tmpvar = '+chks[i].getAttribute('data-info'));
						key = '';
						for (key in tmpvar) {
							if (key.substr(0,5) === 'block') {
								if (tmpvar[key] === true) {
									result[key] = true;
								}
							} else {
								result[key] = result[key] | tmpvar[key];
							}
						}
					}
				}
				for (key in result) {
					if (key.substr(0,5) === 'block') {
						$('#'+key).removeClass('bg-success');
						if (result[key] === true) {
							$('#'+key).addClass('bg-success');
						}
					} else {
						$('#'+key).removeClass('btn-primary').removeClass('btn-success').removeClass('btn-danger').addClass('btn-default');
						if (result[key] == 1) {
							$('#'+key).addClass('btn-danger').removeClass('btn-default');
						} else if (result[key] == 2) {
							$('#'+key).addClass('btn-success').removeClass('btn-default');
						} else if (result[key] == 3) {
							$('#'+key).addClass('btn-primary').removeClass('btn-default');
						}
					}
				}
			}
			function toggleCase(status) {
				var chks = $('.caseswitch');
				for (var i=0; i<chks.length; i++) {
					chks[i].checked = status;
				}
				updateCss();
			}
			$(document).ready(function() {
				$('#casetable').DataTable({
					scrollY: 300,
					scrollX: true,
					scrollCollapse: true,
					paging: false,
					fixedColumns: true,
					bPaginate: false,
					bFilter: false
				});
				updateCss();
			});
		</script>
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
				<a href="javascript:void(0)" class="col-sm-2 btn-default">None</a>
				<a href="javascript:void(0)" class="col-sm-2 btn-danger">False</a>
				<a href="javascript:void(0)" class="col-sm-2 btn-success">True</a>
				<a href="javascript:void(0)" class="col-sm-2 btn-primary">True/False</a>
			</div>
''')
        fhtml.write(sourcetab)
        fhtml.write('''			<ul>
				<li class="col-sm-6"><a href="javascript:void(0)" onclick="toggleCase(true)">Check All</a></li>
				<li class="col-sm-6"><a href="javascript:void(0)" onclick="toggleCase(false)">Check None</a></li>
			</ul>''')
        fhtml.write(casetable)
        fhtml.write('''		</div>
	</body>
</html>''')
        fhtml.close()
    def _htmlcode(self, cfiles):
        # 生成C代码的HTML区块
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
            self._initval[bid]=False
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
            cid = '{0}{1}'.format(idprefix,level)
            newline += text[lastidx:matchcond.span()[0]] + '<a href="javascript:void(0)" class="btn-default" id="{0}">{1}</a>'.format(cid, truecond)
            lastidx = matchcond.span()[1]
            self._initval[cid]=0
        newline += text[lastidx:]
        return newline
    def _htmlcase(self, resultfile):
        # 生成测试用例的HTML区块
        fh = openTextFile(['cp932','cp936'], resultfile, 'r')
        lines = fh.readlines()
        fh.close()
        results = []
        checkvar = []
        pat_first = re.compile(r'^;TestCase\s+(?P<caseno>\d+)')
        pat_middle = re.compile(r'^(?P<name>.+)\s+=\s+(?P<value1>-?\d+),\s+(?P<value2>-?\d+)')
        pat_last = re.compile(r'^#Track\s+=\s+(?P<track>.+)')
        for line in lines:
            line = line.strip()
            if line.startswith(';'):
                ret = pat_first.search(line)
                testcase = ret.group('caseno')
                tmplist = []
            elif line.startswith('#'):
                ret = pat_last.search(line)
                results.append((testcase, tuple(tmplist), ret.group('track')))
            else:
                ret = pat_middle.search(line)
                if len(results) < 1:
                    checkvar.append(ret.group('name'))
                tmplist.append((ret.group('value1'),ret.group('value2')))
        bodylist = []
        for item in results:
            testcase = item[0]
            tmplist = item[1]
            status = True
            for subitem in tmplist:
                if subitem[0] != subitem[1]:
                    status = False
                    break
            caseval = self._decodeTrack(item[2])
            if status:
                txt = '<tr><td>'+testcase+'</td>' + '<td>OK</td>'
            else:
                txt = '<tr><td class="text-danger">'+testcase+'</td>' + '<td class="text-danger">NG</td>'
            txt += '<td><div class="switch"><input type="checkbox" class="caseswitch" onclick="updateCss()" id="chk-{}" checked="checked" data-info="{}"/></div></td>\n'.format(testcase, json.dumps(caseval).replace('"',"'"))
            for subitem in tmplist:
                if subitem[0] != subitem[1]:
                    txt+='<td><a href="javascript:void(0)" class="btn btn-danger">' + subitem[0] + '(' + subitem[1] + ')</a></td>'
                else:
                    txt+='<td>' + subitem[0] + '(' + subitem[1] + ')</td>'
            txt+='</tr>'
            bodylist.append(txt)
        outtxt = '<table class="table table-hover table-striped" id="casetable">\n\t<thead>\n\t\t<tr>\n\t\t\t<td>TestCase</td>\n\t\t\t<td>Status</td>\n\t\t\t<td>Show</td>'
        for item in checkvar:
            outtxt += '\n\t\t\t<td>' + item + '</td>'
        outtxt += '\n\t\t</tr>\n\t</thead>\n\t<tbody>\n\t\t'
        outtxt += '\n\t\t'.join(bodylist)
        outtxt += '\n\t</tbody>\n</table>'
        return outtxt
    def _decodeTrack(self, text):
        outdict = {}
        partlist = []
        i = 0
        txtlen = len(text)
        while i < txtlen:
            if text[i] == '<':
                j = text.find(':', i)
                k = text.find('>', j)
                filename = text[i+1:j].replace('.','_')
                funcname = text[j+1:k]
                part = '_'+filename+'_'+funcname+'_'
                partlist.append(part)
                outdict['block'+partlist[-1]+'00'] = True
                i = k + 1
            elif text[i] == '#':
                outdict['block'+partlist[-1]+text[i+1:i+3]] = True
                i += 3
            elif text[i] == '@':
                outdict['block'+partlist[-1]+text[i+1:i+3]] = True
                i += 3
                partlist.pop()
            else:
                cid = 'cond'+partlist[-1]+text[i:i+2]
                outdict.setdefault(cid, 0)
                if text[i+2] == 'T':
                    outdict[cid] = outdict[cid] | 2
                else:
                    outdict[cid] = outdict[cid] | 1
                i += 3
        return outdict

class WinAMS(object):
    CSVInfo = collections.namedtuple('CSVInfo',['funcname','funcno','icount','ocount','stub','var','case','ret','param'])
    def __init__(self):
        pass
    def _loadCSV(self, csvfile):
        fh = openTextFile(('cp932','cp936'),csvfile,'r')
        stub = []
        var = []
        case = []
        reader = csv.reader(fh)
        retflag = False
        paramflag = False
        for rowidx,row in enumerate(reader):
            if row[0] == 'mod':
                # 第一行,提取目标函数名和入出力个数
                targetfunc = row[1]
                targetno   = row[2]
                count_in   = int(row[3])
                count_out  = int(row[4])
            elif row[0] == '%':
                # stub函数定义
                stub.append((row[2],row[1]))
            elif row[0] == '#COMMENT':
                # 入出力定义
                for x in row:
                    if x.endswith('@@'):
                        var.append(x.replace('@@','__ret'))
                        retflag = True
                    elif x.startswith('@'):
                        var.append(x[1:])
                        paramflag = True
                    else:
                        var.append(x)
            elif row[0] == '':
                # 测试用例
                row[0] = rowidx + 1
                case.append(tuple(row))
        fh.close()
        self.csvinfo = self.CSVInfo(funcname = targetfunc,
                                    funcno   = targetno,
                                    icount   = count_in,
                                    ocount   = count_out,
                                    stub     = stub,
                                    var      = var,
                                    case     = case,
                                    ret      = retflag,
                                    param    = paramflag)
    def _writeTestFunc(self, modfile, funcdetail):
        fh = open(modfile, 'a', encoding='utf_8_sig')
        fh.write('#include <stdio.h>\n')
        fh.write('#include <stdlib.h>\n')
        fh.write('#include <string.h>\n')
        fh.write('void TestMain()\n')
        fh.write('{\n')
        fh.write('    int i;\n')
        # 测试目标函数的参数和返回值
        if self.csvinfo.ret:
            fh.write('    '+funcdetail[0][1]+' '+funcdetail[0][0]+'__ret;\n')
        if self.csvinfo.param:
            for i in range(len(funcdetail)-1):
                fh.write('    '+funcdetail[i+1][1]+';\n')
        fh.write('    FILE *fp;\n')
        resultfile = os.path.join(scriptPath(),self.csvinfo.funcno+'.txt').replace('\\','\\\\')
        fh.write('    fopen_s(&fp, "{}", "wt");\n'.format(resultfile))
        fh.write('    for (i = 0; i < {}; ++i)\n'.format(len(self.csvinfo.case)))
        fh.write('    {\n')
        fh.write('        /* initialize */\n')
        fh.write('        _dmy_index = 0;\n')
        fh.write('        memset(&_dmy_record[0], 0, _dmy_size);\n')
        for i in range(len(self.csvinfo.case)):
            if i == 0:
                fh.write('        if (i == {}) \n'.format(i))
            else:
                fh.write('        else if (i == {}) \n'.format(i))
            fh.write('        {\n')
            fh.write('            /* TestCase {} */\n'.format(self.csvinfo.case[i][0]))
            for j in range(self.csvinfo.icount):
                fh.write('            {} = {};\n'.format(self.csvinfo.var[j+1],self.csvinfo.case[i][j+1]))
            fh.write('        }\n')
        fh.write('        /* call function */\n')
        # 调用测试目标函数
        if self.csvinfo.ret:
            tmptxt = '        ' + funcdetail[0][0] + '__ret = '
        else:
            tmptxt = '        '
        tmptxt += funcdetail[0][0] + '('
        if self.csvinfo.param:
            tmptxt += ', '.join([x[0] for x in funcdetail[1:]])
        tmptxt += ');\n'
        fh.write(tmptxt)
        fh.write('        /* write output */\n')
        for i in range(len(self.csvinfo.case)):
            if i == 0:
                fh.write('        if (i == {}) \n'.format(i))
            else:
                fh.write('        else if (i == {}) \n'.format(i))
            fh.write('        {\n')
            fh.write('            fprintf(fp, ";TestCase {}\\n");\n'.format(self.csvinfo.case[i][0]))
            for j in range(self.csvinfo.ocount):
                fh.write('            fprintf(fp, "{0} = %d, %d\\n", {1}, {0});\n'.format(self.csvinfo.var[self.csvinfo.icount + j + 1], self.csvinfo.case[i][self.csvinfo.icount + j + 1]))
            fh.write('        }\n')
        fh.write('        /* write track info */\n')
        fh.write('        fprintf(fp, "#Track = %s\\n", _dmy_record);\n')
        fh.write('    }\n')
        fh.write('    fclose(fp);\n')
        fh.write('}\n')
        fh.close()
    def test(self, csvfile, rootpath):
        self._loadCSV(csvfile)
        inputinfo = [
                     {'function':self.csvinfo.funcname,
                      'dummy':self.csvinfo.stub
                     },
                    ]
        ct = CTest(rootpath)
        ct.inject(inputinfo)
        for fname in ct.funcdetail:
            for item in ct.funcdetail[fname]:
                if item[0][0] == self.csvinfo.funcname:
                    self._writeTestFunc(fname, item)
                    break
