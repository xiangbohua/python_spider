#!/usr/local/bin/python3
# -*- coding: UTF* -*-

import urllib.request
from vip_mro import VipMro
from bs4 import BeautifulSoup

request = urllib.request.Request("http://www.vipmro.com/")
response = urllib.request.urlopen(request)
html = response.read()
html = html.decode("utf-8")

soup = BeautifulSoup(html, 'html.parser')

result = soup.find_all(class_='nav-main-left J_cate_left')


exit(1)

vip = VipMro();
mainCates = vip.getMainCategory()
for mainCat in mainCates:
    subCates = vip.getSubCategory(mainCat)
    for subCate in subCates:
        productUrls = vip.getProductList(subCate)
        for product in productUrls:
            vip.processOneProduct(product)

