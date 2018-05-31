#!/usr/local/bin/python3
# -*- conding: utf8 -*-

from dbObject import DbObject
from tool import raiseIf


class ProductImage(DbObject):
    def getFields(self):
        return ['product_code','product_id','image_url','local_path','type',]

    def getRuntimeProp(self):
        return []

