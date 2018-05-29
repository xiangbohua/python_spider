#!/usr/local/bin/python3
# -*- coding: UTF* -*-

import urllib.request
from vip_mro import VipMro
from bs4 import BeautifulSoup
from dbtool import MySQLCommand

from tool import is_gz_file



vip = VipMro()


vip.redoError() #每次开启重试保存失败的商品
vip.saveAllProduct()    #开始获取新商品信息，此时会自动保存图片



print('处理完成')
exit()


