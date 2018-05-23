#!/usr/local/bin/python3
# -*- coding: UTF* -*-
import time
from tool import getHtmlAsSoup

class VipMro:
    def __init__(self):
        self.url = 'www.vipmro.com'

    def getMainCategory(self):
        soup = getHtmlAsSoup(self.url)
        soup.

        return ['a']

    def getSubCategory(self, mainCate):
        return ['1','2', '3']

    def getProductList(self, pageUrl):
        return ['product1', 'product2']


    def processOneProduct(self, productUrl):
        time.sleep(1)
        print(productUrl)



