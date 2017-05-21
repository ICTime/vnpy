# encoding: UTF-8

'''
本文件中实现了行情数据记录引擎，用于汇总TICK数据，并生成K线插入数据库。

使用DR_setting.json来配置需要收集的合约，以及主力合约代码。
'''

import json
import os
import copy
from collections import OrderedDict
from datetime import datetime, timedelta
from Queue import Queue
from threading import Thread

from vnpy.event import Event
from vnpy.trader.vtEvent import *
from vnpy.trader.vtFunction import todayDate
from vnpy.trader.vtObject import VtSubscribeReq, VtLogData, VtBarData, VtTickData

from vnpy.trader.dataRecorder.drBase import *
from vnpy.trader.dataRecorder.language import text


########################################################################
class DrEngine(object):
    """数据记录引擎"""
    
    settingFileName = 'DR_setting.json'
    path = os.path.abspath(os.path.dirname(__file__))
    settingFileName = os.path.join(path, settingFileName)    

    #----------------------------------------------------------------------
    def __init__(self, mainEngine, eventEngine):
        """Constructor"""
        self.mainEngine = mainEngine
        self.eventEngine = eventEngine
        
        # 当前日期
        self.today = todayDate()
        
        # 主力合约代码映射字典，key为具体的合约代码（如IF1604），value为主力合约代码（如IF0000）
        self.activeSymbolDict = {}
        
        # Tick对象字典
        self.tickDict = {}
        
        # K线对象字典
        self.barDict = {}
        
        # 负责执行数据库插入的单独线程相关
        self.active = False                     # 工作状态
        # self.queue = Queue()                    # 队列
        # self.thread = Thread(target=self.run)   # 线程
        
        # 载入设置，订阅行情
        self.loadSetting()
        
    #----------------------------------------------------------------------
    def loadSetting(self):
        """载入设置"""
        print self.settingFileName

        with open(self.settingFileName) as f:
            drSetting = json.load(f)
            
            # 如果working设为False则不启动行情记录功能
            working = drSetting['working']
            if not working:
                return
            
            if 'tick' in drSetting:
                l = drSetting['tick']
                
                for setting in l:
                    symbol = setting[0]
                    vtSymbol = symbol

                    req = VtSubscribeReq()
                    req.symbol   = setting[0]
                    req.exchange = setting[2]
                    self.mainEngine.subscribe(req, setting[1])
                    
                    tick = VtTickData()           # 该tick实例可以用于缓存部分数据（目前未使用）
                    self.tickDict[vtSymbol] = tick
                    
            if 'bar' in drSetting:
                l = drSetting['bar']
                
                for setting in l:
                    bar = VtBarData() 

                    # FOR CTP:  vtSymbol is symbol
                    if len(setting)==3:
                        vtSymbol = setting[0]
                        req = VtSubscribeReq()
                        req.symbol   = setting[0]
                        req.exchange = setting[2]
                        bar.symbol = req.symbol 
                        bar.vtSymbol = vtSymbol 
                        bar.gatewayName = setting[1]
                        bar.exchange    = setting[2]
    
                    # FOR IB:  vtSymbol is symbol-expiry.exchange 
                    if len(setting)==5:
                        symbollist= setting[0].split('-')
                        req.symbol = symbollist[0] 
                        req.expiry = symbollist[1] 
                        req.exchange     = setting[2]
                        req.currency     = setting[3]
                        req.productClass = setting[4]                    
                        
                        bar.symbol   = req.symbol 
                        bar.exchange = req.exchange 
                        bar.gatewayName = setting[1]
                        vtSymbol = '.'.join([setting[0], req.exchange])
                        bar.vtSymbol = vtSymbol 
                        
                    print '---------- DrEngine.loadSetting req', vtSymbol, req.__dict__
                    print '---------- DrEngine.loadSetting bar', vtSymbol, bar.__dict__
                    self.mainEngine.subscribe(req, setting[1])  
                    self.barDict[vtSymbol] = bar

            # 启动数据插入线程
            # self.start()
            
            # 注册事件监听
            self.registerEvent()    

            print '---------- DrEngine.loadSetting end', self.barDict
    #----------------------------------------------------------------------
    def procecssTickEvent(self, event):
        """处理行情推送"""
        tick = event.dict_['data']
        vtSymbol = tick.vtSymbol
        # print '----- DrEngine.procecssTickEvent', vtSymbol,tick.__dict__ 

        # 转化Tick格式
        if not tick.datetime:
            tick.datetime = datetime.strptime(' '.join([tick.date, tick.time]), '%Y%m%d %H:%M:%S.%f')            

        # 更新分钟线数据
        if vtSymbol in self.barDict:
            bar = self.barDict[vtSymbol]
            # 如果第一个TICK或者新的一分钟
            # if not bar.datetime or bar.datetime.minute != tick.datetime.minute:
            # using 5 seconds bars as min bars  
            # if not bar.datetime or bar.datetime.minute != tick.datetime.minute or (tick.datetime.second % 5 ==0 and str(tick.time).endswith('.0')):    
            if not bar.datetime or bar.datetime.minute != tick.datetime.minute or (tick.datetime.second % 5 ==0 and tick.datetime.microsecond <= 100000):  
                if bar.vtSymbol:
                    newBar = copy.copy(bar)
                    self.putBarEvent(newBar)

                    self.writeDrLog(text.BAR_LOGGING_MESSAGE.format(symbol=bar.vtSymbol, 
                                                                    time=bar.time, 
                                                                    open=bar.open, 
                                                                    high=bar.high, 
                                                                    low=bar.low, 
                                                                    close=bar.close))
                         
                # bar.vtSymbol = tick.vtSymbol
                # bar.symbol = tick.symbol
                bar.exchange = tick.exchange
                
                bar.open = tick.lastPrice
                bar.high = tick.lastPrice
                bar.low = tick.lastPrice
                bar.close = tick.lastPrice
                
                bar.date = tick.date
                bar.time = tick.time
                bar.datetime = tick.datetime
                bar.volume = tick.volume
                bar.openInterest = tick.openInterest        
            # 否则继续累加新的K线
            else:                               
                bar.high = max(bar.high, tick.lastPrice)
                bar.low = min(bar.low, tick.lastPrice)
                bar.close = tick.lastPrice            

    #----------------------------------------------------------------------
    def registerEvent(self):
        """注册事件监听"""
        self.eventEngine.register(EVENT_TICK, self.procecssTickEvent)
 
    #----------------------------------------------------------------------
    def insertData(self, dbName, collectionName, data):
        """插入数据到数据库（这里的data可以是VtTickData或者VtBarData）"""
        self.queue.put((dbName, collectionName, data.__dict__))
        
    #----------------------------------------------------------------------
    def run(self):
        """运行插入线程"""
        while self.active:
            try:
                dbName, collectionName, d = self.queue.get(block=True, timeout=1)
                self.mainEngine.dbInsert(dbName, collectionName, d)
            except Empty:
                pass
            
    #----------------------------------------------------------------------
    def start(self):
        """启动"""
        self.active = True
        self.thread.start()
        
    #----------------------------------------------------------------------
    def stop(self):
        """退出"""
        if self.active:
            self.active = False
            self.thread.join()
        
    #----------------------------------------------------------------------
    def writeDrLog(self, content):
        """快速发出日志事件"""
        log = VtLogData()
        log.logContent = content
        event = Event(type_=EVENT_LOG)
        event.dict_['data'] = log
        self.eventEngine.put(event)   
    #----------------------------------------------------------------------
    def putBarEvent(self, bar) :
        """快速发出BAR事件"""
        event = Event(type_=EVENT_BAR)
        event.dict_['data'] = bar
        self.eventEngine.put(event)
        # print "----- putBarEvent ", bar.__dict__

    
