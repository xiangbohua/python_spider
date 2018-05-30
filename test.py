#!/usr/local/bin/python3
# -*- conding: utf8 -*-
import m_base


class Base(object):
    name = ''

    def __init__(self):
        self.name = self.getName()


    def getName(self):
        return 'B'

    def eat(self):
        print(self.name +': eat')




class A(Base):
    def getName(self):
        return 'A'




b = m_base.MBase()