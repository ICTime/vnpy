# encoding: UTF-8

import shelve
import os 
from collections import OrderedDict
from datetime import datetime
import numpy as np 

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

from vnpy.event import *
from vnpy.trader.vtGlobal import globalSetting
from vnpy.trader.vtEvent import *
from vnpy.trader.vtGateway import *
from vnpy.trader.language import text

from vnpy.trader.gateway import GATEWAY_DICT
from vnpy.trader.dataRecorder.drEngine import DrEngine
from vnpy.trader.ctaStrategy.ctaEngine import CtaEngine
from vnpy.trader.riskManager.rmEngine import RmEngine


########################################################################
class MainEngine(object):
    """主引擎"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        # 记录今日日期
        self.todayDate = datetime.now().strftime('%Y%m%d')
        
        # 创建事件引擎
        self.eventEngine = EventEngine2()
        self.eventEngine.start()
        
        # 创建数据引擎
        self.dataEngine = DataEngine(self.eventEngine)
        
        # MongoDB数据库相关
        self.dbClient = None    # MongoDB客户端对象
        
        # 调用一个个初始化函数
        self.initGateway()

        # 扩展模块
        self.ctaEngine = CtaEngine(self, self.eventEngine)
        self.drEngine = DrEngine(self, self.eventEngine)
        self.rmEngine = RmEngine(self, self.eventEngine)
        
    #----------------------------------------------------------------------
    def initGateway(self):
        """初始化接口对象"""
        # 用来保存接口对象的字典
        self.gatewayDict = OrderedDict()
        
        # 遍历接口字典并自动创建所有的接口对象
        for gatewayModule in GATEWAY_DICT.values():
            try:
                self.addGateway(gatewayModule.gateway, gatewayModule.gatewayName)
                if gatewayModule.gatewayQryEnabled:
                    self.gatewayDict[gatewayModule.gatewayName].setQryEnabled(True)
            except Exception, e:
                print e

    #----------------------------------------------------------------------
    def addGateway(self, gatewayClass, gatewayName=None):
        """创建接口"""
        self.gatewayDict[gatewayName] = gatewayClass(self.eventEngine, gatewayName)
        
    #----------------------------------------------------------------------
    def getGateway(self, gatewayName):
        """获取接口"""
        if gatewayName in self.gatewayDict:
            return self.gatewayDict[gatewayName]
        else:
            self.writeLog(text.GATEWAY_NOT_EXIST.format(gateway=gatewayName))
            return None
        
    #----------------------------------------------------------------------
    def connect(self, gatewayName):
        """连接特定名称的接口"""
        gateway = self.getGateway(gatewayName)
        
        if gateway:
            gateway.connect()
            
            # 接口连接后自动执行数据库连接的任务
            # self.dbConnect()        
   
    #----------------------------------------------------------------------
    def subscribe(self, subscribeReq, gatewayName):
        """订阅特定接口的行情"""
        gateway = self.getGateway(gatewayName)
        
        if gateway:
            gateway.subscribe(subscribeReq)
  
    #----------------------------------------------------------------------
    def sendOrder(self, orderReq, gatewayName):
        """对特定接口发单"""
        # 如果风控检查失败则不发单
        if not self.rmEngine.checkRisk(orderReq):
            return ''

        gateway = self.getGateway(gatewayName)
        
        if gateway:
            return gateway.sendOrder(orderReq)
        else:
            return ''
        
    #----------------------------------------------------------------------
    def cancelOrder(self, cancelOrderReq, gatewayName):
        """对特定接口撤单"""
        gateway = self.getGateway(gatewayName)
        
        if gateway:
            gateway.cancelOrder(cancelOrderReq)   
  
    #----------------------------------------------------------------------
    def qryAccount(self, gatewayName):
        """查询特定接口的账户"""
        gateway = self.getGateway(gatewayName)
        
        if gateway:
            gateway.qryAccount()      
        
    #----------------------------------------------------------------------
    def qryPosition(self, gatewayName):
        """查询特定接口的持仓"""
        gateway = self.getGateway(gatewayName)
        
        if gateway:
            gateway.qryPosition()
            
    #----------------------------------------------------------------------
    def exit(self):
        """退出程序前调用，保证正常退出"""        
        # 安全关闭所有接口
        for gateway in self.gatewayDict.values():        
            gateway.close()
        
        # 停止事件引擎
        self.eventEngine.stop()      
        
        # 停止数据记录引擎
        self.drEngine.stop()
        
        # 保存数据引擎里的合约数据到硬盘
        self.dataEngine.saveContracts()
    
    #----------------------------------------------------------------------
    def writeLog(self, content):
        """快速发出日志事件"""
        log = VtLogData()
        log.logContent = content
        event = Event(type_=EVENT_LOG)
        event.dict_['data'] = log
        self.eventEngine.put(event)        
    
    #----------------------------------------------------------------------
    def dbConnect(self):
        pass 
    
    #----------------------------------------------------------------------
    def dbInsert(self, dbName, collectionName, d):
        """向MongoDB中插入数据，d是具体数据"""
        if self.dbClient:
            db = self.dbClient[dbName]
            collection = db[collectionName]
            collection.insert_one(d)
        else:
            self.writeLog(text.DATA_INSERT_FAILED)
    
    #----------------------------------------------------------------------
    def dbQuery(self, dbName, collectionName, d):
        pass 

    #----------------------------------------------------------------------
    def getDayBars(self, vtSymbol, counts):
        print '-----VtEngine.getDayBars', vtSymbol,counts
        return self.dataEngine.getDayBars(vtSymbol, counts)

    #----------------------------------------------------------------------
    def getMinuteBars(self, vtSymbol, counts):
        return self.dataEngine.getMinuteBars(vtSymbol, counts)

    #----------------------------------------------------------------------
    def dbUpdate(self, dbName, collectionName, d, flt, upsert=False):
        """向MongoDB中更新数据，d是具体数据，flt是过滤条件，upsert代表若无是否要插入"""
        if self.dbClient:
            db = self.dbClient[dbName]
            collection = db[collectionName]
            collection.replace_one(flt, d, upsert)
        else:
            self.writeLog(text.DATA_UPDATE_FAILED)        
            
    #----------------------------------------------------------------------
    def dbLogging(self, event):
        """向MongoDB中插入日志"""
        log = event.dict_['data']
        d = {
            'content': log.logContent,
            'time': log.logTime,
            'gateway': log.gatewayName
        }
        self.dbInsert(LOG_DB_NAME, self.todayDate, d)
    
    #----------------------------------------------------------------------
    def getContract(self, vtSymbol):
        """查询合约"""
        return self.dataEngine.getContract(vtSymbol)
    
    #----------------------------------------------------------------------
    def getAllContracts(self):
        """查询所有合约（返回列表）"""
        return self.dataEngine.getAllContracts()
    
    #----------------------------------------------------------------------
    def getOrder(self, vtOrderID):
        """查询委托"""
        return self.dataEngine.getOrder(vtOrderID)
    
    #----------------------------------------------------------------------
    def getAllWorkingOrders(self):
        """查询所有的活跃的委托（返回列表）"""
        return self.dataEngine.getAllWorkingOrders()
    
    #----------------------------------------------------------------------
    def getAllGatewayNames(self):
        """查询引擎中所有可用接口的名称"""
        return self.gatewayDict.keys()
        
    

########################################################################
class DataEngine(object):
    """数据引擎"""
    contractFileName = 'ContractData.vt'

    #----------------------------------------------------------------------
    def __init__(self, eventEngine):
        """Constructor"""
        self.eventEngine = eventEngine
        
        # 保存合约详细信息的字典
        self.contractDict = {}
        
        # 保存委托数据的字典
        self.orderDict = {}

        #  
        self.dayBarsDict = {}
        self.minuteBarsDict = {}
        
        # 保存活动委托数据的字典（即可撤销）
        self.workingOrderDict = {}
        
        # 读取保存在硬盘的合约数据
        self.loadContracts()
        
        # 注册事件监听
        self.registerEvent()
        
    #----------------------------------------------------------------------
    def updateContract(self, event):
        """更新合约数据"""
        contract = event.dict_['data']
        # print '--------updateContract',contract.__dict__
        self.contractDict[contract.vtSymbol] = contract
        self.contractDict[contract.symbol] = contract       # 使用常规代码（不包括交易所）可能导致重复
        
    #----------------------------------------------------------------------
    def getContract(self, vtSymbol):
        """查询合约对象"""
        try:
            return self.contractDict[vtSymbol]
        except KeyError:
            return None
    
    
    #----------------------------------------------------------------------
    def convertDate(self,text):
        return datetime.strptime(text, '%Y-%m-%d')
    
    #----------------------------------------------------------------------
    def convertDatetime(self,text):
        return datetime.strptime(text, '%Y-%m-%d %H:%M:%S')

    #----------------------------------------------------------------------
    def loadDayBars(self, vtSymbol):
        columns = ('Timestamp', 'open','high','low','close','atr')
        filename = os.path.join('database',vtSymbol+'.day.csv') 
        bars = np.genfromtxt(filename,delimiter=",", skip_header=1, names=columns, dtype=None, converters={'Timestamp':self.convertDate})
        self.dayBarsDict[vtSymbol] = bars

    #----------------------------------------------------------------------
    def getDayBars(self, vtSymbol,counts):
        print '-----DataEngine.getDayBars',  vtSymbol,counts
        if not vtSymbol in self.dayBarsDict:
            self.loadDayBars(vtSymbol) 

        return self.dayBarsDict[vtSymbol][-counts:] 

    #----------------------------------------------------------------------
    def getMinuteBars(self, vtSymbol,counts):
        try:
            return self.minuteBarsDict[vtSymbol]
        except KeyError:
            return None
        
        
    #----------------------------------------------------------------------
    def getAllContracts(self):
        """查询所有合约对象（返回列表）"""
        return self.contractDict.values()
    
    #----------------------------------------------------------------------
    def saveContracts(self):
        """保存所有合约对象到硬盘"""
        f = shelve.open(self.contractFileName)
        f['data'] = self.contractDict
        f.close()
    
    #----------------------------------------------------------------------
    def loadContracts(self):
        """从硬盘读取合约对象"""
        f = shelve.open(self.contractFileName)
        if 'data' in f:
            d = f['data']
            for key, value in d.items():
                self.contractDict[key] = value
        f.close()
        
    #----------------------------------------------------------------------
    def updateOrder(self, event):
        """更新委托数据"""
        order = event.dict_['data']        
        self.orderDict[order.vtOrderID] = order
        
        # 如果订单的状态是全部成交或者撤销，则需要从workingOrderDict中移除
        if order.status == STATUS_ALLTRADED or order.status == STATUS_CANCELLED:
            if order.vtOrderID in self.workingOrderDict:
                del self.workingOrderDict[order.vtOrderID]
        # 否则则更新字典中的数据        
        else:
            self.workingOrderDict[order.vtOrderID] = order
        
    #----------------------------------------------------------------------
    def getOrder(self, vtOrderID):
        """查询委托"""
        try:
            return self.orderDict[vtOrderID]
        except KeyError:
            return None
    
    #----------------------------------------------------------------------
    def getAllWorkingOrders(self):
        """查询所有活动委托（返回列表）"""
        return self.workingOrderDict.values()
    
    #----------------------------------------------------------------------
    def registerEvent(self):
        """注册事件监听"""
        self.eventEngine.register(EVENT_CONTRACT, self.updateContract)
        self.eventEngine.register(EVENT_ORDER, self.updateOrder)
        
    
    
