#!/usr/local/bin/python3
# -*- coding: UTF* -*-

import urllib.request
from vip_mro import VipMro
from bs4 import BeautifulSoup


vip = VipMro()
mainCates = vip.saveCategory()
print(vip.category3)
exit(1)


