#!/usr/local/bin/python3
# -*- conding: utf8 -*-

from dbObject import DbObject
from tool import raiseIf


class Spec(DbObject):
    def getFields(self):
        return ['product_code','product_id','spec_name','spec_value']

    def getRuntimeProp(self):
        return []

