#!/usr/local/bin/python3
# -*- conding: utf8 -*-

import configparser
import os
import abc

import tool

from tool import mkDir, raiseIf


class MBase(object):
    __metaclass__ = abc.ABCMeta

    #首页的soup对象
    mainPage = None

    #网站首页地址
    url = None

    #配置文件对象
    conf = None

    #要抓取的网站标志
    mark = None

    #当前网页的保存跟目录
    base_path = None

    @abc.abstractmethod
    def getRootUrl(self):
        pass

    @abc.abstractmethod
    def getMark(self):
        pass

    def __init__(self):
        self.__loadConfig()

        self.__prepareAll()
        self.__checkAll()

    def __loadConfig(self, fileName = 'conf.ini'):
        self.conf = configparser.ConfigParser()
        if not os.path.exists(fileName):
            raise FileNotFoundError
        self.conf.read(fileName)


    def __prepareAll(self):
        self.url = self.getRootUrl()
        self.mark = self.getMark()
        self.__prepareBasePath()



    def __checkAll(self):
        raiseIf(self.mark == None)
        raiseIf(self.url == None)
        raiseIf(self.conf == None)
        raiseIf(self.base_path == None)
        raiseIf(not os.path.exists(self.base_path))

    def getConfig(self, key):
        con = self.conf.get('config', key)
        if con == '' or con == None:
            raise ValueError('配置未找到' + str(key))
        return con

    def __prepareBasePath(self):
        basePath = self.getConfig('db_image_path')
        print(basePath)
        exit(1)
        if basePath[-1:] != '/':
            basePath += '/'
        self.base_path = basePath + self.mark + '/'
        mkDir(self.base_path)

    def loadMainPage(self):
        self.mainPage = tool.getHtmlAsSoup(self.url)


