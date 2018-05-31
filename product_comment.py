#!/usr/local/bin/python3
# -*- conding: utf8 -*-

from dbObject import DbObject
from tool import raiseIf


class ProductComment(DbObject):
    def getFields(self):
        return ['mark','product_code','product_id','p_comment']

    def getRuntimeProp(self):
        return []

