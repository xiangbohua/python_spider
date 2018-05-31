#!/usr/local/bin/python3
# -*- conding: utf8 -*-

from dbObject import DbObject
from tool import raiseIf


class ErrorProduct(DbObject):
    def getFields(self):
        return ['type','error_url','redo']

    def getRuntimeProp(self):
        return []

