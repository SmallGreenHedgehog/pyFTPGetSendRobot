# -*- coding: utf8 -*-
import os
import ftplib
import socks

class Cp1251FTP(ftplib.FTP):
   def putline(self, line):
        line = line + '\r\n'
        if self.debugging > 1:
            print('*put*', self.sanitize(line))
        self.sock.sendall(line.encode('cp1251'))

def log(text):
    print(text)
    #TODO реализовать человеческое логирование


def getparamsfromstring(line):
    params=[]
    lenline=len(line)
    i=0
    par=''
    while (i<lenline) and not(line[i]=='\n'):
        sym=line[i]
        if sym==';':
            # log(par)
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
    log('*********************************************')
    log('Удаление файлов:')

    countdelfiles=len(filelist)
    if countdelfiles>0:
        for i in range(0,countdelfiles):
            curfile=filelist[i]
            log('Удаляем файл "'+curfile+'".')
            succes=1
            try:
                os.remove(curfile)
            except NameError:
                succes=0
            if succes==1:
                log('Файл "'+curfile+'" успешно удален.')
            else:
                log('Ошибка удаления файла "'+curfile+'".')
    log('*********************************************')

def sendfiles(localDir, FTPHost, FTPPort, FTPDir, FTPLogin, FTPPass):
    #Сначала проверим есть ли файлы в указанной директории
    files=os.listdir(localDir)
    countfiles=len(files)

    if countfiles>0: #Если есть файлы в директории, то попытаемся их отправить
        log('*********************************************')
        log('Отправка файлов:')
        fordelfileslist=[]

        #Создаем подключение
        FtpConnect=Cp1251FTP(FTPHost,FTPLogin,FTPPass)
        if not(FTPDir==''):
            FtpConnect.cwd(FTPDir)
        for i in range(0, countfiles):
            curfile=files[i]
            curfullfile=localDir+'\\'+curfile
            log('Отправляем "'+str(curfullfile)+'"')
            sendfileFTP = open(curfullfile,'rb')
            success=1
            try:
                FtpConnect.storbinary('STOR '+curfile, sendfileFTP)
            except:
                success=0
            sendfileFTP=''

            if success==1:
                # Если файл был успешно передан - добавим файлы в список удаляемых
                # (#TODO в будующем необходимо реализовать перенос в архив в соответствии с конфигом)
                log('Файл "'+curfile+'" успешно отправлен.')
                fordelfileslist.append(curfullfile)
            else:
                log('Ошибка отправки файла "'+curfile+'"!')
        FtpConnect.close()
        FtpConnect=''
        log('*********************************************')

        removefiles(fordelfileslist)
    else:
        log('Файлов в каталоге "'+localDir+'" не найдено.')

def getfiles(localDir, FTPHost, FTPPort, FTPDir, FTPLogin, FTPPass):
    #TODO реализовать получение
    log('Получение файлов еще не реалзиовано.')

def processline(params):
    localDir=params[0]
    FTPHost=params[1]
    FTPPort=params[2]
    FTPDir=params[3]
    FTPLogin=params[4] #Логин и пароль пока храним в открытом виде,
    FTPPass=params[5] #позже добавим шифрование
    FTPMethod=params[6]
    SigText=params[7]

    #В зависимости от метода передачи получим или отправим файлы
    if int(FTPMethod)==0: #Отправка файлов
        sendfiles(localDir, FTPHost, FTPPort, FTPDir, FTPLogin, FTPPass)
    elif FTPMethod==1: #Получение файлов
        getfiles(localDir, FTPHost, FTPPort, FTPDir, FTPLogin, FTPPass)

def initial():
    global pathtoscript
    global conffilepath
    global confproxyfilepath

    succes=1
    pathtoscript=os.getcwd()
    conffilepath=pathtoscript+'\config.cfg'
    confproxyfilepath=pathtoscript+'\proxy.cfg'

    if not(os.path.exists(conffilepath)): #Проверяем наличие основного конфига
        succes=0
        log('Ошибка! Отсутсвует файл "'+conffilepath+'" конфига.')

    if os.path.exists(confproxyfilepath): #Конфиг прокси существует
        log('Найден конфиг прокси. Подгружаем параметры.')
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
                log('Работаем через '+proxyType+' прокси ('+proxyHost+':'+proxyPort+').')
        else:
            succes=0
            log('Ошибка! Конфиг прокси не корректен!')
    else:
        log('Конфиг прокси не найден. Работаем с прямым соединением.')
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
                log('Недопустимое количество параметров в строке №'+str(i+1)+'!')
else:
    log('Инициализая параметров скрипта не удачна! Проверьте логи и конфигурационные файлы!')