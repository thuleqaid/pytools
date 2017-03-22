# -*- coding:utf-8 -*-
## 输入：路径1，路径2，文件过滤字符串
## 输出：html路径，临时路径
## 1. 在临时路径中生成脚本1（比较目录）
## 2. 使用脚本1比较目录，生成html结果（html路径）及文本结果（临时路径）
## 3. 根据文本结果生成脚本2（比较各个差分文件）
## 4. 使用脚本2比较文件
## 5. 修改目录比较html结果
##    图片base64化，嵌入html文件中
##    增加到文件比较结果的链接
## 6. 修改文件比较html结果
##    增加差异区分列
## 7. 删除临时路径及BComp的图片目录
import os
import sys
import re
import base64
import shutil
import xml.parsers.expat
import ToExcel
from collectscript import logutil, guess, multiprocess

if hasattr(sys, 'frozen'):
    SELFPATH = logutil.scriptPath(sys.executable)
else:
    SELFPATH = logutil.scriptPath(__file__)
LOGCONFIG = os.path.join(SELFPATH, 'logging.conf')

LOGNAME = "FolderCompare"
logutil.registerLogger(LOGNAME)

class FolderCompare(object):
    DEFAULT_SUMMARY = "report.html"
    DEFAULT_FILTER = "*.*"
    DEFAULT_SCRIPT0 = '''log verbose "{logpath}"
'''
    DEFAULT_SCRIPT1 = '''load "{path1}" "{path2}"
expand all
filter "{filter}"
criteria binary
folder-report layout:side-by-side options:display-mismatches,column-size,column-timestamp title:"{title}" output-to:"{summary1}" output-options:html-color
folder-report layout:xml options:display-all,column-size,column-timestamp title:"title" output-to:"{summary2}"
'''
    DEFAULT_SCRIPT2 = '''file-report layout:side-by-side options:display-all,line-numbers title:"{title}" output-to:"{outfile}" output-options:html-color "{source1}" "{source2}"
'''
    def __init__(self):
        self._log = logutil.LogUtil().logger(LOGNAME)
        self._script0 = self.DEFAULT_SCRIPT0
        self._script1 = self.DEFAULT_SCRIPT1
        self._script2 = self.DEFAULT_SCRIPT2
        self._filter = self.DEFAULT_FILTER
        self._summaryfile = self.DEFAULT_SUMMARY
        self._exepath = ''
        self._path1 = ''
        self._path2 = ''
        self._outpath = ''
        self._tmppath = ''
        self._xmlstatus = ''
        self._xmllevel = 0
        self._xmlpath = []
        self._xmldirpath = []
        self._xmlresult = {}
    def setBComp(self, exepath):
        path = os.path.abspath(exepath)
        if os.path.isfile(path):
            self._exepath = path
            self._log.log(20, "Set BeyondCompare Path: {}".format(self._exepath))
        else:
            self._exepath = ''
            self._log.log(20, "Set BeyondCompare Path: Failed")
    def setPath(self, path1, path2, outpath, tmppath):
        self._path1 = os.path.abspath(path1)
        self._path2 = os.path.abspath(path2)
        self._outpath = os.path.abspath(outpath)
        self._tmppath = os.path.abspath(tmppath)
        self._log.log(20, "Source Path 1:{}".format(self._path1))
        self._log.log(20, "Source Path 2:{}".format(self._path2))
        self._log.log(20, "Output Path:{}".format(self._outpath))
        self._log.log(20, "Temp Path:{}".format(self._tmppath))
    def setFilter(self, filter):
        if filter == "":
            self._filter = self.DEFAULT_FILTER
        else:
            self._filter = filter
        self._log.log(20, "Set File Filter:{}".format(self._filter))
    def setSummaryFile(self, summary):
        self._summaryfile = summary
        self._log.log(20, "Set Summary File:{}".format(self._summaryfile))
    def run1(self):
        # Compare folders and output summary report
        self._log.log(20, "Generate Script 1")
        self._genScript1()
        mp = multiprocess.MultiProcess()
        exeinfo = [self._exepath, '@{}'.format(os.path.join(self._tmppath, 'script1.txt'))]
        self._log.log(20, "Run Script 1")
        mp.run(exeinfo)
        self._log.log(20, "Generate Script 2")
        self._genScript2(True)
    def run2(self):
        # Compare each different files
        self._log.log(20, "Generate Script 2 if not exists")
        self._genScript2()
        mp = multiprocess.MultiProcess()
        exeinfo = [self._exepath, '@{}'.format(os.path.join(self._tmppath, 'script2.txt'))]
        self._log.log(20, "Run Script 2")
        mp.run(exeinfo)
    def run3(self):
        # Patch summary report
        self._log.log(20, "Patch Summary File:{}".format(os.path.join(self._outpath,self._summaryfile)))
        # load report file
        fh = guess.openTextFile(os.path.join(self._outpath, self._summaryfile), 'r')
        data = fh.read()
        fh.close()
        # patch report file
        pat_tr = re.compile(r'<tr class="Section(Begin|Middle|End)">(?P<content>(.|\n)*?)</tr>')
        pat_td = re.compile(r'<td class="(?P<class>.*?)">(?P<content>.*?)</td>')
        col1, col2 = 0, 0
        dirinfo = [[], []]
        newdata = ''
        lastpos = 0
        imagedata = {}
        for item in pat_tr.finditer(data):
            if col2 <= col1:
                # get column index for the filename of right side
                subitems = pat_td.findall(item.group('content'))
                col2 = len(subitems) // 2 + 1
            newdata += data[lastpos:item.start('content')]
            content = item.group('content')
            sublastpos = 0
            for subidx, subitem in enumerate(pat_td.finditer(content)):
                curtdtext = content[sublastpos:subitem.end(0)]
                if subidx == col1:
                    info = self._patchSummaryTd(subitem.group('class'), subitem.group('content'))
                    didx = 0
                elif subidx == col2:
                    info = self._patchSummaryTd(subitem.group('class'), subitem.group('content'))
                    didx = 1
                elif subidx == col2 - 1:
                    info = self._patchSummaryTd(subitem.group('class'), subitem.group('content'))
                    didx = 2
                else:
                    didx = -1
                if 0 <= didx <= 1:
                    if info['is_dir']:
                        if info['level'] < len(dirinfo[didx]):
                            dirinfo[didx][info['level']:] = [info['name']]
                        else:
                            dirinfo[didx].append(info['name'])
                    else:
                        if info['level'] < len(dirinfo[didx]):
                            dirinfo[didx] = dirinfo[didx][0:info['level']]
                    if info['link_target']:
                        # add html link
                        link_target = os.path.join(*dirinfo[didx],info['name']+".html").replace("\\", "/")
                        if os.path.isfile(os.path.join(self._outpath, link_target)):
                            curtdtext = curtdtext.replace(info['name'], '<a href="{}" target="_blank">{}</a>'.format(link_target, info['name']))
                    # embed image data
                    for img in info['image']:
                        if img not in imagedata:
                            fh = open(os.path.join(self._outpath, img), 'rb')
                            idata = fh.read()
                            fh.close()
                            imagedata[img] = 'data:image/png;base64,'+base64.b64encode(idata).decode()
                        curtdtext = curtdtext.replace(img, imagedata[img])
                elif didx == 2:
                    # embed image data
                    for img in info['image']:
                        if img not in imagedata:
                            fh = open(os.path.join(self._outpath, img), 'rb')
                            idata = fh.read()
                            fh.close()
                            imagedata[img] = 'data:image/png;base64,'+base64.b64encode(idata).decode()
                        curtdtext = curtdtext.replace(img, imagedata[img])
                newdata += curtdtext
                sublastpos = subitem.end(0)
            newdata += content[sublastpos:]
            newdata += data[item.end('content'):item.end(0)]
            lastpos = item.end(0)
        newdata += data[lastpos:]
        fh = open(os.path.join(self._outpath, self._summaryfile), 'w', encoding='utf-8')
        fh.write(newdata)
        fh.close()
        # remove image files
        img = tuple(imagedata.keys())
        if len(img) > 0:
            imgpath = os.path.join(self._outpath, img[0])
            shutil.rmtree(os.path.dirname(imgpath))
    def run4(self, neighbors=5):
        # Patch individual diff file
        if len(self._xmlresult) <= 0:
            self._parseXml()
        for item in self._xmlresult.get('diff', ()):
            fname = os.path.join(self._outpath, item+".html")
            self._patchHtml(fname, neighbors)
        for item in self._xmlresult.get('ltonly', ()):
            fname = os.path.join(self._outpath, item+".html")
            self._patchHtml(fname, neighbors)
        for item in self._xmlresult.get('rtonly', ()):
            fname = os.path.join(self._outpath, item+".html")
            self._patchHtml(fname, neighbors)
    def run5(self):
        shutil.rmtree(self._tmppath)
    def runExcel(self):
        summary = os.path.join(self._outpath, self._summaryfile)
        outxlsm = os.path.splitext(summary)[0] + '.xlsm'
        outxlsx = os.path.splitext(summary)[0] + '.xlsx'
        tmpl = os.path.join(SELFPATH, 'tmpl.xlsm')
        ToExcel.toExcel(self._outpath, outxlsm, outxlsx, tmpl, [summary,])
    def _patchSummaryTd(self, tdclass, tdtext):
        pat_img = re.compile(r'<img src="(?P<image>.*?)".*?\balt="(?P<alt>.*?)".*?>')
        pos, imgcount = 0, -1
        flag_dir = False
        images = []
        for idx, item in enumerate(pat_img.finditer(tdtext)):
            images.append(item.group('image'))
            if item.group('alt') == '<DIR>' and 'zip' not in images[-1].lower():
                flag_dir = True
            pos = item.end(0)
            imgcount = idx
        if not flag_dir:
            imgcount += 1
        flag_target = ("DirItemDiff" in tdclass) or ("DirItemOrphan" in tdclass)
        return {'link_target': flag_target,
                'level':imgcount,
                'name':tdtext[pos:].strip(),
                'is_dir':flag_dir,
                'image':set(images)}
    def _patchHtml(self, fname, neighbors):
        self._log.log(20, "Patch Html File:{}".format(fname))
        fh = guess.openTextFile(fname, 'r')
        lines = fh.readlines()
        fh.close()
        ptn_tr = re.compile(r'^<tr class="')
        ptn_td = re.compile(r'^<td class=".*?\bAlignCenter\b.*?">(?P<compare>.*?)</td>')
        linelist = []
        complist = []
        for idx in range(len(lines)):
            ret1 = ptn_tr.search(lines[idx])
            ret2 = ptn_td.search(lines[idx])
            if ret1:
                linelist.append(idx)
            elif ret2:
                comp = ret2.group('compare')
                if comp == '=':
                    complist.append(0)
                elif comp == '&nbsp;':
                    complist.append(complist[-1])
                else:
                    complist.append(neighbors)
        self._log.log(10, "Linelist:{}".format(repr(linelist)))
        self._log.log(10, "Complist:{}".format(repr(complist)))
        for i in range(1, len(complist)):
            complist[i] = max(complist[i], complist[i-1] - 1)
        for i in range(len(complist)-2, 0, -1):
            complist[i] = max(complist[i], complist[i+1] - 1)
        self._log.log(10, "Adjusted Complist:{}".format(repr(complist)))
        for i in range(len(linelist)-1, -1, -1):
            lines.insert(linelist[i]+1, '<td class="TextItemNum AlignRight">{}</td>'.format(complist[i]))
        fh = open(fname, 'w', encoding='utf-8')
        fh.writelines(lines)
        fh.close()
    def _genScript1(self, title="Folder Compare Report"):
        fname = os.path.join(self._tmppath, 'script1.txt')
        info = {'path1':self._path1,
                'path2':self._path2,
                'filter':self._filter,
                'title':title,
                'summary1':os.path.join(self._outpath, self._summaryfile),
                'summary2':os.path.join(self._tmppath, 'report.xml')
        }
        if not os.path.isdir(self._tmppath):
            os.makedirs(self._tmppath)
        if not os.path.isdir(self._outpath):
            os.makedirs(self._outpath)
        with open(fname, 'w', encoding='utf-8') as fh:
            fh.write(self._script0.format(logpath=os.path.join(self._tmppath, 'log1.txt')))
            fh.write(self._script1.format(**info))
    def _genScript2(self, force = False):
        fname = os.path.join(self._tmppath, 'script2.txt')
        if (not force) and os.path.isfile(fname):
            return
        self._parseXml()
        with open(fname, 'w', encoding='utf-8') as fh:
            fh.write(self._script0.format(logpath=os.path.join(self._tmppath, 'log2.txt')))
            for item in self._xmlresult.get('diff', ()):
                info = {'title':item,
                        'source1':os.path.join(self._path1, item),
                        'source2':os.path.join(self._path2, item),
                        'outfile':os.path.join(self._outpath, item+".html")
                }
                fh.write(self._script2.format(**info))
            fh.write('## Old olny\n')
            for item in self._xmlresult.get('ltonly', ()):
                info = {'title':item,
                        'source1':os.path.join(self._path1, item),
                        'source2':'XXXUnKnownXXX',
                        'outfile':os.path.join(self._outpath, item+".html")
                }
                fh.write('#' + self._script2.format(**info))
            fh.write('## New olny\n')
            for item in self._xmlresult.get('rtonly', ()):
                info = {'title':item,
                        'source1':'XXXUnKnownXXX',
                        'source2':os.path.join(self._path2, item),
                        'outfile':os.path.join(self._outpath, item+".html")
                }
                fh.write('#' + self._script2.format(**info))
    def _xml_start_element(self, name, attrs):
        self._xmlpath.append(name)
        status = attrs.get('status', '')
        if status != '':
            self._xmlstatus = status
            self._xmllevel = len(self._xmlpath)
        if name == 'foldercomp':
            self._xmldirpath.append('')
    def _xml_end_element(self, name):
        if len(self._xmlpath) == self._xmllevel:
            self._xmllevel = 0
            self._xmlstatus = ''
        self._xmlpath.pop(-1)
        if name == 'foldercomp':
            self._xmldirpath.pop(-1)
    def _xml_char_data(self, data):
        if len(self._xmlpath) > 3 and self._xmlpath[-1] == 'name':
            if self._xmlpath[-3] == 'foldercomp':
                if self._xmlpath[-2] in ('lt', 'rt'):
                    self._xmldirpath[-1] = data
            elif self._xmlpath[-3] == 'filecomp':
                if self._xmlpath[-2] in ('lt', 'rt'):
                    self._xmlresult.setdefault(self._xmlstatus, set()).add(os.path.join(*self._xmldirpath, data))
    def _parseXml(self):
        p = xml.parsers.expat.ParserCreate()
        p.StartElementHandler = self._xml_start_element
        p.EndElementHandler = self._xml_end_element
        p.CharacterDataHandler = self._xml_char_data
        fh =guess.openTextFile(os.path.join(self._tmppath, 'report.xml'), 'r')
        data = fh.read()
        fh.close()
        self._xmlstatus = ''
        self._xmllevel = 0
        self._xmlpath = []
        self._xmldirpath = []
        self._xmlresult = {}
        p.Parse(data, 1)

if __name__ == '__main__':
    logutil.logConf(LOGCONFIG)
    logutil.LogUtil(LOGCONFIG)
    path1 = r'd:\temp\17M_ARM-5.07.0.07\00_BasePlatform'
    path2 = r'd:\temp\17M_ARM-5.08.0.06\00_BasePlatform'
    # path1 = r'd:\temp\17M_ARM-5.07.0.07'
    # path2 = r'd:\temp\17M_ARM-5.08.0.06'
    path3 = r'd:\temp\AAA'
    path4 = r'd:\temp\BBB'
    fc = FolderCompare()
    fc.setPath(path1, path2, path3, path4)
    fc.setBComp(r'c:\Program Files\Beyond Compare 3\BCompare.exe')
    fc.run1()
    fc.run2()
    fc.run3()
    fc.run4()
    fc.run5()
