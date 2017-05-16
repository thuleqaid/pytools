@echo off
python -m PyQt5.uic.pyuic toolbox.ui -o toolbox_ui.py
python -m PyQt5.uic.pyuic filefilter.ui -o filefilter_ui.py
@echo on