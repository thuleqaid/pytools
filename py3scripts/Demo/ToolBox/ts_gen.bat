@echo off
set lupdate="d:\Anaconda3\Library\bin\pylupdate5.exe"
%lupdate% filefilter_ui.py toolbox_ui.py -ts toolbox_zh_CN.ts
@echo on