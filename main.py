#!/usr/local/bin/python3
# -*- coding: UTF* -*-

import urllib.request

import time

from m_base import MBase
from m_grainger import Grainer
from m_vipmro import VipMro
from bs4 import BeautifulSoup
from dbtool import MySQLCommand
from product import Product
from product_sku import ProductSku

from tool import is_gz_file


g = Grainer()


#pro = g.getSkuOne('http://item.grainger.cn/u/00186391/')

#exit()

pro = g.getProductOne('http://item.grainger.cn/g/00275917/')

g.saveProduct(pro)
g.saveProductSku(pro)

print('处理完成')


