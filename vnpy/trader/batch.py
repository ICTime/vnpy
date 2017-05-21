# encoding: UTF-8
import sys 
from vnpy.trader.gateway.ctpGateway.ctpGateway import CtpGateway 
from vnpy.trader.gateway.ibGateway.ibGateway import IbGateway 

from vnpy.event.eventEngine import * 
from vtGateway import *
from vtEngine import *

def print_log(event):
    log = event.dict_['data']
    print ':'.join([log.logTime, log.logContent])
    

def testCTP():
    """测试"""
    # from PyQt4 import QtCore
    # app = QtCore.QCoreApplication(sys.argv)    

    eventEngine = EventEngine2()
    eventEngine.register(EVENT_LOG, print_log)
    eventEngine.start()
    
    gateway = CtpGateway(eventEngine)
    gateway.connect()

    sleep(5)
    req = VtSubscribeReq()
    req.symbol = 'IF1609'
    req.symbol = 'rb1710'
    req.symbol = 'm1709-P-2800'
    gateway.subscribe(req)
    req.symbol = 'rb1710'
    gateway.subscribe(req)

    # sleep(20)
    # req = VtOrderReq()
    # req.symbol = 'rb1605'
    # req.exchange = 'SHFE'
    # req.price = 1850
    # req.volume = 1
    # req.priceType = PRICETYPE_LIMITPRICE  
    # req.direction = DIRECTION_LONG 
    # req.offset    = OFFSET_OPEN
    # rtn = gateway.sendOrder(req)
    # sleep(5)
    # print "-----ABC ",rtn 
        
    # sys.exit(app.exec_())

def testIB():
    """测试"""
    # from PyQt4 import QtCore
    # app = QtCore.QCoreApplication(sys.argv)    

    eventEngine = EventEngine2()
    eventEngine.register(EVENT_LOG, print_log)
    eventEngine.start()
    
    gateway = IbGateway(eventEngine)
    gateway.connect()
    sleep(5)
    print "Debug after sleep " 

    # productClass: FUT STK CFD CASH OPT
    # exchange SGX HKFE GLOBEX ECBOT 
    # currency USD HKD JPY UER GBP 
    req = VtSubscribeReq()
    req.symbol   = 'XINA50'
    req.expiry   = '201608'

    req.currency = 'HKD'
    req.symbol   = 'MHI'
    req.expiry   = '201607'

    # GLOBEX: ES GBP AUD NQ  CL 
    req.symbol   = 'ES'
    req.symbol   = 'GBP'
    req.expiry   = '201602'

    # ECBOT: ZS ZC ZW ZN ZB
    req.symbol   = 'ZC'
    req.expiry   = '201603'

    # NYMEX: CL 
    req.symbol   = 'KC'

    # SMART: NVDA SPY
    # 'STK' 'CNH' 600000.SEHKNTL

    # req.productClass = 'CFD'
    # req.currency = 'USD'
    # req.exchange = 'SMART'
    # req.symbol   = 'IBUS500'
    # req.expiry   = ''

    req.currency = 'HKD'
    req.symbol   = 'MHI'
    req.exchange = 'HKFE'
    req.expiry   = '201607'

    # req.productClass = 'STK'
    # req.exchange = 'SMART'
    # req.symbol   = 'NVDA'
    # req.expiry   = ''


    req.productClass = 'FUT'
    req.currency = 'USD'
    req.exchange = 'GLOBEX'
    req.symbol   = 'ES'
    req.expiry   = '201706'

    req.currency = 'HKD'
    req.symbol   = 'MHI'
    req.exchange = 'HKFE'
    req.expiry   = '201705'
    print '------AA', req.__dict__
    gateway.subscribe(req)

    # gateway.getRealBars(req,1,"TRADES") 
    # gateway.getHistBars(req, "20170301 00:00:00", "1 W", "1 day", "TRADES")
    # gateway.getHistBars(req, "20160724 00:00:00", "1 W", "1 min", "TRADES")

    # # gateway.subscribe(req)
    # gateway.getRealBars(req,1,"MIDPOINT") 
    # req.symbol   = 'IBUST100'
    # gateway.getRealBars(req,1,"MIDPOINT") 
    # req.symbol   = 'IBDE30'
    # req.currency = 'EUR'
    # gateway.getRealBars(req,1,"MIDPOINT") 

    # gateway.getHistBars(req, "20160205 00:00:00", "1 W", "1 hour", "MIDPOINT")
    req.symbol 	 = 'N225M'
    req.currency = 'JPY'
    req.exchange = 'OSE.JPN'
    req.expiry 	 = '201706'
    # gateway.subscribe(req)
    # gateway.getHistBars(req, "20170301 00:00:00", "1 W", "1 day", "TRADES")

    # gateway.getHistBars(req, "20160128 00:00:00", "1 D", "1 hour", "TRADES")
    # sys.exit(app.exec_())

def testCTA_CTP():
    from time import sleep

    # connect to gateway  
    # app = QtCore.QCoreApplication(sys.argv)    
    mainEngine=MainEngine()
    mainEngine.eventEngine.register(EVENT_LOG, print_log)
    mainEngine.connect('CTP') 

    sleep(5)
    mainEngine.ctaEngine.loadSetting()
    mainEngine.ctaEngine.initStrategy('SMA1')
    mainEngine.ctaEngine.startStrategy('SMA1')

    sleep(10000)
    mainEngine.gatewayDict['CTP'].close()
    mainEngine.eventEngine.stop()
    mainEngine.dataEngine.saveContracts()

    # sys.exit(app.exec_())

def testCTA_IB():
    from time import sleep

    # connect to gateway  
    # app = QtCore.QCoreApplication(sys.argv)    
    mainEngine=MainEngine()
    mainEngine.eventEngine.register(EVENT_LOG, print_log)
    mainEngine.connect('IB') 

    sleep(2)
    mainEngine.ctaEngine.loadSetting()
    mainEngine.ctaEngine.initStrategy('SMA1')
    mainEngine.ctaEngine.startStrategy('SMA1')

    sleep(100000)
    mainEngine.gatewayDict['IB'].close()
    mainEngine.eventEngine.stop()
    mainEngine.dataEngine.saveContracts()


if __name__ == '__main__':
    testCTA_CTP()
    # testCTA_IB()
    # testCTP()
    # testIB()
