# -*- coding: utf8 -*-
import os
import ftplib
import socks
from jillmodule import Jlog

def getparamsfromstring(line):
    params=[]
    lenline=len(line)
    i=0
    par=''
    while (i<lenline) and not(line[i]=='\n'):
        sym=line[i]
        if sym==';':
            params.append(par)
            par=''
        else:
            par+=sym
        i+=1
    return params

def getlinesfromconfig():
    conffile=open(conffilepath)
    conflines=conffile.readlines()
    conffile.close()
    return conflines

def removefiles(filelist):
    log.message('---------------------------------------------')
    log.message('Удаление файлов:')

    countdelfiles=len(filelist)
    if countdelfiles>0:
        for i in range(0,countdelfiles):
            curfile=filelist[i]
            log.message('Удаляем файл "'+curfile+'".')
            succes=1
            try:
                os.remove(curfile)
            except:
                succes=0
            if succes==1:
                log.message('Файл "'+curfile+'" успешно удален.')
            else:
                log.message('Ошибка удаления файла "'+curfile+'".',0)
    else:
        log.message('Список файлов на удаление пуст.')
    log.message('---------------------------------------------')

def sendfiles(localDir, FTPHost, FTPPort, FTPDir, FTPLogin, FTPPass):
    #Сначала проверим есть ли файлы в указанной директории
    files=os.listdir(localDir)
    countfiles=len(files)

    if countfiles>0: #Если есть файлы в директории, то попытаемся их отправить
        log.message('*********************************************')
        log.message('Отправка файлов:')
        fordelfileslist=[]

        #Создаем подключение
        success=1
        try:
            # FtpConnect=Cp1251FTP(FTPHost,FTPLogin,FTPPass)
            FtpConnect=ftplib.FTP(FTPHost,FTPLogin,FTPPass)
            FtpConnect.encoding='cp1251'
        except:
            log.message('Ошибка! Соединение с FTP сервером не установлено. Проверьте настройки конфига.',0)
            success=0

        if success==1:
            log.message('Соединение с FTP сервером успешно установлено.')
            if not(FTPDir==''):
                log.message('Переходим в указанную директорию ('+FTPDir+')')
                try:
                    FtpConnect.cwd(FTPDir)
                except:
                    success=0
            if success==0:
                log.message('Указанная директория ('+FTPDir+') не доступна или не существует.',0)
            else:
                for i in range(0, countfiles):
                    curfile=files[i]
                    curfullfile=localDir+'\\'+curfile
                    log.message('Отправляем "'+str(curfullfile)+'"')
                    sendfileFTP = open(curfullfile,'rb')
                    try:
                        FtpConnect.storbinary('STOR '+curfile, sendfileFTP)
                    except:
                        success=0
                    sendfileFTP=''

                    if success==1:
                        # Если файл был успешно передан - добавим файлы в список удаляемых
                        #TODO в будущем необходимо реализовать перенос в архив в соответствии с конфигом
                        log.message('Файл "'+curfile+'" успешно отправлен.')
                        fordelfileslist.append(curfullfile)
                    else:
                        log.message('Ошибка отправки файла "'+curfile+'"!',0)
            FtpConnect.close()
        FtpConnect=''
        removefiles(fordelfileslist)
        log.message('Отправка файлов завершена.')
        log.message('*********************************************')
    else:
        log.message('Файлов в каталоге "'+localDir+'" не найдено.')

def getfiles(localDir, FTPHost, FTPPort, FTPDir, FTPLogin, FTPPass):
    log.message('*********************************************')
    log.message('Получение файлов:')
    success=1
    try:
        FtpConnect=ftplib.FTP(FTPHost,FTPLogin,FTPPass)
        FtpConnect.encoding='cp1251'
    except:
        log.message('Ошибка! Соединение с FTP сервером не установлено. Проверьте настройки конфига.',0)
        success=0
    if success==1:
        log.message('Соединение с FTP сервером успешно установлено.')
        remotefiles=[]
        if not(FTPDir==''):
            log.message('Переходим в указанную директорию ('+FTPDir+')')
            try:
                FtpConnect.cwd(FTPDir)
            except:
                success=0
        if success==0:
            log.message('Указанная директория ('+FTPDir+') не доступна или не существует.',0)
        else:
            log.message('Получаем список файлов (без поддиректорий)')
            files=FtpConnect.nlst()
            for i in range(0,len(files)):
                filename=files[i]
                tmpfilename=filename.replace('я','Я') #Обходим проблему непонимания маленькой "я" на FTP IIS

                #Проверяем не является ли файл папкой
                isfolder=1
                try:
                    FtpConnect.cwd(FTPDir+'/%s' % tmpfilename)
                    FtpConnect.cwd(FTPDir)
                except:
                    isfolder=0
                if isfolder==0: # Это файл, добавляем в список для получения
                    log.message('Добавляем файл "'+filename+'" в список для получения')
                    remotefiles.append(filename)

            countfiles=len(remotefiles)
            if countfiles>0:
                fordelfileslist=[]

                for i in range(0, countfiles):
                    success=1
                    curfile=remotefiles[i]
                    curfullfile=localDir+'\\'+curfile
                    log.message('Получаем "'+str(curfile)+'" в "'+curfullfile+'"')
                    getfileFTP = open(curfullfile,'wb')
                    try:
                        FtpConnect.retrbinary('RETR %s' % curfile, getfileFTP.write)
                    except:
                        success=0
                    if success==1:
                        log.message('Файл "'+curfile+'" успешно получен.')
                        fordelfileslist.append(curfile)
                    else:
                        log.message('Ошибка получения файла "'+curfile+'"')
                    getfileFTP=''
                log.message('---------------------------------------------')
                log.message('Удаляем полученные файлы с FTP')
                countfiles=len(fordelfileslist)
                if countfiles>0:
                    for i in range(0, countfiles):
                        curfile=fordelfileslist[i]
                        success=1
                        try:
                            FtpConnect.delete(curfile)
                        except:
                            success=0
                        if success==1:
                            log.message('Файл "'+curfile+'" успешно удален с FTP сервера')
                        else:
                            log.message('Ошибка удаления файла "'+curfile+'" c FTP сервера')
                else:
                    log.message('Нет файлов на удаление с FTP')
                log.message('---------------------------------------------')
            else:
                log.message('Нет файлов в указанной директории')
    FtpConnect.close()
    FtpConnect=''
    log.message('Получение файлов завершено.')
    log.message('*********************************************')

def processline(params):
    localDir=params[0]
    FTPHost=params[1]
    FTPPort=params[2]
    FTPDir=params[3]
    FTPLogin=params[4] #Логин и пароль пока храним в открытом виде,
    FTPPass=params[5] #позже добавим шифрование
    FTPMethod=int(params[6])
    SigText=params[7]

    #В зависимости от метода передачи получим или отправим файлы
    #TODO в дальнейшем можно добавить сжатие
    if int(FTPMethod)==0: #Отправка файлов
        sendfiles(localDir, FTPHost, FTPPort, FTPDir, FTPLogin, FTPPass)
    elif FTPMethod==1: #Получение файлов
        getfiles(localDir, FTPHost, FTPPort, FTPDir, FTPLogin, FTPPass)
    #TODO добавить генерацию sig файла


def initial():
    global pathtoscript
    global conffilepath
    global confproxyfilepath
    global log

    log=Jlog()
    log.setmaxfilesizeMB(5)
    log.setneedprinttext(True)
    log.setlogfilename('ftprobot.log')

    log.message('')
    log.message('START SCRIPT')
    succes=1
    pathtoscript=os.getcwd()
    conffilepath=pathtoscript+'\config.cfg'
    confproxyfilepath=pathtoscript+'\proxy.cfg'

    if not(os.path.exists(conffilepath)): #Проверяем наличие основного конфига
        succes=0
        log.message('Ошибка! Отсутсвует файл "'+conffilepath+'" конфига.')

    if os.path.exists(confproxyfilepath): #Конфиг прокси существует
        log.message('Найден конфиг прокси. Подгружаем параметры.')
        correct=1

        confproxyfile=open(confproxyfilepath)
        confproxylines=confproxyfile.readlines()
        countlines=len(confproxylines)
        confproxyfile.close()
        if countlines<1:
            correct=0

        if correct==1:
            proxyline=confproxylines[0]
            proxyparams=getparamsfromstring(proxyline)
            if len(proxyparams)<4:
                correct=0

        if correct==1:
            proxyType=proxyparams[0]
            proxyHost=proxyparams[1]
            proxyPort=proxyparams[2]
            proxyLogin=proxyparams[3] # Логин и пароль пока храним в открытом виде,
            proxyPass=proxyparams[4] #TODO добавить шифрование для хранения паролей
            if proxyType.lower()=='http':
                sockproxyType=socks.PROXY_TYPE_HTTP
            elif proxyType.lower()=='sock5':
                sockproxyType=socks.PROXY_TYPE_SOCKS5
            try:
                socks.setdefaultproxy(sockproxyType,proxyHost,int(proxyPort),True,proxyLogin,proxyPass)
            except:
                succes=0
            if succes==1:
                log.message('Работаем через '+proxyType+' прокси ('+proxyHost+':'+proxyPort+').')
        else:
            succes=0
            log.message('Ошибка! Конфиг прокси не корректен!')
    else:
        log.message('Конфиг прокси не найден. Работаем с прямым соединением.')
    return succes

if initial(): #Инициализация
    conflines=getlinesfromconfig() #Получаем строки из конфига
    countlines=len(conflines)

    if countlines>0: #Построчно получаем параметры
        for i in range(0, countlines):
            line=conflines[i]
            params=getparamsfromstring(line)

            #Теперь перезапишем параметры строки в переменные
            if len(params)>6:
                processline(params)
            else:
                log.message('Недопустимое количество параметров в строке №'+str(i+1)+'!')
else:
    log.message('Инициализая параметров скрипта не удачна! Проверьте логи и конфигурационные файлы!')