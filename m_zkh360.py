#!/usr/local/bin/python3
# -*- conding:utf8-*-
import abc

from m_base import MBase


class Zkh360(MBase):

    @abc.abstractmethod
    def getRootUrl(self):
        return 'http://www.zkh360.com/'

    @abc.abstractmethod
    def getMark(self):
        return 'zkh360'

    @abc.abstractmethod
    def getProductOne(self, url):
        raise Exception('方法必须实现')