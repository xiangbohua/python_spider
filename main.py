#!/usr/local/bin/python3
# -*- coding: UTF* -*-

import urllib.request
from vip_mro import VipMro
from bs4 import BeautifulSoup
from dbtool import MySQLCommand

from tool import is_gz_file



vip = VipMro()

p = vip.processOneProduct('http://www.vipmro.com/product/573468')
vip.downloadImgWithProduct(p)

print()
exit(1)

vip.saveImageWithUrl()
vip.saveAllProduct()



print('处理完成')
exit()


