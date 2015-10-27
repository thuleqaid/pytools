# -*- coding:utf-8 -*-
# VERSION: 0.1
import collections
import threading
import queue
from .logutil import LogUtil

LOGNAME = 'MultiThread'

class MultiThread(object):
    QueueItem = collections.namedtuple('QueueItem', ['group','param'])
    def __init__(self,worker=2,daemon=False):
        self._queue = queue.Queue()
        self._worker = worker
        self._daemon = daemon
        self._finish = True
        self._lock = threading.Lock()
        self._cbfuncs = {}
        self._log = LogUtil().logger(LOGNAME)
    def register(self, target, group='DEFAULT'):
        if self._finishCheck:
            self._cbfuncs[group] = target
            self._log.log(10, 'Add Function for [{}]'.format(group))
        else:
            self._log.log(30, 'Can only register a function before start')
    def addJob(self,param,group='DEFAULT'):
        self._queue.put(self.QueueItem(group, param))
        self._log.log(10, 'Add Job for [{}] with data[{}]'.format(group, param))
    def start(self):
        self._finish = False
        self._log.log(20, 'Start multithread[{}]'.format(self._worker))
        # 启动子线程
        for i in range(self._worker):
             t = threading.Thread(target=self._dispatch)
             t.daemon = self._daemon
             t.start()
    def join(self):
        self._log.log(20, 'Wait multithread')
        # 等待队列处理完成
        self._queue.join()
        self._log.log(20, 'Wait finished')
        self.stop()
    def stop(self):
        self._lock.acquire()
        self._finish = True
        self._lock.release()
        self._log.log(20, 'Stop multithread')
    def _dispatch(self):
        while True:
            try:
                item = self._queue.get(True, 1)
                # 调用注册的函数
                if item.group in self._cbfuncs:
                    self._log.log(10, 'Run function for [{}] with data[{}]'.format(item.group, item.param))
                    self._cbfuncs[item.group](item.param)
                else:
                    self._log.log(10, 'No function for [{}]'.format(item.group))
                self._queue.task_done()
                if self._finishCheck():
                    break
            except queue.Empty as e:
                # 1秒内未取到队列数据，则判断队列是否已经处理完成
                if self._finishCheck():
                    break
    def _finishCheck(self):
        self._lock.acquire()
        flag = self._finish
        self._lock.release()
        return flag

if __name__ == '__main__':
    def test(data):
        print("Test:{}".format(data))
    def test1(data):
        print("Test1:{}".format(data))
    def test2(data):
        print("Test2:{}".format(data))
    #logutil.newConf((LOGNAME,))
    mt = MultiThread(3)
    mt.register(test)
    mt.register(test1, 'Test1')
    mt.register(test2, 'Test2')
    mt.start()
    for i in range(10):
        mt.addJob(i)
        mt.addJob(i*2, 'Test1')
        mt.addJob(i*i, 'Test2')
    mt.join()
