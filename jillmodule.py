# -*- coding: utf8 -*-
__author__ = 'Jill'

import os
import logging
import shutil

class Jlog:
    __pathtoscript=os.getcwd()
    __maxfilesizeMB=10
    __logfilename='debug.log'
    __fullfilepath=__pathtoscript+'\\'+__logfilename
    __needprinttext=False

    def setlogfilename(self, logfilename='debug.log'):
        self.__logfilename=logfilename
        self.__fullfilepath=self.__pathtoscript+'\\'+self.__logfilename

    def setmaxfilesizeMB(self, maxfilesizeMB=10):
        self.__maxfilesizeMB=maxfilesizeMB

    def setneedprinttext(self, needprinttext=False):
        self.__needprinttext=needprinttext


    def message(self, text, typemes=1):
        if self.__needprinttext:
            print(text)

        if os.path.exists(self.__fullfilepath): #Если файл существует - проверим его размер
            #Если файл больше максимального значения - переименовываем
            if os.path.getsize(self.__fullfilepath)>self.__maxfilesizeMB*1024**2:
                shutil.move(self.__fullfilepath,self.__fullfilepath+'.bak')

        logging.basicConfig(format = u'%(levelname)-8s [%(asctime)s] %(message)s', level = logging.DEBUG, filename = u''+self.__logfilename)
        if typemes==1:
            logging.info(text)
        else:
            logging.error(text)