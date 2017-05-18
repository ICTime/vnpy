#encoding utf-8 

#----------------------------------------------------------------------
# from PyQt4 import QtCore
import sys
from time import sleep

from vtEngine  import MainEngine 
from vtGateway import VtSubscribeReq

def testCTP():
    # connect to gateway  
    # app = QtCore.QCoreApplication(sys.argv)    
    mainEngine=MainEngine()
    mainEngine.connect('CTP') 
    req = VtSubscribeReq()
    req.symbol = 'IF1709'
    req.symbol = 'rb1710'
    mainEngine.subscribe(req,'CTP') 

    # req.symbol = 'SR605'
    # req.symbol = 'm1605'
    # req.symbol = 'rb1605'
    # sys.exit(app.exec_())
def testIB():
    # connect to gateway  
    # app = QtCore.QCoreApplication(sys.argv)    
    mainEngine=MainEngine()
    mainEngine.connect('IB') 

    req = VtSubscribeReq()
    req.productClass = 'FUT'
    req.currency = 'USD'
    req.exchange = 'GLOBEX'
    req.symbol   = 'ES'
    req.expiry   = '201709'
    mainEngine.subscribe(req,'IB') 
    # sys.exit(app.exec_())

def testTDX():
    # connect to gateway  
    app = QtCore.QCoreApplication(sys.argv)    
    mainEngine=MainEngine()
    mainEngine.connect('TDX') 

    req = VtSubscribeReq()
    req.exchange = 'SZSE'
    req.symbol   = '150153'
    mainEngine.subscribe(req,'TDX') 
    sys.exit(app.exec_())

def testCTA_CTP():
    from time import sleep

    # connect to gateway  
    app = QtCore.QCoreApplication(sys.argv)    
    mainEngine=MainEngine()
    mainEngine.connect('CTP') 

 
    # gaive 10 second for CTP connect 
    sleep(5)
    mainEngine.ctaEngine.loadSetting()
    sleep(5)
    mainEngine.ctaEngine.initStrategy('SMA1')
    mainEngine.ctaEngine.startStrategy('SMA1')

    sleep(10000)
    mainEngine.gatewayDict['CTP'].close()
    mainEngine.eventEngine.stop()
    mainEngine.dataEngine.saveContracts()

    sys.exit(app.exec_())

def testCTA_IB():
    from time import sleep

    # connect to gateway  
    app = QtCore.QCoreApplication(sys.argv)    
    mainEngine=MainEngine()
    mainEngine.connect('IB') 
 
    mainEngine.ctaEngine.loadSetting()
    # mainEngine.ctaEngine.startStrategy('SMA1')

    sleep(300)

    sys.exit(app.exec_())

def testCTA_TDX():
    from time import sleep

    # connect to gateway  
    app = QtCore.QCoreApplication(sys.argv)    
    mainEngine=MainEngine()
    mainEngine.connect('TDX') 

    sleep(5)
 
    mainEngine.ctaEngine.loadSetting()
    # mainEngine.ctaEngine.startStrategy('SMA1')
    sleep(300)
    sys.exit(app.exec_())


def testCTA_ALL():
    from time import sleep

    # connect to gateway  
    app = QtCore.QCoreApplication(sys.argv)    
    mainEngine=MainEngine()
    mainEngine.connect('IB') 
    mainEngine.connect('CTP') 
    mainEngine.connect('TDX') 

    # gaive 10 second for CTP connect 
    sleep(5)
 
    mainEngine.ctaEngine.loadSetting()
    # mainEngine.ctaEngine.initStrategy('SMA1')
    # mainEngine.ctaEngine.startStrategy('SMA1')

    sleep(300)
    sys.exit(app.exec_())
if __name__ == '__main__':
    testCTP()
    # testIB()
    # testTDX()
    # testCTA_CTP()
    # testCTA_IB()
    # testCTA_TDX()
    # testCTA_ALL()
