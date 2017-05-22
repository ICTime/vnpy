# encoding: UTF-8

import os
import sys
import ctypes
from datetime import datetime, timedelta, date
from time import sleep

from vnpy.event.eventEngine import *
from vtEngine import MainEngine
from ctaStrategy.strategy import STRATEGY_CLASS
from threading import Thread

from noUiBasicWidget import *

"""
启动：python noUiMain.py >>logs/mylog.log &
停止：ps -ef | grep python ; kill -9 PID
查看：tail -f logs/filename 
"""

##############################################################
class NoUiMain(object):

    #----------------------------------------------------------------------
    def __init__(self):
        # gateway 是否连接
        self.connected = False
        # gateway 的连接名称，在vtEngine.initGateway()里面定义，对应的配置文件是 "连接名称_connect.json"，
        self.gateway_name = 'CTP'
        # 启动的策略实例，须在catAlgo/CtaSetting.json 里面定义  [u'S28_RB1001', u'S28_TFT', u'S28_HCRB',u'atr_rsi']
        # self.strategies = [u'S28_HCRB']
        self.strategies = []

        self.g_count = 0

        self.last_dt = datetime.now()

        # 实例化 主引擎
        print u'instance mainengine'
        self.mainEngine = MainEngine()

    #----------------------------------------------------------------------
    def trade_off(self):
        """检查现在是否为非交易时间"""
        now = datetime.now()
        a = datetime.now().replace(hour=2, minute=35, second=0, microsecond=0)
        b = datetime.now().replace(hour=8, minute=30, second=0, microsecond=0)
        c = datetime.now().replace(hour=15, minute=30, second=0, microsecond=0)
        d = datetime.now().replace(hour=20, minute=30, second=0, microsecond=0)
        weekend = (now.isoweekday() == 6 and now >= a) or (now.isoweekday() == 7)
        off = (a <= now <= b) or (c <= now <= d) or weekend
        return off

    #----------------------------------------------------------------------
    def disconnect(self):
        """"断开底层gateway的连接"""
        if self.mainEngine:
            self.mainEngine.disconnect(self.gateway_name)
            self.connected = False

    #----------------------------------------------------------------------
    def onTimer(self, event):
        """定时器执行逻辑，每十秒执行一次"""

        # 十秒才执行一次检查
        self.g_count += 1
        if self.g_count <= 20:
            return

        self.g_count = 0
        dt = datetime.now()
        if dt.hour != self.last_dt.hour:
            self.last_dt = dt
            self.mainEngine.writeLog( u'noUiMain.py checkpoint:{0}'.format(dt))

        # 定时断开
        if self.trade_off():
            """非交易时间"""
            if self.connected:
                self.mainEngine.writeLog(u'断开连接{0}'.format(self.gateway_name))
                self.disconnect()
                self.mainEngine.writeLog(u'清空数据引擎')
                self.mainEngine.clearData()
                self.connected = False
            return

        # 交易时间内，定时重连和检查
        if not self.connected:
            self.mainEngine.writeLog(u'启动连接{0}'.format(self.gateway_name))
            self.mainEngine.writeLog(u'清空数据引擎')
            # self.mainEngine.clearData()
            self.mainEngine.writeLog(u'重新连接{0}'.format(self.gateway_name))
            self.mainEngine.connect(self.gateway_name)
            self.connected = True
            return
        else:
            if not self.mainEngine.checkGatewayStatus(self.gateway_name):
                self.mainEngine.writeLog(u'检查连接{0}异常，重新启动连接'.format(self.gateway_name))
                self.mainEngine.writeLog(u'断开连接{0}'.format(self.gateway_name))
                self.disconnect()
                # self.mainEngine.writeLog(u'清空数据引擎')
                self.mainEngine.clearData()
                self.mainEngine.writeLog(u'重新连接{0}'.format(self.gateway_name))
                self.mainEngine.connect(self.gateway_name)
                self.connected = True

    #----------------------------------------------------------------------
    def Start(self):
        """启动"""

        # 若需要连接数据库，则启动
        #self.mainEngine.dbConnect()

        # 加载cta的配置
        print u'load cta setting'
        self.mainEngine.ctaEngine.loadSetting()

        print u'initialize all strategies'
        # 初始化策略，如果多个，则需要逐一初始化多个
        for s in self.strategies:
            print 'init trategy {0}'.format(s)
            self.mainEngine.ctaEngine.initStrategy(s)
            # 逐一启动策略
            print 'start strategy {0}'.format(s)
            self.mainEngine.ctaEngine.startStrategy(s)

        # 指定的连接配置
        print u'connect gateway:{0}'.format(self.gateway_name)
        self.mainEngine.connect(self.gateway_name)
        self.connected = True

        # 注册定时器，用于判断重连
        self.mainEngine.eventEngine.register(EVENT_TIMER, self.onTimer)

        # 所有的日志监控
        self.logM = LogMonitor(self.mainEngine.eventEngine)
        self.errorM = ErrorMonitor(self.mainEngine.eventEngine)
        self.tradeM = TradeMonitor(self.mainEngine.eventEngine)
        self.orderM = OrderMonitor(self.mainEngine.eventEngine, self.mainEngine)
        self.positionM = PositionMonitor(self.mainEngine.eventEngine)
        self.accountM = AccountMonitor(self.mainEngine.eventEngine)

    #----------------------------------------------------------------------

def run_noui():
    # logFileName = './logs/' + u'noUiMain_{0}.log'.format(datetime.now().strftime('%m%d_%H%M'))
    logFileName   = './logs/' + u'noUiMain_{0}.log'.format(datetime.now().strftime('%m%d'))

    vtLogger= VtLogger() 
    vtLogger.run(filename=logFileName)
    noUi = NoUiMain()
    noUi.Start()

if __name__ == '__main__':
    thread = Thread(target=run_noui, args=())
    thread.start()
