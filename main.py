#!/usr/local/bin/python3
# -*- coding: UTF* -*-

import urllib.request

import time

from m_base import MBase
from m_grainger import Grainger
from m_vipmro import VipMro
from bs4 import BeautifulSoup
from dbtool import MySQLCommand
from product import Product
from product_sku import ProductSku

from tool import is_gz_file


g = Grainger()

g.redoErrorSaveSku()

# pro = g.getProductList('http://item.grainger.cn/s/page-1672/')
# print(pro)
# print('处理完成')
# exit()

#pro = g.saveProductAllInfo('http://item.grainger.cn/g/00335929/')

exit()

pro = g.getProductOne('http://item.grainger.cn/g/00335929/')
g.saveProduct(pro)
# g.saveImageWithInfo(pro)
# g.saveProductSku(pro)

print('处理完成')


