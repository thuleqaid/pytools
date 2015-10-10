# -*- coding:utf-8 -*-
import sys
import logutil
import encodechanger

FILTER_LIST = (('C/C++ Files',r'\.(c|c\+\+|cc|cp|cpp|cxx|h|h\+\+|hh|hp|hpp|hxx)$'),
               ('Python Files', r'\.(py|pyx|pxd|pxi|scons)$'),
              )
if __name__ == '__main__':
    #logutil.newConf(('EncodeChanger',))
    ec = encodechanger.EncodeChanger()
    ec.vcs = True
    ec.copyother = True
    ec.srcdir = 'd:/work_files/AB0100_SRC/ECUSAR'
    ec.dstdir = 'd:/work_files/AB0100_SRC/ECUSAR2'
    ec.regex = FILTER_LIST[0][1]
    ec.newline = 'unix'
    ec.outcode = 'utf_8_sig'
    ec.incode = ('cp932', 'cp936')
    ec.translate()
