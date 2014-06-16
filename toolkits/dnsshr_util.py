import re
import pickle
import datetime
import requests

# http://10.73.216.20/dnsshr/zz/SelfHelpLeft.aspx
# 	Href='SelfInfoManager.aspx'				个人信息维护
# 	Href='../ChangePassword.aspx'			修改密码
# 	Href='SalaryInfo.aspx'					工资信息
# 	Href='../NoLogin/RuleView.aspx'			规章制度
# 	Href='../NoLogin/NoticeView.aspx'		通知
# 	Href='../NoLogin/NewsView.aspx'			新闻
# 	Href='../DC/pxdctfLst.aspx'				问卷调查
# 	Href='../KQ/kq_cardzz.aspx'				刷卡记录
# 	Href='../KQ/kq_self_leave.aspx'			请假
# 	Href='../KQ/KQ_selfControlLeave.aspx'	可用休假
# 	Href='../KQ/kq_self_over.aspx'			加班
# 	Href='../KQ/kq_self_out.aspx'			外出/出差
# 	Href='../ZZ/KQ_DayNormalRight.aspx'		查看考勤记录
# 	Href='../zz/ccbx.aspx'					出差报销
# 	Href='../LsWebPublic/ShortMessage.aspx'	查阅短信

class DNSSHR(object):
    def __init__(self):
        self.session=None
        self.rooturl='http://10.73.216.20/DNSSHR/'
        #self.login(username,passwd)

    def login(self,username,passwd):
        # url=self.rooturl+'login.aspx'
        # use redirect to check whether login success
        url=self.rooturl+'login.aspx?ReturnUrl=%2fdnsshr%2fzz%2fSelfHelpLeft.aspx'
        self.session=requests.Session()
        r=self.session.get(url)
        postdata=self._findHiddenData(r)
        postdata['edtUserName']=username
        postdata['edtPassWord']=passwd
        postdata['ddl1']="3",
        postdata['ImageButton1.x']="30"
        postdata['ImageButton1.y']="8"
        r=self.session.post(url,postdata)
        return r.url!=url

    def record(self,year=-1,month=-1):
        url=self.rooturl+'KQ/kq_cardzz.aspx'
        dateinfo=self._monthDate(year,month)
        r=self.session.get(url)
        postdata=self._findHiddenData(r)
        postdata['txtDateBegin']=dateinfo[2]
        postdata['txtDateEnd']=dateinfo[3]
        postdata['bnDisPlay.x']="18"
        postdata['bnDisPlay.y']="10"
        postdata['DataGrid1.tcChangePage:txtRecord']="100"
        r=self.session.post(url,postdata)
        timerecord=self._parseRecord(r)
        self._dumpData(timerecord,'cardrecord.bin')
        return timerecord

    def overtime(self,year=-1,month=-1):
        url=self.rooturl+'KQ/kq_self_over.aspx'
        dateinfo=self._monthDate(year,month)
        r=self.session.get(url)
        postdata=self._findHiddenData(r)
        postdata['btnLoadData.x']="29"
        postdata['btnLoadData.y']="13"
        postdata['1']="rb1"
        postdata['txtYear']=dateinfo[0]
        postdata['txtMonth']=dateinfo[1]
        postdata['txtDate1']="2014-06-01"
        postdata['txtDate2']="2014-06-30"
        postdata['hid']=""
        overtime=[]
        #postdata['ucCtlSignedType:DropDownList1']="0    " # draft
        #r=self.session.post(url,postdata)
        #overtime.append(self._parseOvertime(r))
        postdata['ucCtlSignedType:DropDownList1']="1    " # accepted
        r=self.session.post(url,postdata)
        overtime.append(self._parseOvertime(r))
        postdata['ucCtlSignedType:DropDownList1']="2    " # waiting
        r=self.session.post(url,postdata)
        overtime.append(self._parseOvertime(r))
        #postdata['ucCtlSignedType:DropDownList1']="3    " # declined
        #r=self.session.post(url,postdata)
        #overtime.append(self._parseOvertime(r))
        self._dumpData(overtime,'overtime.bin')
        return overtime

    def leavetime(self,year=-1,month=-1):
        url=self.rooturl+'KQ/kq_self_leave.aspx'
        dateinfo=self._monthDate(year,month)
        r=self.session.get(url)
        postdata=self._findHiddenData(r)
        postdata['btnLoadData.x']="0"
        postdata['btnLoadData.y']="0"
        postdata['1']="rb1"
        postdata['txtYear']=dateinfo[0]
        postdata['txtMonth']=dateinfo[1]
        postdata['txtDate1']="2014-06-01"
        postdata['txtDate2']="2014-06-30"
        postdata['hid']=""
        leavetime=[]
        #postdata['ucCtlSignedType:DropDownList1']="0    " # draft
        #r=self.session.post(url,postdata)
        #leavetime.append(self._parseLeavetime(r))
        postdata['ucCtlSignedType:DropDownList1']="1    " # accepted
        r=self.session.post(url,postdata)
        leavetime.append(self._parseLeavetime(r))
        postdata['ucCtlSignedType:DropDownList1']="2    " # waiting
        r=self.session.post(url,postdata)
        leavetime.append(self._parseLeavetime(r))
        #postdata['ucCtlSignedType:DropDownList1']="3    " # declined
        #r=self.session.post(url,postdata)
        #leavetime.append(self._parseLeavetime(r))
        self._dumpData(leavetime,'leavetime.bin')
        return leavetime

    def available_leavetime(self):
        url=self.rooturl+'KQ/kq_selfControlLeave.aspx'
        r=self.session.get(url)
        available=self._parseAvailableLeavetime(r)
        self._dumpData(available,'available_leavetime.bin')
        print(available)

    def _parseRecord(self,r):
        pattern=re.compile(r'<td width="120">(?P<time>.+?)</td>')
        outlist=[]
        for line in r.text.splitlines():
            ret=pattern.search(line)
            if ret:
                dtime=datetime.datetime.strptime(ret.group('time'),'%Y-%m-%d %H:%M')
                outlist.append(dtime)
        return tuple(outlist)
    def _parseOvertime(self,r):
        pattern=re.compile(r'<td width="120">(?P<starttime>.+?)</td><td width="120">(?P<stoptime>.+?)</td>')
        outlist=[]
        for line in r.text.splitlines():
            ret=pattern.search(line)
            if ret:
                dtime1=datetime.datetime.strptime(ret.group('starttime'),'%Y-%m-%d %H:%M')
                dtime2=datetime.datetime.strptime(ret.group('stoptime'),'%Y-%m-%d %H:%M')
                outlist.append((dtime1,dtime2))
        return tuple(outlist)
    def _parseLeavetime(self,r):
        pattern=re.compile(r'<td width="100">(?P<name>.+?)</td><td width="100">(?P<starttime>.+?)</td><td width="100">(?P<stoptime>.+?)</td><td width="100">(?P<hours>.+?)</td><td width="100">(?P<type>.+?)</td><td width="100">(?P<status1>.+?)</td><td width="200">(?P<reason>.*?)</td><td width="100">(?P<days>.+?)</td><td width="100">(?P<applyname>.+?)</td><td width="100">(?P<applytime>.+?)</td><td width="100">(?P<status2>.+?)</td><td width="120">(?P<memo>.*?)</td>')
        outlist=[]
        for line in r.text.splitlines():
            ret=pattern.search(line)
            if ret:
                dtime1=datetime.datetime.strptime(ret.group('starttime'),'%Y-%m-%d %H:%M')
                dtime2=datetime.datetime.strptime(ret.group('stoptime'),'%Y-%m-%d %H:%M')
                outlist.append((dtime1,dtime2))
        return tuple(outlist)
    def _parseAvailableLeavetime(self,r):
        pattern=re.compile(r'<td align="center">(?P<type>.+?)</td><td align="center">(?P<total>.+?)</td><td align="center">(?P<used>.+?)</td><td align="center">(?P<remain>.+?)</td>')
        outlist=[]
        for line in r.text.splitlines():
            ret=pattern.search(line)
            if ret:
                outlist.append((ret.group('type'),ret.group('total'),ret.group('used'),ret.group('remain')))
        return tuple(outlist[1:])

    def _findHiddenData(self,r):
        hidden=re.compile(r'type="hidden".+?name="(?P<name>.+?)".+?value="(?P<value>.+?)"')
        outdict={}
        for line in r.text.splitlines():
            ret=hidden.search(line)
            if ret:
                outdict[ret.group('name')]=ret.group('value')
        return outdict
    def _monthDate(self,year=-1,month=-1):
        if year<=0 or month<=0:
            today=datetime.date.today()
        if year<=0:
            objyear=today.year
        else:
            objyear=year
        if month<=0:
            objmonth=today.month
        else:
            objmonth=month
        delta=datetime.timedelta(days=1)
        monthmin=datetime.date(objyear,objmonth,1)
        if objmonth>=12:
            monthmax=datetime.date(objyear+1,1,1)-delta
        else:
            monthmax=datetime.date(objyear,objmonth+1,1)-delta
        minstr="%d/%d/%d"%(monthmin.year,monthmin.month,monthmin.day)
        maxstr="%d/%d/%d"%(monthmax.year,monthmax.month,monthmax.day)
        return (str(objyear),str(objmonth),minstr,maxstr)
    def _writeHtml(self,r,outfile,encode='utf-8'):
        with open(outfile,'w',encoding=encode) as fd:
            fd.write(r.text)
        return
    def _dumpData(self,data,outfile):
        #with open(outfile,'wb') as fd:
            #pickle.dump(data,fd)
        return
    def _loadData(self,infile):
        data=None
        with open(infile,'rb') as fd:
            data=pickle.load(fd)
        return data

