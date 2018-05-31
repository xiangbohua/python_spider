#!/usr/local/bin/python3
# -*- conding: utf8 -*-

from dbObject import DbObject
from tool import raiseIf


class Product(DbObject):
    def getFields(self):
        return ['category_path','product_id','product_code','product_url','product_name','price','model','buy_code','brand_name','brand_img', 'category_name','brand_url','image_saved']

    def getRuntimeProp(self):
        return [
            'main_img',
            'detail_img',
            'specs',
            'skus',
            'comments',
        ]

