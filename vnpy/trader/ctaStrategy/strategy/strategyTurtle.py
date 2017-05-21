# encoding: UTF-8

'''
Turtle Trading System:
1U long or short at 20 Day High Low, Addig 1U at 1ATR
2ATR stop loss(touch), 1U SL is 1%, 2U SL is 1.5%, 10 Day H/L  for Trailing (close)
Adding risk free (2U/2U) at first two correction bar

STATE:  
FLAT  - LONG                      FLAT  - SHORT
LONG  - LADD1                     SHORT - LADD1  
LONG  - STOP - FLAT               SHORT - STOP - FLAT  
LADD1 - STOP - FLAT               SADD1 - STOP - FLAT  
LADD1 - LADD2                     SADD1 - SADD2 
LADD2 - STOP - FLAT               SADD2 - STOP - FLAT  
LADD2 - LADD3                     SADD2 - SADD3 
LADD3 - STOP - FLAT               SADD3 - STOP - FLAT  

'''

from __future__ import division

from vnpy.trader.vtObject import VtBarData
from vnpy.trader.vtConstant import EMPTY_STRING, EMPTY_FLOAT
from vnpy.trader.ctaStrategy.ctaTemplate import  CtaTemplate 
import json 
import os 

########################################################################
class TurtleStrategy(CtaTemplate):
    className = 'TurtleStrategy'
    author = u'ICTime'
    
    # 策略参数
    entryDays = 20  # 20天高低点开仓
    trailDays = 10  # 10跟踪止损
    initDays  = 20  # 初始化数据所用的天数
    
    # 策略变量
    bar = None
    barMinute = EMPTY_STRING
    
    # 参数列表，保存了参数的名称
    paramList = ['name',
                 'className',
                 'author',
                 'vtSymbol',
                 'entryDays',
                 'trailDays']    
    
    # 变量列表，保存了变量的名称
    varList = ['inited',
               'trading',
               'pos'
               ]  

    #----------------------------------------------------------------------
    def __init__(self, ctaEngine, setting):
        """Constructor"""
        super(TurtleStrategy, self).__init__(ctaEngine, setting)
        print '---- TurtleStrategy.__init__', 

        self.positionDict = {}  
        
    #----------------------------------------------------------------------
    def onInit(self):
        """初始化策略（必须由用户继承实现）"""
        self.writeCtaLog(u'TurtleStrategy onInit')
        # print '---- TurtleStrategy.onInit1', self.vtSymbol 

        """载入历史数据 """
        for vtSymbol in self.vtSymbol: 
            initData = self.loadBar(vtSymbol,'day',self.initDays)
            print initData 

        """载入历史仓位 """
        filepath = os.path.abspath(os.path.join(__file__ ,"../../../database", self.className + '.pos.json'))
        with open(filepath) as fp:
            self.positionDict= json.load(fp)
        print '---- TurtleStrategy.onInit', self.positionDict 

    #----------------------------------------------------------------------
    def onStart(self):
        """启动策略（必须由用户继承实现）"""
        self.writeCtaLog(u'双EMA演示策略启动')
        self.putEvent()
    
    #----------------------------------------------------------------------
    def onStop(self):
        """停止策略（必须由用户继承实现）"""
        self.writeCtaLog(u'双EMA演示策略停止')
        self.putEvent()
        
    #----------------------------------------------------------------------
    def onTick(self, tick):
        # print "---------- ctaStrategy.strategy.strategyTurtle.onTick:", tick.symbol, tick.time, tick.lastPrice
        pass 

    #----------------------------------------------------------------------
    def onBar(self, bar):
        """收到Bar推送（必须由用户继承实现）"""
        # 判断买卖
        print "---------- ctaStrategy.strategy.strategyTurtle.onBar:", bar.vtSymbol, bar.time, bar.close  

    #----------------------------------------------------------------------
    def onOrder(self, order):
        """收到委托变化推送（必须由用户继承实现）"""
        # 对于无需做细粒度委托控制的策略，可以忽略onOrder
        pass
    
    #----------------------------------------------------------------------
    def onTrade(self, trade):
        """收到成交推送（必须由用户继承实现）"""
        # 对于无需做细粒度委托控制的策略，可以忽略onOrder
        pass
