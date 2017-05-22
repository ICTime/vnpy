#!/usr/bin/env python
# coding=utf8

import logging
import threading
import logging.config
from logging import handlers


########################################################################
class ExtFormatter(logging.Formatter):

    #----------------------------------------------------------------------
    def __init__(self, colorful=False, simple=False):
        self.SIMPLE_FORMAT = "[%(asctime)s] %(message)s"
        self.RECORD_FORMAT = "[%(asctime)s.%(msecs)d][%(filename)s:%(lineno)d][%(process)d:%(threadName)s] %(message)s"
        self.COLOR_FORMAT = {
            'DEBUG': "\033[1;34m%(levelname)s\033[0m: ",
            'INFO': "\033[1;32m%(levelname)s\033[0m: ",
            'WARNING': "\033[1;33m%(levelname)s\033[0m: ",
            'ERROR': "\033[1;31m%(levelname)s\033[0m: ",
        }
        self.DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


        self._colorful = colorful
        self._simple = simple
        logging.Formatter.__init__(self, datefmt=self.DATE_FORMAT)


    #----------------------------------------------------------------------
    def format(self, record):
        fmt = self.SIMPLE_FORMAT if self._simple else self.RECORD_FORMAT
        if self._colorful:
            self._fmt = self.COLOR_FORMAT[record.levelname] + fmt
        else:
            self._fmt = "%(levelname)s: " + fmt
        return logging.Formatter.format(self, record)


########################################################################
class BasicFormatter(ExtFormatter):
    def __init__(self):
        # super(BasicFormatter, self).__init__()
        super(BasicFormatter, self).__init__(simple=True)
        # super(BasicFormatter, self).__init__(colorful=True)

# thread_data = threading.local()


########################################################################
class VtLogger(object):
    """主引擎"""
    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""

    #----------------------------------------------------------------------
    def setup_logger(self,filename=None):
        LOGGING = {
            'version': 1,
            'disable_existing_loggers': True,
            'formatters': {
                'basic': {
                    '()': BasicFormatter,
                },
            },
            'handlers': {
                'local_info': {
                    'level': 'DEBUG',
                    '()': handlers.TimedRotatingFileHandler,
                    'filename': filename,
                    'formatter': 'basic',
                    'interval': 1,
                    'when': 'D',
                },
            },
            'loggers': {
                '': {
                    'level': 'DEBUG',
                    'handlers': ['local_info'],
                    'propagate': True,
                }
            },
        }
    
        logging.config.dictConfig(LOGGING)
        return LOGGING
    #----------------------------------------------------------------------
