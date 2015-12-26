# -*- coding:utf-8 -*-
import os
import html
import re
import json
import collections
import csv
import itertools
from .logutil import LogUtil, registerLogger, scriptPath
from .tagparser import CscopeParser
from .ctokens import CTokens
from .guess import guessEncode, openTextFile

LOGNAME = "CTest"
LOGNAME2 = "CResult"
registerLogger(LOGNAME)
registerLogger(LOGNAME2)

# 使用方法：
# 1. 代码注入
#    根据测试用例文件格式不同，需要编写一个类似WinAMS的class
#    ams = ctest.WinAMS()
#    ams.test(测试用例设计.csv, 代码路径)
# 2. 编译运行C工程文件
#    下面的命令可以在命令行下编译和运行
#    set devenv="%VS80COMNTOOLS%..\IDE\devenv"
#    set sln="d:\xxx\xxx.sln"
#    %devenv% %sln% /Build
#    %devenv% %sln% /RunExit
#    下面的命令可以等待10秒
#    ping -n 10 127.0.0.1 >nul
# 3. 结果生成
#    cr = ctest.CResult()
#    cr.report()
# 4. 代码还原
#    restore.bat
# 5. 批量处理
#    5.1 脚本文件1(batch.py)
#        from collectscript import ctest
#        if __name__ == '__main__':
#            cb = ctest.CBatch()
#            cb.batch()
#    5.2 脚本文件2(modify.py)
#        import sys
#        from collectscript import ctest
#        if __name__ == '__main__':
#            ams = ctest.WinAMS()
#            ams.test(sys.argv[1], sys.argv[2])
#    5.3 脚本文件3(result.py)
#        from collectscript import ctest
#        if __name__ == '__main__':
#            cr = ctest.CResult()
#            cr.report()
#    5.4 编写batchList.txt
#        以"#"或者";"开头的行是注释（无效行）
#        第一有效行为代码路径
#        第二有效行为工程文件路径
#        第三有效行开始为测试用例文件
#    5.5 运行batch.py生成batch.bat
#    5.6 运行batch.bat

# CTest注入时调用的函数代码
# /* dmy_test.h */
# #ifndef _DMY_TEST_H_
# #define _DMY_TEST_H_
# #ifdef _DMY_TEST_C_
# #define EXTERN
# #else
# #define EXTERN extern
# #endif
# #define _dmy_step 3
# #define _dmy_size (3072)
# EXTERN char _dmy_record[_dmy_size];
# EXTERN int _dmy_index;
# typedef int DMYBOOL;
# #ifdef __cplusplus
# extern "C" {
# #endif
# 	DMYBOOL	DMYBLOCK(char const * const name);
# 	DMYBOOL	DMYCOND(DMYBOOL cond, char const * const name);
# 	void	TestMain( void );
# #ifdef __cplusplus
# }
# #endif
# #endif
# /* dmy_test.c */
# #define _DMY_TEST_C_
# #include "dmy_test.h"
# DMYBOOL DMYBLOCK(char const * const name)
# {
# 	int i = 0;
# 	if (name[0] == '<') {
# 		while (name[i] != '>') {
# 			_dmy_record[_dmy_index + i] = name[i];
# 			i++;
# 		}
# 		_dmy_record[_dmy_index + i] = name[i];
# 		_dmy_index += i+1;
# 	} else {
# 		for (i = 0; i < _dmy_step; ++i) {
# 			_dmy_record[_dmy_index + i] = name[i];
# 		}
# 		_dmy_index += _dmy_step;
# 	}
# 	return 1;
# }
# DMYBOOL DMYCOND(DMYBOOL cond, char const * const name)
# {
# 	int i = 0;
# 	for (i = 0; i < _dmy_step - 1; ++i) {
# 		_dmy_record[_dmy_index + i] = name[i];
# 	}
# 	if (cond) {
# 		_dmy_record[_dmy_index + _dmy_step - 1] = 'T';
# 	} else {
# 		_dmy_record[_dmy_index + _dmy_step - 1] = 'F';
# 	}
# 	_dmy_index += _dmy_step;
# 	return cond;
# }

class CTest(object):
    # 代码注入
    def __init__(self, tagpath):
        self._log = LogUtil().logger(LOGNAME)
        self.rootpath = tagpath
        self.parser = CscopeParser(os.path.join(tagpath,'cscope.out'))
    def inject(self, funclist):
        # funclist: [{'function':function-name,'dummy':[(org-function-name, dmy-function-name),...]},...]
        self.funcdetail = collections.OrderedDict() # key:fullpath, value: CTokens.funcinfo
        self.staticdetail = collections.OrderedDict() # key:fullpath value: CTokens.staticinfo
        injectinfo = collections.OrderedDict() # key:relpath
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
                            subfuncs.append(dmy[1])
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
                    subfuncs = list(self.parser.getFuncCall_asdict(funcinfo).keys())
                    for subf in subfuncs:
                        appendfunclist.append({'function':subf, 'dummy':[]})
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
            self.staticdetail[fullpath] = token.staticinfo

class CResult(object):
    # 结果显示
    PTN_COND = re.compile(r'\(DMYCOND\((?P<cond>.+?),&quot;(?P<level>.{2})&quot;\)\)')
    PTN_BLOCK = re.compile(r'(DMYBOOL )?__tmp__ = DMYBLOCK\(&quot;(&lt;(?P<filename>.+?):(?P<funcname>.+?)&gt;|(?P<blockno>.{3}))&quot;\);')
    def __init__(self):
        self._log = LogUtil().logger(LOGNAME2)
    def report(self, conffile='report.conf'):
        fh = open(conffile, 'r', encoding='utf-8')
        lines = fh.readlines()
        fh.close()
        title = lines[0].strip()
        outfile = lines[1].strip()
        resultfile = lines[2].strip()
        cfiles = [x.strip() for x in lines[3:]]
        self._report(title, outfile, cfiles, resultfile)
    def _report(self, title, outfile, cfiles, resultfile):
        # 生成结果报告
        self._initval = {}
        self._coverage = collections.OrderedDict()
        sourcetab=self._htmlcode(cfiles)
        initval=json.dumps(self._initval)
        casetable = self._htmlcase(resultfile)
        covtable = self._calcCoverage()
        fhtml = open(outfile,'w',encoding='utf-8')
        fhtml.write('''<!DOCTYPE html>
<html>
	<head>
		<meta charset="UTF-8">
		<meta name="viewport" content="width=device-width, initial-scale=1">
		<title>''')
        fhtml.write(title);
        fhtml.write('''</title>
		<link type="text/css" href="../lib/bootstrap/css/bootstrap.min.css" rel="stylesheet">
		<link type="text/css" href="../lib/bootstrap/css/bootstrap-theme.min.css" rel="stylesheet">
		<script type="text/javascript" src="../lib/jquery/jquery.min.js"></script>
		<script type="text/javascript" src="../lib/bootstrap/js/bootstrap.min.js"></script>
		<link rel="stylesheet" type="text/css" href="../lib/datatables/datatables.min.css">
		<script type="text/javascript" charset="utf8" src="../lib/datatables/datatables.min.js"></script>
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
        fhtml.write(covtable)
        fhtml.write('''			<ul>
				<li class="col-sm-6"><a href="javascript:void(0)" onclick="toggleCase(true)">Check All</a></li>
				<li class="col-sm-6"><a href="javascript:void(0)" onclick="toggleCase(false)">Check None</a></li>
			</ul>''')
        fhtml.write(casetable)
        fhtml.write('''		</div>
	</body>
</html>''')
        fhtml.close()
    def _calcCoverage(self):
        for filename in self._coverage.keys():
            for funcname in self._coverage[filename].keys():
                info = self._coverage[filename][funcname]
                # C0 Coverage
                for block in info['block'][:-1]:
                    if not info['result'].get(block, False):
                        flag_c0 = False
                        break
                else:
                    flag_c0 = True
                # MC/DC Coverage
                for cond in info['cond1']:
                    if info['result'].get(cond, 0) != 3:
                        flag_mcdc = False
                        break
                else:
                    flag_mcdc = True
                # C1 Coverage
                if flag_c0:
                    if len(info['cond0']) == len(info['cond1']):
                        # 没有复合条件，C1和MC/DC等价
                        flag_c1 = flag_mcdc
                    else:
                        if flag_mcdc:
                            # MC/DC覆盖完全，C1必然覆盖完全
                            flag_c1 = True
                        else:
                            for conds in info['cond0']:
                                parts = re.split(r'\s*(?:and|or)\s*',conds)
                                if len(parts) == 1:
                                    # 不是复合语句
                                    if info['result'][parts[0]] != 3:
                                        flag_c1 = False
                                        break
                                else:
                                    result = 0
                                    values = []
                                    for part in parts:
                                        val = info['result'].get(part, 1)
                                        if val == 3:
                                            values.append(['True', 'False'])
                                        elif val == 2:
                                            values.append(['True'])
                                        else:
                                            values.append(['False'])
                                    for comb in itertools.product(*values):
                                        tmpcond = conds
                                        for pidx, part in enumerate(parts):
                                            tmpcond = tmpcond.replace(part, comb[pidx])
                                        if eval(tmpcond):
                                            result = result | 2
                                        else:
                                            result = result | 1
                                        if result == 3:
                                            break
                                    else:
                                        flag_c1 = False
                                        break
                            else:
                                flag_c1 = True
                else:
                    # C0覆盖不完全，C1必然覆盖不完全
                    flag_c1 = False
                self._coverage[filename][funcname]['coverage'] = (flag_c0, flag_c1, flag_mcdc)
        outtext = '<table class="table table-hover table-striped">\n\t<thead>\n\t\t<tr><td>File</td><td>Function</td><td>C0</td><td>C1</td><td>MC/DC</td></tr>\n\t</thead>\n\t<tbody>\n'
        for filename in self._coverage.keys():
            dotpos = filename.rfind('_')
            if dotpos > 0:
                truename = filename[:dotpos] + '.' + filename[dotpos+1:]
            else:
                truename = filename
            for funcname in self._coverage[filename].keys():
                cov = self._coverage[filename][funcname]['coverage']
                outtext += '\t\t<tr><td>'+truename+'</td><td>'+funcname+'</td>'
                for covflag in cov:
                    if covflag:
                        outtext += '<td>OK</td>'
                    else:
                        outtext += '<td><a href="" class="btn btn-danger">NG</a></td>'
                outtext += '</tr>\n'
        outtext += '\t</tbody>\n</table>\n'
        return outtext
    def _htmlcode(self, cfiles):
        # 生成C代码的HTML区块
        tabtitle = []
        tabcontent = []
        for idx,cfile in enumerate(cfiles):
            if idx == 0:
                tabtitle.append('<li class="active"><a href="#tab{index}" data-toggle="tab">{title}</a></li>'.format(index=idx, title=os.path.basename(cfile)))
                tabcontent.append('<div class="tab-pane active" id="tab{index}"><pre class="bg-danger">{content}</pre></div>'.format(index=idx, content=self._html_block(cfile)))
            else:
                tabtitle.append('<li><a href="#tab{index}" data-toggle="tab">{title}</a></li>'.format(index=idx, title=os.path.basename(cfile)))
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
                    outline += self._html_condition(funcline,lastfilename, lastfuncname) + '</span>'
                    funcline = ''
                # 第一个函数开始
                lastfilename = filename.replace('.','_')
                lastfuncname = funcname
                blockno = '00'
                self._coverage.setdefault(lastfilename,{}).setdefault(lastfuncname,{'block':[],'cond0':[],'cond1':[],'result':{},'coverage':()})
            bid = 'block_{0}_{1}_{2}'.format(lastfilename, lastfuncname, blockno)
            self._coverage[lastfilename][lastfuncname]['block'].append(bid)
            self._initval[bid]=False
            if blockno == '00':
                funcline += source[lastidx:matchblock.span()[0]] + '<span id="{0}">'.format(bid)
            else:
                funcline += source[lastidx:matchblock.span()[0]] + '</span><span id="{0}">'.format(bid)
            lastidx = matchblock.span()[1]
        outline += self._html_condition(funcline,lastfilename, lastfuncname) + '</span>'
        outline += source[lastidx:]
        return outline
    def _html_condition(self, text, curfilename, curfuncname):
        lastidx = 0
        newline = ''
        for matchcond in self.PTN_COND.finditer(text):
            level = matchcond.group('level')
            truecond = matchcond.group('cond')
            cid = 'cond_{0}_{1}_{2}'.format(curfilename, curfuncname, level)
            self._coverage[curfilename][curfuncname]['cond1'].append(cid)
            newline += text[lastidx:matchcond.span()[0]] + '<a href="javascript:void(0)" class="btn-default" id="{0}">{1}</a>'.format(cid, truecond)
            lastidx = matchcond.span()[1]
            self._initval[cid]=0
        newline += text[lastidx:]
        cmtfree = re.sub(r'//.*','',text)
        cmtfree = re.sub(r'/\*(.|\n)*?\*/','',cmtfree)
        cmtfree = re.sub(r'\n', ' ', cmtfree)
        cmtfree = re.sub(r'\s+', ' ', cmtfree)
        cmtfree = self.PTN_COND.sub(r'DMYCOND(\g<level>)', cmtfree)
        cmtfree = re.sub(r'\s*&amp;&amp;\s*',r'&&',cmtfree)
        cmtfree = re.sub(r'\s*\|\|\s*',r'||',cmtfree)
        cmtfree2 = re.sub(r'\(\s*(DMYCOND\(.+?\))\s*\)',r'\1',cmtfree)
        while len(cmtfree) != len(cmtfree2):
            cmtfree = cmtfree2
            cmtfree2 = re.sub(r'\(\s*(DMYCOND\(.+?\))\s*\)',r'\1',cmtfree)
        for item in re.finditer(r'[( )]*DMYCOND\(.+?\)([( )]*(&&|\|\|)[( )]*DMYCOND\(.+?\)[( )]*)*',cmtfree):
            ifcond = item.group(0).strip()
            ifcond = re.sub(r'DMYCOND\((.+?)\)','cond_'+curfilename+'_'+curfuncname+'_'+r'\1',ifcond)
            ifcond = re.sub(r'&&', ' and ', ifcond)
            ifcond = re.sub(r'\|\|', ' or ', ifcond)
            self._coverage[curfilename][curfuncname]['cond0'].append(ifcond)
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
        ngcnt = 0
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
                ngcnt += 1
            txt += '<td><div class="switch"><input type="checkbox" class="caseswitch" onclick="updateCss()" id="chk-{}" checked="checked" data-info="{}"/></div></td>\n'.format(testcase, json.dumps(caseval).replace('"',"'"))
            for subitem in tmplist:
                if subitem[0] != subitem[1]:
                    txt+='<td><a href="javascript:void(0)" class="btn btn-danger">' + subitem[0] + '(' + subitem[1] + ')</a></td>'
                else:
                    txt+='<td>' + subitem[0] + '(' + subitem[1] + ')</td>'
            txt+='</tr>'
            bodylist.append(txt)
        outtxt = '<p>OK Case: '+str(len(results)-ngcnt)+'/'+str(len(results))+'</p>\n'
        outtxt += '<table class="table table-hover table-striped" id="casetable">\n\t<thead>\n\t\t<tr>\n\t\t\t<td>TestCase</td>\n\t\t\t<td>Status</td>\n\t\t\t<td>Show</td>'
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
                partlist.append((part, filename, funcname))
                outdict['block'+partlist[-1][0]+'00'] = True
                self._coverage[partlist[-1][1]][partlist[-1][2]]['result']['block'+partlist[-1][0]+'00'] = True
                i = k + 1
            elif text[i] == '#':
                outdict['block'+partlist[-1][0]+text[i+1:i+3]] = True
                self._coverage[partlist[-1][1]][partlist[-1][2]]['result']['block'+partlist[-1][0]+text[i+1:i+3]] = True
                i += 3
            elif text[i] == '@':
                outdict['block'+partlist[-1][0]+text[i+1:i+3]] = True
                self._coverage[partlist[-1][1]][partlist[-1][2]]['result']['block'+partlist[-1][0]+text[i+1:i+3]] = True
                i += 3
                partlist.pop()
            else:
                cid = 'cond'+partlist[-1][0]+text[i:i+2]
                self._coverage[partlist[-1][1]][partlist[-1][2]]['result'].setdefault('cond'+partlist[-1][0]+text[i:i+2], 0)
                outdict.setdefault(cid, 0)
                if text[i+2] == 'T':
                    outdict[cid] = outdict[cid] | 2
                    self._coverage[partlist[-1][1]][partlist[-1][2]]['result']['cond'+partlist[-1][0]+text[i:i+2]] = self._coverage[partlist[-1][1]][partlist[-1][2]]['result']['cond'+partlist[-1][0]+text[i:i+2]] | 2
                else:
                    outdict[cid] = outdict[cid] | 1
                    self._coverage[partlist[-1][1]][partlist[-1][2]]['result']['cond'+partlist[-1][0]+text[i:i+2]] = self._coverage[partlist[-1][1]][partlist[-1][2]]['result']['cond'+partlist[-1][0]+text[i:i+2]] | 1
                i += 3
        return outdict

class CBatch(object):
    # 使用VS2005Professional批量测试
    def __init__(self, conffile='batchList.txt'):
        self._loadConf(conffile)
    def _loadConf(self, conffile):
        # 读取配置文件
        #   配置文件第一有效行为代码路径
        #   配置文件第二有效行为工程文件路径
        #   配置文件第三有效行开始为测试用例文件
        fh = openTextFile(('cp932','cp936'), conffile, 'r')
        self._csv = []
        rdidx = 0
        for line in fh.readlines():
            line = line.strip()
            if len(line)>0:
                if line[0] in ('#',';'):
                    pass
                else:
                    rdidx += 1
                    if rdidx == 1:
                        self._src = line
                    elif rdidx == 2:
                        self._sln = line
                    else:
                        if os.path.isfile(line):
                            self._csv.append(line)
        fh.close()
    def batch(self, outfile='batch.bat', rebuild_first=False, waittime=5):
        fh = open(outfile, 'w')
        fh.write('''@echo off
set devenv="%VS80COMNTOOLS%..\\IDE\\devenv"
set sln="{}"

'''.format(self._sln))
        for idx,item in enumerate(self._csv):
            if idx == 0 and rebuild_first:
                fh.write('''echo {0}
python modify.py {0} {1}
%devenv% %sln% /Rebuild
%devenv% %sln% /RunExit
ping -n {2} 127.0.0.1 >nul
python result.py
call restore.bat

'''.format(item, self._src, waittime))
            else:
                fh.write('''echo {0}
python modify.py {0} {1}
%devenv% %sln% /Build
%devenv% %sln% /RunExit
ping -n {2} 127.0.0.1 >nul
python result.py
call restore.bat

'''.format(item, self._src, waittime))
        fh.write('@echo on\n')
        fh.close()

class WinAMS(object):
    # 本class需要完成的任务：
    # 1. 测试用例读取，生成测试入口函数
    # 2. 生成代码还原用的批处理文件(restore.bat)
    # 3. 生成Html报告的配置文件(report.conf)
    # WinAMS测试用例文件格式说明
    # 1. 采用csv格式保存
    # 2. 第一行第一列是"mod",第二列是目标函数名，第三列是函数编号，第四列是输入个数，第五列是输出个数
    # 3. 第一列是"#COMMENT"的行，从第二列开始依次是输入和输出变量名
    #    以"@"开头的变量是目标函数的参数（目标函数的static变量无法处理，跳过），变量名与函数定义一致
    #    以"@@"结尾的变量是目标函数的返回值，变量名是函数名
    #    "函数名@变量名"是dummy函数的参数/返回值/内部static变量的值（无法处理，跳过；解决方法：dummy函数也使用全局变量）
    # 4. 第一列是没有内容的行，是测试用例，从第二列开始依次是输入变量的设定值和输出变量的期待值
    #    对于数组的整体赋值，值之间用"|"分隔，重复数据用"data|*count"的形式
    CSVInfo = collections.namedtuple('CSVInfo',['funcname','funcno','icount','ocount','stub','var','case','ret','param'])
    def __init__(self, resultdir='csvfile'):
        # @resultdir funcname, funcno, csvfile
        resultdir = resultdir.lower()
        if resultdir not in ('funcname', 'funcno', 'csvfile'):
            self._resultdir = 'funcname'
        else:
            self._resultdir = resultdir
    def test(self, csvfile, rootpath):
        self._loadCSV(csvfile)
        inputinfo = [
                     {'function':self.csvinfo.funcname,
                      'dummy':self.csvinfo.stub
                     },
                    ]
        ct = CTest(rootpath)
        ct.inject(inputinfo)
        appendfuncs = []
        svarlist = {}
        flag_stripWinAMS = False
        for fname in ct.staticdetail.keys():
            if len(ct.staticdetail[fname].keys()) > 0:
                appendfuncs.append(os.path.splitext(os.path.basename(fname))[0])
                for key,value in ct.staticdetail[fname].items():
                    if key == self.csvinfo.funcname:
                        varprefix = '@'
                    else:
                        varprefix = key+'@'
                    if flag_stripWinAMS and key.startswith('AMSTB_'):
                        varprefix2 = 's'+key[len('AMSTB_'):]+'_'
                    else:
                        varprefix2 = 's'+key+'_'
                    for subvalue in value:
                        csvvar = varprefix + subvalue
                        if flag_stripWinAMS and subvalue.startswith('AM'):
                            srcvar = varprefix2 + subvalue[subvalue.find('_')+1:]
                        else:
                            srcvar = varprefix2 + subvalue
                        svarlist.setdefault(fname,[]).append((csvvar, srcvar))
        for fname in ct.funcdetail.keys():
            for item in ct.funcdetail[fname]:
                if item[0][0] == self.csvinfo.funcname:
                    self._writeTestFunc(fname, item, appendfuncs)
                    testfile = fname
                    break
        for fname in ct.staticdetail.keys():
            if len(ct.staticdetail[fname].keys()) > 0:
                if fname == testfile:
                    self._writeAccessFunc(fname, svarlist[fname], True)
                else:
                    self._writeAccessFunc(fname, svarlist[fname])
        fnames = [os.path.abspath(x) for x in ct.funcdetail.keys()]
        self._restore(fnames)
    def _restore(self, filenames, conffile='report.conf', outfile='restore.bat'):
        htmltitle = self.csvinfo.funcname
        #htmlfile = os.path.abspath(self.csvinfo.funcno + '.html')
        #resultfile = os.path.abspath(self.csvinfo.funcno+'.txt')
        htmlfile = self.csvinfo.funcno + '.html'
        resultfile = self.csvinfo.funcno+'.txt'
        fh = open(conffile, 'w')
        fh.write(htmltitle+'\n')
        fh.write(htmlfile+'\n')
        fh.write(resultfile+'\n')
        #fh.write('\n'.join([os.path.abspath(os.path.basename(x)) for x in filenames]))
        fh.write('\n'.join([os.path.basename(x) for x in filenames]))
        fh.close()

        curfolder = os.path.abspath('.')
        curdriver = os.path.splitdrive(curfolder)[0]
        srcdriver = os.path.splitdrive(os.path.abspath(filenames[0]))[0]
        fh = open(outfile, 'w')
        fh.write('@echo off\n')
        fh.write('{}\n'.format(srcdriver))
        for fname in filenames:
            srcfolder,srcfile = os.path.split(fname)
            fh.write('cd "{}"\n'.format(srcfolder))
            fh.write('copy {0}.org {0}\n'.format(srcfile)) # 还原代码文件
            fh.write('copy /B {0} +\n'.format(srcfile))    # 更新还原后代码文件的时间戳
            fh.write('del {0}.org\n'.format(srcfile))      # 删除备份文件
        fh.write('{}\n'.format(curdriver))
        fh.write('cd "{}"\n'.format(curfolder))

        if self._resultdir == 'csvfile':
            resultdir = os.path.splitext(os.path.basename(self.csvfile))[0]
        elif self._resultdir == 'funcname':
            resultdir = htmltitle
        else:
            resultdir = self.csvinfo.funcno
        fh.write('mkdir {}\n'.format(resultdir))
        fh.write('del /f /q {}\\*.*\n'.format(resultdir))
        fh.write('copy "{}" {}\\\n'.format(self.csvfile, resultdir))
        fh.write('move {} {}\\\n'.format(conffile, resultdir))
        fh.write('move {} {}\\\n'.format(htmlfile,resultdir))
        fh.write('move {} {}\\\n'.format(resultfile,resultdir))
        for fname in filenames:
            fh.write('move {} {}\\\n'.format(os.path.basename(fname),resultdir))

        fh.write('del {}\n'.format(outfile))
        fh.write('@echo on\n')
        fh.close()
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
                if len(targetno.strip()) <= 2:
                    targetno = targetfunc
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
                        var.append(x)
                        paramflag = True
                    else:
                        var.append(x)
            elif row[0] == '':
                # 测试用例
                row[0] = rowidx + 1
                case.append(tuple(row))
        fh.close()
        self.csvfile = os.path.normpath(os.path.abspath(csvfile))
        self.csvinfo = self.CSVInfo(funcname = targetfunc,
                                    funcno   = targetno,
                                    icount   = count_in,
                                    ocount   = count_out,
                                    stub     = stub,
                                    var      = var,
                                    case     = case,
                                    ret      = retflag,
                                    param    = paramflag)
    def _writeAccessFunc(self, modfile, svarlist, noinclude=False):
        fh = openTextFile(('cp932','cp936'), modfile, 'a')
        funcname = os.path.splitext(os.path.basename(modfile))[0]
        if not noinclude:
            fh.write('#include <stdio.h>\n')
        fh.write('void i{}(int idx)\n'.format(funcname))
        fh.write('{\n')
        for i in range(len(self.csvinfo.case)):
            if i == 0:
                fh.write('    if (idx == {}) \n'.format(i))
            else:
                fh.write('    else if (idx == {}) \n'.format(i))
            fh.write('    {\n')
            fh.write('        /* TestCase {} */\n'.format(self.csvinfo.case[i][0]))
            for j in range(self.csvinfo.icount):
                if '@' in self.csvinfo.var[j+1]:
                    varname = self.csvinfo.var[j+1]
                    for k in range(len(svarlist)):
                        varname = re.sub(r'\b'+svarlist[k][0]+r'\b', svarlist[k][1], varname)
                    if varname != self.csvinfo.var[j+1]:
                        if '|' in self.csvinfo.case[i][j+1]:
                            vallist = []
                            for xx in self.csvinfo.case[i][j+1].split('|'):
                                xx = xx.strip()
                                if xx.startswith('*'):
                                    xxcnt = int(xx[1:])
                                    xxval = vallist[-1]
                                    vallist.extend([xxval,]*xxcnt)
                                else:
                                    vallist.append(xx)
                        else:
                            vallist = [self.csvinfo.case[i][j+1].strip()]
                        if len(vallist) == 1:
                            fh.write('        {} = {};\n'.format(varname,vallist[0]))
                        else:
                            for xxi in range(len(vallist)):
                                fh.write('        {}[{}] = {};\n'.format(varname,xxi,vallist[xxi]))
            fh.write('    }\n')
        fh.write('}\n')
        fh.write('void o{}(int idx, FILE *fp)\n'.format(funcname))
        fh.write('{\n')
        for i in range(len(self.csvinfo.case)):
            if i == 0:
                fh.write('    if (idx == {}) \n'.format(i))
            else:
                fh.write('    else if (idx == {}) \n'.format(i))
            fh.write('    {\n')
            for j in range(self.csvinfo.ocount):
                if '@' in self.csvinfo.var[self.csvinfo.icount+j+1]:
                    varname = self.csvinfo.var[self.csvinfo.icount+j+1]
                    for k in range(len(svarlist)):
                        varname = re.sub(r'\b'+svarlist[k][0]+r'\b', svarlist[k][1], varname)
                    if varname != self.csvinfo.var[self.csvinfo.icount+j+1]:
                        if self.csvinfo.case[i][self.csvinfo.icount + j + 1].strip() != '':
                            fh.write('        fprintf(fp, "{0} = %d, %d\\n", {1}, {0});\n'.format(varname, self.csvinfo.case[i][self.csvinfo.icount + j + 1]))
                        else:
                            fh.write('        fprintf(fp, "{0} = %d\\n", {0});\n'.format(varname))
            fh.write('    }\n')
        fh.write('}\n')
        fh.close()
    def _writeTestFunc(self, modfile, funcdetail, appendfuncs):
        fh = open(modfile, 'a', encoding='utf_8_sig')
        fh.write('#include <stdio.h>\n')
        fh.write('#include <stdlib.h>\n')
        fh.write('#include <string.h>\n')
        for appfunc in appendfuncs:
            fh.write('extern void i{}(int idx);\n'.format(appfunc))
            fh.write('extern void o{}(int idx, FILE *fp);\n'.format(appfunc))
        fh.write('void TestMain()\n')
        fh.write('{\n')
        fh.write('    int _g_test_i_;\n')
        # 测试目标函数的参数和返回值
        if self.csvinfo.ret:
            fh.write('    '+funcdetail[0][1]+' '+funcdetail[0][0]+'__ret;\n')
        if len(funcdetail) > 1:
            paramptn = re.compile(r'\b('+'|'.join([x[0] for x in funcdetail[1:]])+r')\b')
        else:
            paramptn = re.compile(r'#@#')
        for i in range(len(funcdetail)-1):
            fh.write('    '+funcdetail[i+1][1]+';\n')
        fh.write('    FILE *fp;\n')
        resultfile = os.path.abspath(self.csvinfo.funcno+'.txt').replace('\\','\\\\')
        fh.write('    fopen_s(&fp, "{}", "wt");\n'.format(resultfile))
        fh.write('    for (_g_test_i_ = 0; _g_test_i_ < {}; ++_g_test_i_)\n'.format(len(self.csvinfo.case)))
        fh.write('    {\n')
        fh.write('        /* initialize */\n')
        fh.write('        _dmy_index = 0;\n')
        fh.write('        memset(&_dmy_record[0], 0, _dmy_size);\n')
        for i in range(len(self.csvinfo.case)):
            if i == 0:
                fh.write('        if (_g_test_i_ == {}) \n'.format(i))
            else:
                fh.write('        else if (_g_test_i_ == {}) \n'.format(i))
            fh.write('        {\n')
            fh.write('            /* TestCase {} */\n'.format(self.csvinfo.case[i][0]))
            for j in range(self.csvinfo.icount):
                if '|' in self.csvinfo.case[i][j+1]:
                    vallist = []
                    for xx in self.csvinfo.case[i][j+1].split('|'):
                        xx = xx.strip()
                        if xx.startswith('*'):
                            xxcnt = int(xx[1:])
                            xxval = vallist[-1]
                            vallist.extend([xxval,]*xxcnt)
                        else:
                            vallist.append(xx)
                else:
                    vallist = [self.csvinfo.case[i][j+1].strip()]
                if self.csvinfo.var[j+1].startswith('@'):
                    if paramptn.search(self.csvinfo.var[j+1]):
                        if len(vallist) == 1:
                            fh.write('            {} = {};\n'.format(self.csvinfo.var[j+1][1:],vallist[0]))
                        else:
                            for xxi in range(len(vallist)):
                                fh.write('            {}[{}] = {};\n'.format(self.csvinfo.var[j+1][1:],xxi,vallist[xxi]))
                    else:
                        # 目标函数的static变量
                        pass
                elif '@' in self.csvinfo.var[j+1]:
                    # dummy函数的参数/返回值/内部static变量的值
                    pass
                else:
                    if len(vallist) == 1:
                        fh.write('            {} = {};\n'.format(self.csvinfo.var[j+1],vallist[0]))
                    else:
                        for xxi in range(len(vallist)):
                            fh.write('            {}[{}] = {};\n'.format(self.csvinfo.var[j+1],xxi,vallist[xxi]))
            fh.write('        }\n')
        for appfunc in appendfuncs:
            fh.write('        i{}(_g_test_i_);\n'.format(appfunc))
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
                fh.write('        if (_g_test_i_ == {}) \n'.format(i))
            else:
                fh.write('        else if (_g_test_i_ == {}) \n'.format(i))
            fh.write('        {\n')
            fh.write('            fprintf(fp, ";TestCase {}\\n");\n'.format(self.csvinfo.case[i][0]))
            for j in range(self.csvinfo.ocount):
                if self.csvinfo.var[self.csvinfo.icount+j+1].startswith('@'):
                    if self.csvinfo.case[i][self.csvinfo.icount + j + 1].strip() != '':
                        fh.write('            fprintf(fp, "{0} = %d, %d\\n", {1}, {0});\n'.format(self.csvinfo.var[self.csvinfo.icount + j + 1][1:], self.csvinfo.case[i][self.csvinfo.icount + j + 1]))
                    else:
                        fh.write('            fprintf(fp, "{0} = %d\\n", {0});\n'.format(self.csvinfo.var[self.csvinfo.icount + j + 1][1:]))
                elif '@' in self.csvinfo.var[self.csvinfo.icount+j+1]:
                    # dummy函数的参数/返回值/内部static变量的值
                    pass
                else:
                    if self.csvinfo.case[i][self.csvinfo.icount + j + 1].strip() != '':
                        fh.write('            fprintf(fp, "{0} = %d, %d\\n", {1}, {0});\n'.format(self.csvinfo.var[self.csvinfo.icount + j + 1], self.csvinfo.case[i][self.csvinfo.icount + j + 1]))
                    else:
                        fh.write('            fprintf(fp, "{0} = %d\\n", {0});\n'.format(self.csvinfo.var[self.csvinfo.icount + j + 1]))
            fh.write('        }\n')
        for appfunc in appendfuncs:
            fh.write('        o{}(_g_test_i_, fp);\n'.format(appfunc))
        fh.write('        /* write track info */\n')
        fh.write('        fprintf(fp, "#Track = %s\\n", _dmy_record);\n')
        fh.write('    }\n')
        fh.write('    fclose(fp);\n')
        fh.write('}\n')
        fh.close()
