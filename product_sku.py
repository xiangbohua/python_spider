#!/usr/local/bin/python3
# -*- conding: utf8 -*-

from dbObject import DbObject
from tool import raiseIf


class ProductSku(DbObject):
    def getFields(self):
        return ['product_code','product_id','product_model','model_url','remark','can_replace', ['info_saved','0']]

    def getRuntimeProp(self):
        return []

