#!/usr/local/bin/python3
# -*- conding: utf8 -*-

from dbObject import DbObject

class Category(DbObject):
    def getFields(self):
        return ['mark','c_name','c_url','level','parent_name','c_index','processed']

    def getRuntimeProp(self):
        return []

