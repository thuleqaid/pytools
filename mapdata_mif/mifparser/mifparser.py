import sys
import os.path
import re
import logging
import ply.lex as lex
import ply.yacc as yacc

#logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(level=logging.CRITICAL)
'''
Usage:
  mif=MIFParser()
  mif.parse(mif-filepath,file-encode)
  data_array=mif.getTokens()
MIF Format:
POINT x y
  [ SYMBOL (shape, color, size)]
LINE x1 y1 x2 y2 [ PEN (width, pattern, color)]
PLINE [ MULTIPLE numsections ]
  numpts1
    x1 y1
    x2 y2
    :
  [ numpts2
    x1 y1
    x2 y2 ]
  :
  [ PEN (width, pattern, color)]
  [ SMOOTH ]
REGION numpolygons
  numpts1
  x1 y1
  x2 y2
  :
  [ numpts2
  x1 y1
  x2 y2 ]
  :
  [ PEN (width, pattern, color)]
  [ BRUSH (pattern, forecolor, backcolor)]
  [ CENTER x y ]
PEN (width, pattern, color)
Brush (pattern, forecolor [, backcolor ])
SYMBOL (shape, color, size)
'''

class MIFObject(object):
    '''
type:NONE,POINT,PLINE,REGION
point:int
pline:int
region:int
points:[[],...]    # used by point, pline, region
symbol:[]          # used by point
brush:[]           # used by region
pen:[]             # used by pline, region
center:[]          # used by region
smooth:True,False  # used by pline
data:{k=>v,...}    # MID
    '''
    def __init__(self):
        self._type=''
        self._point=0
        self._pline=0
        self._region=0
        self._points=(())
        self._symbol=()
        self._brush=()
        self._pen=()
        self._center=()
        self._smooth=False
        self._data={}
    def __str__(self):
        outtext="Type(%s)"%(self._type)
        if self._point>0:
            outtext+="Point(%d)"%(self._point)
        if self._pline>0:
            outtext+="Pline(%d)"%(self._pline)
        if self._region>0:
            outtext+="Region(%d)"%(self._region)
        if self._points:
            outtext+="Points(%s)"%(str(self._points))
        if self._symbol:
            outtext+="Symbol(%s)"%(str(self._symbol))
        if self._brush:
            outtext+="Brush(%s)"%(str(self._brush))
        if self._pen:
            outtext+="Pen(%s)"%(str(self._pen))
        if self._center:
            outtext+="Center(%s)"%(str(self._center))
        if self._smooth:
            outtext+="Smooth"
        outtext+="Data(%s)"%(str(self._data))
        return outtext
    @property
    def type(self):
        return self._type
    @type.setter
    def type(self,typestr):
        self._type=typestr.upper()
    @property
    def point(self):
        return self._point
    #@point.setter
    #def point(self,pointnum):
    #    self._point=int(pointnum)
    @property
    def pline(self):
        return self._pline
    @pline.setter
    def pline(self,plinenum):
        self._pline=int(plinenum)
    @property
    def region(self):
        return self._region
    @region.setter
    def region(self,regionnum):
        self._region=int(regionnum)
    @property
    def points(self):
        return self._points
    @points.setter
    def points(self,pointarr):
        cnt=0
        inarray=list(pointarr)
        outarray=[]
        while len(inarray)>0:
            len1=int(inarray.pop(0))
            cnt+=len1
            line=[]
            for i in range(len1):
                line.append((inarray.pop(0),inarray.pop(0)))
            outarray.append(tuple(line))
        self._points=tuple(outarray)
        self._point=cnt
    @property
    def symbol(self):
        return self._symbol
    @symbol.setter
    def symbol(self,symbolarr):
        self._symbol=tuple(symbolarr)
    @property
    def brush(self):
        return self._brush
    @brush.setter
    def brush(self,brusharr):
        self._brush=tuple(brusharr)
    @property
    def pen(self):
        return self._pen
    @pen.setter
    def pen(self,penarr):
        self._pen=tuple(penarr)
    @property
    def center(self):
        return self._center
    @center.setter
    def center(self,centerarr):
        self._center=tuple(centerarr)
    @property
    def smooth(self):
        return self._smooth
    @smooth.setter
    def smooth(self,smoothflag):
        self._smooth=smoothflag
    def getMid(self,keystr,defaultvalue=''):
        return self._data.get(keystr,defaultvalue)
    def setMid(self,keystr,valuestr):
        self._data[keystr]=valuestr

class MIFParser(object):
    tokens = (
        'NONE','POINT','PLINE','REGION','LINE',
        'PEN','BRUSH','SYMBOL','CENTER','SMOOTH','MULTIPLE',
        'NUMBER','LPAREN','RPAREN',
        )
    def __init__(self):
        lex.lex(module=self)
        yacc.yacc(module=self)
        self.mid=MIDParser()
        self.mifobj=[]
    def init(self):
        self.lineno=0
    def initstate(self):
        self.point=''
        self.pline=''
        self.smooth=False
        self.region=''
        self.numbers=[]
        self.symbol=[]
        self.brush=[]
        self.pen=[]
        self.center=[]
    def getTokens(self):
        return tuple(self.mifobj)
    def logstate(self):
        if self.point!='':
            logging.debug('POINT:'+self.point)
        if self.pline!='':
            logging.debug('PLINE:'+self.pline)
        if self.region!='':
            logging.debug('REGION:'+self.region)
        if len(self.numbers)>0:
            logging.debug('NUMBERS:'+",".join(self.numbers))
        if len(self.symbol)>0:
            logging.debug('SYMBOL:'+",".join(self.symbol))
        if len(self.brush)>0:
            logging.debug('BRUSH:'+",".join(self.brush))
        if len(self.pen)>0:
            logging.debug('PEN:'+",".join(self.pen))
        if len(self.center)>0:
            logging.debug('CENTER:'+",".join(self.center))
        if self.smooth:
            logging.debug('SMOOTH:'+str(self.smooth))
    def parse(self,fname,encode):
        self.mifobj=[]
        pat=re.compile(r'(?i)\bdata\b')
        pat2=re.compile(r'(?i)Columns\s+(?P<cols>\d+)')
        pat3=re.compile(r'^\s*(?P<colname>\S+)')
        pat4=re.compile(r'(?i)Delimiter\s+"(?P<sep>.+?)"')
        # load mif file
        fh=open(fname,'rU')
        lines=[]
        for line in fh.readlines():
            lines.append(line.decode(encode).encode('utf8'))
        fh.close()
        # parse col-definition part
        cols=0
        colnames=[]
        while(not pat.search(lines[0])):
            line=lines.pop(0)
            if cols<1:
                ret2=pat2.search(line)
                if ret2:
                    cols=int(ret2.group('cols'))
                else:
                    ret4=pat4.search(line)
                    if ret4:
                        sep=ret4.group('sep')
            else:
                ret3=pat3.search(line)
                colnames.append(ret3.group('colname'))
                cols-=1
        lines.pop(0)
        # load mid file
        self.mid.setup(sep,colnames)
        self.mid.parse(os.path.splitext(fname)[0]+'.MID',encode)
        # parse data part
        self.init()
        self._parse("\n".join(lines))

    def _parse(self,statements):
        self.initstate()
        yacc.parse(statements)

    t_NONE    =r'(?i)none'
    t_POINT   =r'(?i)point'
    t_PLINE   =r'(?i)pline'
    t_REGION  =r'(?i)region'
    t_LINE    =r'(?i)line'
    t_PEN     =r'(?i)pen'
    t_BRUSH   =r'(?i)brush'
    t_SYMBOL  =r'(?i)symbol'
    t_CENTER  =r'(?i)center'
    t_SMOOTH  =r'(?i)smooth'
    t_MULTIPLE=r'(?i)multiple'
    t_NUMBER  =r'\d+\.?\d*'
    t_LPAREN  =r'\('
    t_RPAREN  =r'\)'
    t_ignore  =' \t\x0c\n,'
    def t_error(self,t):
        logging.critical("T_ERROR: %s" % repr(t.value[0]))
        t.lexer.skip(1)
    def p_miffile(self,p):
        '''miffile : item
                   | miffile item'''
        self.lineno+=1
        logging.debug("Item %d"%(self.lineno))
        self.logstate()
        self.initstate()
    def p_item(self,p):
        '''item : NONE
                | point
                | pline
                | line
                | region'''
        mif=MIFObject()
        if p[1]=='PPOINT':
            mif.type='POINT'
            #mif.point=int(self.point)
            mif.points=tuple(self.numbers)
        elif p[1]=='PPLINE':
            mif.type='PLINE'
            mif.pline=int(self.pline)
            mif.pen=tuple(self.pen)
            mif.smooth=self.smooth
            mif.points=tuple(self.numbers)
        elif p[1]=='PLINE':
            mif.type='LINE'
            mif.pline=int(self.pline)
            mif.pen=tuple(self.pen)
            mif.points=tuple(self.numbers)
        elif p[1]=='PREGION':
            mif.type='REGION'
            mif.region=int(self.region)
            mif.pen=tuple(self.pen)
            mif.brush=tuple(self.brush)
            mif.center=tuple(self.center)
            mif.points=tuple(self.numbers)
        else:
            mif.type='NONE'
        for col in range(len(self.mid._cols)):
            mif.setMid(self.mid._cols[col],self.mid._data[self.lineno][col])
        logging.info(mif)
        self.mifobj.append(mif)
    def p_point(self,p):
        '''point : POINT NUMBER NUMBER
                 | POINT NUMBER NUMBER symbol'''
        p[0]='PPOINT'
        self.numbers=['1',p[2],p[3]]
        self.point='1'
    def p_line(self,p):
        '''line : LINE NUMBER NUMBER NUMBER NUMBER
                | LINE NUMBER NUMBER NUMBER NUMBER pen'''
        p[0]='PLINE'
        self.numbers=['2',p[2],p[3],p[4],p[5]]
        self.pline='1'
    def p_pline(self,p):
        '''pline : PLINE numbers
                 | PLINE MULTIPLE NUMBER numbers
                 | pline pen
                 | pline SMOOTH'''
        p[0]='PPLINE'
        if p[2]=='PNUMBERS':
            self.pline='1'
        elif p[2]=='PPEN':
            pass
        else:
            if len(p)>3:
                self.pline=p[3]
                logging.warning('PLINE MULTIPLE')
            else:
                self.smooth=True
    def p_region(self,p):
        '''region : REGION NUMBER numbers
                  | region pen
                  | region brush
                  | region center'''
        p[0]='PREGION'
        if p[2]=='PPEN':
            pass
        elif p[2]=='PBRUSH':
            pass
        elif p[2]=='PCENTER':
            pass
        else:
            self.region=p[2]
            if int(self.region)>1:
                logging.warning('REGION MULTIPLE')
    def p_numbers(self,p):
        '''numbers : NUMBER
                   | numbers NUMBER'''
        p[0]='PNUMBERS'
        if len(p)>2:
            self.numbers.append(p[2])
        else:
            self.numbers.append(p[1])
    def p_symbol(self,p):
        '''symbol : SYMBOL LPAREN NUMBER NUMBER NUMBER RPAREN'''
        p[0]='PSYMBOL'
        self.symbol=[p[3],p[4],p[5]]
    def p_brush(self,p):
        '''brush : BRUSH LPAREN NUMBER NUMBER RPAREN
                 | BRUSH LPAREN NUMBER NUMBER NUMBER RPAREN'''
        p[0]='PBRUSH'
        if len(p)>6:
            self.brush=[p[3],p[4],p[5]]
        else:
            self.brush=[p[3],p[4]]
    def p_pen(self,p):
        '''pen : PEN LPAREN NUMBER NUMBER NUMBER RPAREN'''
        p[0]='PPEN'
        self.pen=[p[3],p[4],p[5]]
    def p_center(self,p):
        '''center : CENTER NUMBER NUMBER'''
        p[0]='PCENTER'
        self.center=[p[2],p[3]]
    def p_error(self,p):
        logging.critical("P_ERROR: "+str(p))

class MIDParser(object):
    def setup(self,sep,colnames):
        self._sep=sep
        self._cols=tuple(colnames)
        self._data=[]
    def parse(self,fname,encode):
        fh=open(fname,'rU')
        lines=[]
        for line in fh.readlines():
            lines.append(line.decode(encode).encode('utf8'))
        fh.close()
        sep='"'+self._sep+'"'
        for line in lines:
            line2=line.strip()
            parts=line2.split(sep)
            self._data.append([])
            for part in parts:
                if part.startswith('"'):
                    self._data[-1].append(part[1:])
                elif part.endswith('"'):
                    self._data[-1].append(part[:-1])
                else:
                    self._data[-1].append(part)
        logging.debug(self._data)

