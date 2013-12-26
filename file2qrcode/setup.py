from distutils.core import setup
import py2exe
from glob import glob

data_files = ['logging.conf','f2q.png',("Microsoft.VC90.CRT", glob(r'C:\Program Files\Microsoft Visual Studio 9.0\VC\redist\x86\Microsoft.VC90.CRT\*.*'))]
option = {
    "compressed"    :    1    ,
    "optimize"      :    2    ,
    "bundle_files"  :    1
}

setup(
    # The first three parameters are not required, if at least a
    # 'version' is given, then a versioninfo resource is built from
    # them and added to the executables.
    version = "0.6.0",
    description = "convert a text file to QRCode images",
    name = "file2qrcode",

    options = {
        "py2exe"    :    option
    },
    zipfile=None,
    # targets to build
    windows = ["file2qrcode_ui.py"],
    data_files = data_files,
    )
