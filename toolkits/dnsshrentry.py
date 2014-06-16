from PyQt4 import QtGui,QtCore
import sys
import datetime
import dnsshrthread
import dnsshrconfig
import dnsshr_ui

class MainWidget(QtGui.QWidget):
    def setupUi(self):
        self._ui=dnsshr_ui.Ui_DNSSHR()
        self._ui.setupUi(self)
        self._scene=WorkScene()
        self._ui.graphics.setScene(self._scene)
        self._scene.drawPanel()
        self._dnsshr=dnsshrthread.DNSSHRThread()
        self.connect(self._dnsshr,QtCore.SIGNAL("threadStatus(const QString&)"),self.threadStatus)
        self.connect(self._dnsshr,QtCore.SIGNAL("finished()"),self.threadFinished)
    def threadStatus(self,status):
        self._ui.txtStatus.setText(status)
    def threadFinished(self):
        timelist=self._dnsshr.cardtime()
        if timelist:
            for item in timelist:
                self._scene.drawCardtime(item)
        timelist=self._dnsshr.overtime()
        if timelist:
            for item in timelist:
                for subitem in item:
                    self._scene.drawOverTime(subitem[0],subitem[1])
        timelist=self._dnsshr.leavetime()
        if timelist:
            for item in timelist:
                for subitem in item:
                    self._scene.drawLeaveTime(subitem[0],subitem[1])
        self.setEnabled(True)
    def onBtnRefresh(self):
        objyear=self._ui.inYear.value()
        objmonth=int(self._ui.inMonth.currentText())
        self._scene.clear()
        self._scene.drawPanel()
        self._scene.drawFreetime(objyear,objmonth)
        self._dnsshr.setAccount(self._ui.txtUsername.text(),self._ui.txtPassword.text())
        self._dnsshr.setDate(objyear,objmonth)
        self._dnsshr.start()
        self.setEnabled(False)

class WorkScene(QtGui.QGraphicsScene):
    D_TXT_WIDTH=40
    D_TXT_HEIGHT=20
    D_TIME_WIDTH=10
    D_TIME_COUNT=48
    D_TIME_DAYS=31
    D_COLOR_OVERTIME=QtGui.QColor(255,0,0,64)
    D_COLOR_LEAVETIME=QtGui.QColor(0,255,0,64)
    D_COLOR_FREETIME=QtGui.QColor(95,95,95,64)
    D_COLOR_CARDTIME=QtGui.QColor(0,0,255,255)
    def __init__(self,parent=None):
        super(WorkScene,self).__init__(parent)
        config=dnsshrconfig.DNSSHRConfig()
        self._workday=config.workday()
        self._holiday=config.holiday()
    def drawCardtime(self,cardtime,color=D_COLOR_CARDTIME):
        gap=self.D_TXT_HEIGHT/4
        circle_d=self.D_TXT_HEIGHT-gap*2
        timeinfo=self._timeToBlock(cardtime)
        day=timeinfo[0]
        block=timeinfo[1]
        startx=self.D_TXT_WIDTH+block*self.D_TIME_WIDTH
        starty=self.D_TXT_HEIGHT+(day-1)*self.D_TXT_HEIGHT
        self.addEllipse(startx-circle_d/2,starty+gap,circle_d,circle_d,color)
        self.addLine(startx-circle_d/2,starty+gap+circle_d/2,startx+circle_d/2,starty+gap+circle_d/2,color)
        self.addLine(startx,starty+gap,startx,starty+gap+circle_d,color)
    def drawOverTime(self,starttime,stoptime,color=D_COLOR_OVERTIME):
        timeinfo=self._timeToBlock(starttime,stoptime)
        self._drawBlock(timeinfo[0],timeinfo[1],timeinfo[2],color)
    def drawLeaveTime(self,starttime,stoptime,color=D_COLOR_LEAVETIME):
        timeinfo=self._timeToBlock(starttime,stoptime)
        self._drawBlock(timeinfo[0],timeinfo[1],timeinfo[2],color)
    def drawPanel(self):
        scenewidth=self.D_TXT_WIDTH+self.D_TIME_WIDTH*self.D_TIME_COUNT
        sceneheight=self.D_TXT_HEIGHT*(self.D_TIME_DAYS+2)
        self.setSceneRect(0,0,scenewidth,sceneheight)
        self.addRect(self.sceneRect())
        for i in range(self.D_TIME_DAYS):
            item=self.addText(str(i+1))
            item.setY((i+1)*self.D_TXT_HEIGHT)
            self.addLine(0,(i+1)*self.D_TXT_HEIGHT,scenewidth,(i+1)*self.D_TXT_HEIGHT)
        self.addLine(0,(self.D_TIME_DAYS+1)*self.D_TXT_HEIGHT,scenewidth,(self.D_TIME_DAYS+1)*self.D_TXT_HEIGHT)
        self.addLine(self.D_TXT_WIDTH,self.D_TXT_HEIGHT,self.D_TXT_WIDTH,sceneheight-self.D_TXT_HEIGHT)
        pen=QtGui.QPen(QtCore.Qt.DotLine)
        for i in range(self.D_TIME_COUNT):
            self.addLine(self.D_TXT_WIDTH+i*self.D_TIME_WIDTH,self.D_TXT_HEIGHT,self.D_TXT_WIDTH+i*self.D_TIME_WIDTH,sceneheight-self.D_TXT_HEIGHT,pen)
        for timeline in ((17,"8:30"),(27,"13:30"),(35,"17:30"),(37,""),(44,"22:00")):
            item=self.addLine(self.D_TXT_WIDTH+timeline[0]*self.D_TIME_WIDTH,self.D_TXT_HEIGHT,self.D_TXT_WIDTH+timeline[0]*self.D_TIME_WIDTH,sceneheight-self.D_TXT_HEIGHT)
            if timeline[1]:
                item=self.addText(timeline[1])
                itemrect=item.boundingRect()
                item.setPos(self.D_TXT_WIDTH+timeline[0]*self.D_TIME_WIDTH-itemrect.width()/2,0)
                item=self.addText(timeline[1])
                itemrect=item.boundingRect()
                item.setPos(self.D_TXT_WIDTH+timeline[0]*self.D_TIME_WIDTH-itemrect.width()/2,sceneheight-self.D_TXT_HEIGHT)
    def drawFreetime(self,year=-1,month=-1):
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
        weekend=[]
        while monthmin<=monthmax:
            if monthmin.isoweekday()>=6:
                weekend.append(monthmin.day)
            monthmin=monthmin+delta
        if monthmax.day<self.D_TIME_DAYS:
            weekend.append(self.D_TIME_DAYS)
        yearmonth="%4d%02d"%(objyear,objmonth)
        workday=self._workday.get(yearmonth,'')
        holiday=self._holiday.get(yearmonth,'')
        if workday:
            for subitem in workday.split(','):
                intsubitem=int(subitem)
                if intsubitem in weekend:
                    weekend.remove(intsubitem)
        if holiday:
            for subitem in holiday.split(','):
                intsubitem=int(subitem)
                if intsubitem not in weekend:
                    weekend.append(intsubitem)
        for day in weekend:
            self._drawBlock(day)
        self.addText("%d/%d"%(objyear,objmonth))
    def _drawBlock(self,day,startBlock=0,blocks=D_TIME_COUNT,color=D_COLOR_FREETIME):
        if startBlock<0 or startBlock>=self.D_TIME_COUNT:
            return
        remains=blocks
        curday=day
        curblock=startBlock
        brush=QtGui.QBrush(color,QtCore.Qt.SolidPattern)
        while remains>0 and curday<=self.D_TIME_DAYS:
            startx=self.D_TXT_WIDTH+curblock*self.D_TIME_WIDTH
            starty=self.D_TXT_HEIGHT+(curday-1)*self.D_TXT_HEIGHT
            if curblock+remains>self.D_TIME_COUNT:
                drawwidth=self.D_TIME_COUNT-curblock
                remains=curblock+remains-self.D_TIME_COUNT
                curblock=0
                curday+=1
            else:
                drawwidth=remains
                remains=0
            self.addRect(startx,starty,drawwidth*self.D_TIME_WIDTH,self.D_TXT_HEIGHT,brush=brush)
    def _timeToBlock(self,starttime,stoptime=None):
        day=starttime.day
        startblock=(starttime.hour+starttime.minute/60)*2
        if stoptime:
            delta=stoptime-starttime
            blocks=delta.seconds/1800+delta.days*self.D_TIME_COUNT
        else:
            blocks=0
        return (day,startblock,blocks)


if __name__ == '__main__':
    app=QtGui.QApplication(sys.argv)
    mw=MainWidget(None)
    mw.setupUi()
    mw.show()
    app.exec_()
