from os.path import exists,isfile,isdir,getsize,dirname,join
from os import makedirs
try:
    import qrcode
    import qrcode.image.svg
    import qrcode.image.pil
except ImportError:
    import sys
    sys.path.extend(('extra/six-1.4.1','extra/qrcode-4.0.4'))
    import qrcode
    import qrcode.image.svg
    import qrcode.image.pil
from logutil import LogUtil

class File2QRCode(object):
    D_CONST_MAXSIZE=2331
    D_CONST_PREFERSIZE=560
    def __init__(self):
        self._log=LogUtil().logger('core')
        self._qr=qrcode.QRCode()
        self._progfunc=None
        self.clearLastData()
    def clearLastData(self):
        self._lastwidth=0
        self._lasttotalpack=0
        self._lastprefix=''
        self._lastextname=''
        self._lastoutpath=''
    def regProgressFunc(self,func):
        self._log.info('callback(%s) register'%(func.__name__,))
        if callable(func):
            self._progfunc=func
        else:
            self._log.error('callback function error')
    def quickSplit(self,infile,splitsize=D_CONST_PREFERSIZE,outpath='',prefix='quick',method='png'):
        if self._fileCheck(infile):
            if outpath=='':
                outpath=dirname(infile)
            self.splitFile(infile,
                           splitsize,
                           outpath,
                           prefix,
                           method)
            return True
        return False
    def splitFile(self,infile,splitsize,outpath,outprefix,outmethod):
        self._log.info('InFile(%s) SplitSize(%d) OutPath(%s) Prefix(%s) Format(%s)'%(infile,splitsize,outpath,outprefix,outmethod))
        if self._fileCheck(infile):
            self.clearLastData()
            if outpath=='':
                self._log.debug('use current dir as output dir')
                outpath='.'
            if exists(outpath) and isdir(outpath):
                pass
            else:
                self._log.debug('make output dir')
                makedirs(outpath)
            self._lastoutpath=outpath
            self._lastprefix=outprefix
            if splitsize<=0 or splitsize>File2QRCode.D_CONST_MAXSIZE:
                splitsize=File2QRCode.D_CONST_MAXSIZE
                self._log.warning('SplitSize out of range, use %d'%(splitsize,))
            om=str(outmethod).upper()
            if om=='PNG':
                image_factory=qrcode.image.pil.PilImage
                self._lastextname='png'
            else:
                image_factory=qrcode.image.svg.SvgImage
                self._lastextname='svg'
            totalsize=getsize(infile)
            self._log.debug('InFile Size:%d'%(totalsize,))
            currentcnt=1
            self._lasttotalpack=(totalsize+splitsize-1)/splitsize
            self._log.debug('Package Count:%d'%(self._lasttotalpack,))
            self._lastwidth=len(str(self._lasttotalpack))
            with open(infile,'rb') as fh:
                while currentcnt<=self._lasttotalpack:
                    data=fh.read(splitsize)
                    self._qr.add_data(data)
                    img = self._qr.make_image(image_factory=image_factory)
                    outfile=self.getLastFilename(currentcnt)
                    img.save(outfile)
                    self._log.debug('%d/%d InSize:%d OutFile:%s QRVersion:%d'%(currentcnt,self._lasttotalpack,len(data),outfile,self._qr.version))
                    self._qr.clear()
                    self._qr.version=0
                    self._fireCallback(currentcnt,self._lasttotalpack)
                    currentcnt+=1
            return True
        return False
    def getLastFilename(self,idx):
        self._log.info('Index:%d Width:%d Prefix:%s'%(idx,self._lastwidth,self._lastprefix))
        filename=self._genOutfile(self._lastprefix,
                                  self._lastextname,
                                  idx,
                                  self._lastwidth)
        return join(self._lastoutpath,filename)
    def _genOutfile(self,prefix,extname,curcnt,width):
        outstr=prefix
        strfmt="%0"+str(width)+"d"
        outstr+=strfmt%(curcnt)
        outstr+='.'+extname
        return outstr
    def _fileCheck(self,infile):
        if exists(infile) and isfile(infile):
            return True
        return False
    def _fireCallback(self,cur,total):
        self._log.info('Current:%d Total:%d'%(cur,total))
        if self._progfunc:
            self._progfunc(cur,total)
