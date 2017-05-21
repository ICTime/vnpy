def testCTA_CTP():
    from time import sleep

    # connect to gateway  
    # app = QtCore.QCoreApplication(sys.argv)    
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

    # sys.exit(app.exec_())

