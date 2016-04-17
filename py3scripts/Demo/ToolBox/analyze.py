# -*- coding:utf-8 -*-
from collectscript import guess, tagparser
import os
import collections

class ExtractInline(object):
    # 抽取inline子函数情报
    # 输入参数：
    #   代码根目录（用于提取函数调用关系）
    #   测试目标函数列表
    #   inline函数列表（未指定时，使用自动解析结果）
    # 输出格式：
    #   第一列是测试目标函数，第二列是inline子函数，第三列是inline子函数的调用次数
    #   如果2n列的函数调用了inline子函数，则添加2n+1和2n+2列数据
    #   同一个函数调用了多个函数时，只在第一行写函数名
    #   测试目标函数没有调用inline子函数时，第二列为空
    def __init__(self, srcroot):
        cscopefile = os.path.abspath(os.path.join(srcroot, 'cscope.out'))
        self._cscope = tagparser.CscopeParser(cscopefile, sourceparser=tagparser.cscopeSourceParserEPS)
        self._targets = ()
        self._inlines = ()
    def setTargetFile(self, targetfile):
        funcs = self._readTextFile(targetfile)
        self.setTargetFuncs(funcs)
    def setTargetFuncs(self, targetfuncs):
        self._targets = tuple(targetfuncs)
    def setInlineFile(self, inlinefile):
        funcs = self._readTextFile(inlinefile)
        self.setInlineFuncs(funcs)
    def setInlineFuncs(self, inlinefuncs):
        self._inlines = tuple(inlinefuncs)
    def outputInline(self, outfile):
        inlinefuncs = set()
        for item in self._cscope._funcs:
            if item.extra.get('Inline', 0) > 0:
                inlinefuncs.add(item.name)
        fh = open(outfile, 'w')
        for item in sorted(inlinefuncs):
            fh.write('{}\n'.format(item))
        fh.close()
    def outputMetric(self, outfile):
        if len(self._inlines) <= 0:
            # inline函数列表（未指定时，使用自动解析结果）
            inlinefuncs = []
            for item in self._cscope._funcs:
                if item.extra.get('Inline', 0) > 0:
                    inlinefuncs.append(item.name)
            self._inlines = tuple(inlinefuncs)
        # 输出需要度量数据的函数一览
        fh = open(outfile, 'w')
        for item in self._targets:
            fh.write('{}\n'.format(item))
        for item in sorted(set(self._inlines)):
            if item not in self._targets:
                fh.write('{}\n'.format(item))
        fh.close()
    def outputTree(self, outfile):
        if len(self._inlines) <= 0:
            # inline函数列表（未指定时，使用自动解析结果）
            inlinefuncs = []
            for item in self._cscope._funcs:
                if item.extra.get('Inline', 0) > 0:
                    inlinefuncs.append(item.name)
            self._inlines = tuple(inlinefuncs)
        # 函数调用信息
        callinfo = {} # key: 函数名, value: {inline子函数名:调用次数, ... }
        for item in self._cscope._funcs:
            callinfo.setdefault(item.name, {})
            for sitem in item.calls:
                if sitem in self._inlines:
                    callinfo[item.name].setdefault(sitem, 0)
                    callinfo[item.name][sitem] += 1
        fh = open(outfile, 'w')
        for item in self._targets:
            fh.write('{}'.format(item))
            if item not in callinfo:
                fh.write('\n')
            elif len(callinfo[item].keys()) <= 0:
                fh.write('\n')
            else:
                for sidx, sitem in enumerate(sorted(callinfo[item].keys())):
                    fh.write('\t{}\t{}'.format(sitem, callinfo[item][sitem]))
                    self._recursiveOutput(fh, callinfo, 1, sitem)
        fh.close()
    def _readTextFile(self, filename):
        fh = guess.openTextFile(("cp932", "cp936"), filename, 'r')
        outlist = []
        for line in fh.readlines():
            line = line.strip()
            if line == '':
                continue
            if line.startswith('#'):
                continue
            outlist.append(line)
        fh.close()
        return outlist
    def _recursiveOutput(self, fhandle, callinfo, level, target):
        if target not in callinfo:
            fhandle.write('\n')
        elif len(callinfo[target].keys()) <= 0:
            fhandle.write('\n')
        else:
            for sidx, sitem in enumerate(sorted(callinfo[target].keys())):
                if sidx > 0:
                    fhandle.write('\t\t' * level)
                fhandle.write('\t{}\t{}'.format(sitem, callinfo[target][sitem]))
                self._recursiveOutput(fhandle, callinfo, level+1, sitem)

class SumMetrics(object):
    # 输入：
    #   ExtractInline()的输出文件
    #   各函数的Metrics数据文件（第一列是函数名，从第二列开始是整数度量信息）
    #   第二列开始度量数据的最小值（两行数据相加时会减去最小值）
    # 输出：
    #   Inline函数展开后的Metrics数据
    def __init__(self, inlinefile):
        self._minmetric = []
        self._metric = collections.OrderedDict()
        self._readInline(inlinefile)
    def outputFunctions(self, listfile):
        outset = set()
        outset.update(self._info.keys())
        for k,v in self._info.items():
            outset.update(v.keys())
        fh = open(listfile, 'w')
        for item in sorted(outset):
            fh.write('{}\n'.format(item))
        fh.close()
    def setMetrics(self, metricfile):
        info = collections.OrderedDict()
        fh = open(metricfile, 'r')
        for line in fh.readlines():
            parts = line.strip().split('\t')
            info[parts[0]] = []
            for x in parts[1:]:
                if x.isdigit():
                    info[parts[0]].append(int(x))
                else:
                    info[parts[0]].append(0)
        fh.close()
        self._metric = info
    def setMinMetrics(self, metrics):
        self._minmetric = list(metrics)
    def outputMetrics(self, metricfile):
        # 取得函数度量信息个数
        if len(self._metric) > 0:
            datalen = len(self._metric[list(self._metric.keys())[0]])
        else:
            datalen = 0
            return
        # 计算各个度量信息的最小值
        minmetriclen = len(self._minmetric)
        curmin = []
        for i in range(datalen):
            if i >= minmetriclen:
                curmin.append(0)
            else:
                if self._minmetric[i] >= 0:
                    curmin.append(self._minmetric[i])
                else:
                    curmin.append(0)
        # 累加度量信息
        for k in self._info.keys():
            if k in self._metric:
                for subk in self._info[k].keys():
                    if subk in self._metric:
                        for i in range(datalen):
                            op1 = self._metric[subk][i]
                            if op1 < curmin[i]:
                                op1 = curmin[i]
                            op1 *= self._info[k][subk]
                            op2 = self._metric[k][i]
                            if op2 < curmin[i]:
                                op2 = curmin[i]
                            self._metric[k][i] = op2 + op1
            else:
                pass
        fh = open(metricfile, 'w')
        for k in self._metric.keys():
            fh.write('{}\t{}\n'.format(k, '\t'.join([str(x) for x in self._metric[k]])))
        fh.close()
    def _readInline(self, infile):
        fh = open(infile, 'r')
        lines = []
        maxlen = 0
        for line in fh.readlines():
            parts =line.rstrip().split('\t')
            if len(parts) > maxlen:
                maxlen = len(parts)
            lines.append(list(parts))
        fh.close()
        linecnt = len(lines)
        # 为了保证顺序，使用有序字典，并且从最深的inline函数调用开始添加
        info = collections.OrderedDict()
        while maxlen >= 3:
            # 子函数名位置
            calleridx = maxlen - 2
            # 子函数被调用次数位置
            cntidx = maxlen -1
            # 父函数名位置
            if maxlen > 3:
                calleeidx = maxlen - 4
            else:
                calleeidx = maxlen - 3
            for idx in range(linecnt):
                if len(lines[idx]) >= maxlen:
                    if lines[idx][calleridx] != '' and lines[idx][cntidx] != '':
                        pidx = idx
                        while pidx >= 0:
                            if len(lines[pidx]) > calleeidx and lines[pidx][calleeidx] != '':
                                break
                            pidx -= 1
                        info.setdefault(lines[pidx][calleeidx], {})
                        info[lines[pidx][calleeidx]][lines[idx][calleridx]] = int(lines[idx][cntidx])
                    # 删除最深层子函数数据
                    lines[idx].pop()
                    lines[idx].pop()
                else:
                    pass
            maxlen -= 2
        self._info = info

if __name__ == '__main__':
    srcroot = 'd:/setup_pack/grape'
    targets = 'targets.txt'
    output = 'output.txt'
    metric = 'metricdata.txt'
    output2 = 'output2.txt'
    # ei = ExtractInline(srcroot)
    # ei.setTargetFile(targets)
    # ei.output(output)
    sm = SumMetrics(output)
    sm.setMetrics(metric)
    sm.outputMetrics(output2)
