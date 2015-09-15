# -*- coding: utf8 -*-
__author__ = 'jill'

import logging

class Jlog:
    maxfilesizeMB=10
    logfilename='debug'
    needprinttext=False

    def message(self, text, typemes=1):
        if self.needprinttext:
            print(text)
        logging.basicConfig(format = u'%(levelname)-8s [%(asctime)s] %(message)s', level = logging.DEBUG, filename = u''+self.logfilename+'.log')
        if typemes==1:
            logging.info(text)
        else:
            logging.error(text)