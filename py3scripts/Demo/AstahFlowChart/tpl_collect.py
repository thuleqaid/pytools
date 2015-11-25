# -*- coding: utf-8 -*-
import os

if __name__ == '__main__':
    tpldir = './tpl'
    fh = open('tpl_collect.txt', 'w', encoding='utf-8')
    for fname in sorted(os.listdir(tpldir)):
        if fname.endswith('.txt'):
            fh.write('#{}\n'.format(fname))
            fi = open(os.path.join(tpldir, fname), 'r', encoding='utf-8')
            fh.write(fi.read())
            fi.close()
    fh.close()
