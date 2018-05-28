#!/usr/local/bin/python3
# -*- coding: UTF* -*-

import urllib.request
from vip_mro import VipMro
from bs4 import BeautifulSoup


vip = VipMro()
vip.saveCategory()

print(vip.category4[0])


exit()


