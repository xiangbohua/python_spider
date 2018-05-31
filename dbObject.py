#!/usr/local/bin/python3
# -*- conding: utf8 -*-
import abc

from tool import raiseIf

from pip._vendor.pyparsing import basestring

class DbObject:

    @abc.abstractmethod
    def getFields(self):
        raise Exception('方法必须实现')

    @abc.abstractmethod
    def getRuntimeProp(self):
        raise Exception('方法必须实现')

    def __init__(self, prop = {}):
        allProp = self.getFields() + self.getRuntimeProp()
        for attr in allProp:
            if isinstance(attr, list):
                initValue = self.tryGetValue(prop, attr[0])
                if initValue != None:
                    self.__dict__[attr[0]] = initValue
                else:
                    self.__dict__[attr[0]] = attr[1]
            elif isinstance(attr, basestring):
                self.__dict__[attr] = self.tryGetValue(prop, attr)

    def saveableObj(self):
        saveObj = {}
        for attr in self.getFields():
            if isinstance(attr, list):
                saveObj[attr[0]] = str(self.__dict__[attr[0]])
            elif isinstance(attr, basestring):
                saveObj[attr] = str(self.__dict__[attr])

        return saveObj

    def tryGetValue(self, dic, key):
        if key in dic:
            return dic[key]
        return None

    def __getitem__(self, key):
        if key not in self.__dict__:
            raise Exception('没有该属性' + key)
        return self.__dict__[key]

    def __setitem__(self, key, value):
        if key not in self.__dict__:
            return None
        self.__dict__[key] = value