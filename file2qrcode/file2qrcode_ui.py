import wx
import os.path
import file2qrcode_core as f2q
from logutil import LogUtil

class F2QToolPanel(wx.Panel):
    def __init__(self,parent,id=wx.ID_ANY,pos=wx.DefaultPosition,size=wx.DefaultSize,style=wx.TAB_TRAVERSAL,name=wx.PanelNameStr):
        super(F2QToolPanel,self).__init__(parent,id,pos,size,style,name)
        self._log=LogUtil().logger('ui')
        self._tool=f2q.File2QRCode()
        self._tool.regProgressFunc(self.OnProgress)
        self.SetupUi()
    def SetupUi(self):
        sizer=wx.GridBagSizer()
        label1=wx.StaticText(self,label='Input File')
        self._txt1=wx.TextCtrl(self,value='')
        btn1=wx.Button(self,label='...')
        label2=wx.StaticText(self,label='Output Path')
        self._txt2=wx.TextCtrl(self,value='')
        btn2=wx.Button(self,label='...')
        label31=wx.StaticText(self,label='Split Size')
        label32=wx.StaticText(self,label='Format')
        self._combo31=wx.ComboBox(self,choices=('14','26','42','62',
                                          '84','106','122','152',
                                          '180','213','251','287',
                                          '331','362','412','450',
                                          '504','560','624','666',
                                          '711','779','857','911',
                                          '997','1059','1125','1190',
                                          '1264','1370','1452','1538',
                                          '1628','1722','1809','1911',
                                          '1989','2099','2213','2331')
                                          ,value='560',style=wx.CB_READONLY)
        self._combo32=wx.ComboBox(self,choices=('png','svg'),value='png',style=wx.CB_READONLY)
        label4=wx.StaticText(self,label='Prefix')
        self._txt4=wx.TextCtrl(self,value='quick')
        btn4=wx.Button(self,label='Split')
        sizer.Add(label1,(0,0),flag=wx.EXPAND)
        sizer.Add(self._txt1,(0,1),(1,3),flag=wx.EXPAND)
        sizer.Add(btn1,(0,4),flag=wx.EXPAND)
        sizer.Add(label2,(1,0),flag=wx.EXPAND)
        sizer.Add(self._txt2,(1,1),(1,3),flag=wx.EXPAND)
        sizer.Add(btn2,(1,4),flag=wx.EXPAND)
        sizer.Add(label31,(2,0),flag=wx.EXPAND)
        sizer.Add(self._combo31,(2,1),flag=wx.EXPAND)
        sizer.Add(label32,(2,3),flag=wx.EXPAND)
        sizer.Add(self._combo32,(2,4),flag=wx.EXPAND)
        sizer.Add(label4,(3,0),flag=wx.EXPAND)
        sizer.Add(self._txt4,(3,1),(1,3),flag=wx.EXPAND)
        sizer.Add(btn4,(3,4),flag=wx.EXPAND)
        sizer.SetFlexibleDirection(wx.HORIZONTAL)
        sizer.AddGrowableCol(2)
        self.SetSizer(sizer)
        self.Bind(wx.EVT_BUTTON,self.OnInBtn,btn1)
        self.Bind(wx.EVT_BUTTON,self.OnOutBtn,btn2)
        self.Bind(wx.EVT_BUTTON,self.OnActBtn,btn4)
    def OnProgress(self,curcnt,totalcnt):
        self._log.info('Callback(%d/%d)'%(curcnt,totalcnt))
        self.GetParent().SetStatusText("%d/%d"%(curcnt,totalcnt),2)
        if curcnt>=totalcnt:
            msgbox=wx.MessageDialog(self,message='Split Done!',style=wx.OK|wx.CENTER)
            msgbox.ShowModal()
    def OnInBtn(self,event):
        self._log.info('ButtonPressed')
        infile=self._txt1.GetValue()
        if infile:
            pathname,filename=os.path.split(infile)
            fd=wx.FileDialog(self,message='Select file to split...',defaultDir=pathname,defaultFile=filename)
        else:
            fd=wx.FileDialog(self,message='Select file to split...')
        if fd.ShowModal()==wx.ID_OK:
            fullname=fd.GetPath()
            self._log.debug('FileDialog:%s'%(fullname,))
            pathname,filename=os.path.split(fullname)
            filesize=os.path.getsize(fullname)
            self._txt1.SetValue(fullname)
            self._txt2.SetValue(pathname)
            self.GetParent().SetStatusText(filename,0)
            self.GetParent().SetStatusText("%d Bytes"%(filesize,),1)
            self.GetParent().SetStatusText("",2)
    def OnOutBtn(self,event):
        self._log.info('ButtonPressed')
        outpath=self._txt2.GetValue() or '.'
        fd=wx.DirDialog(self,message='Select output path...',defaultPath=outpath)
        if fd.ShowModal()==wx.ID_OK:
            pathname=fd.GetPath()
            self._log.debug('DirDialog:%s'%(pathname,))
            self._txt2.SetValue(pathname)
    def OnActBtn(self,event):
        self._log.info('ButtonPressed')
        infile=self._txt1.GetValue()
        outpath=self._txt2.GetValue()
        prefix=self._txt4.GetValue()
        splitsize=int(self._combo31.GetValue())
        method=self._combo32.GetValue()
        self._log.debug('InFile:%s SplitSize:%d OutPath:%s Prefix:%s Format:%s'%(infile,splitsize,outpath,prefix,method))
        self._tool.quickSplit(infile,splitsize,outpath,prefix,method)

class F2QToolApp(wx.App):
    def OnInit(self):
        self.frame=F2QToolFrame(None,title='File2QRCode')
        self.SetTopWindow(self.frame)
        self.frame.Show()
        return True

class F2QToolFrame(wx.Frame):
    def __init__(self,parent,id=wx.ID_ANY,title='',pos=wx.DefaultPosition,size=wx.DefaultSize,style=wx.DEFAULT_FRAME_STYLE):
        super(F2QToolFrame,self).__init__(parent,id,title,pos,size,style)
        self.SetIcon(wx.Icon('f2q.png'))
        self.CreateStatusBar(3)
        self.SetStatusWidths([-4,-2,-1])
        sizer=wx.BoxSizer(wx.VERTICAL)
        panel=F2QToolPanel(self)
        sizer.Add(panel,1,flag=wx.EXPAND|wx.ALL)
        self.SetSizerAndFit(sizer)
        size=self.GetSize()
        self.SetSizeHints(size[0],size[1],-1,size[1])

if __name__=='__main__':
    app=F2QToolApp(False)
    app.MainLoop()
