#!/usr/local/bin/python3
# -*- conding: utf8 -*-
from dbObject import DbObject


class ProductSpec(DbObject):
    def getFields(self):
        return ['product_id', 'product_code', 'spec_name', 'spec_value']

    def getRuntimeProp(self):
        return []
