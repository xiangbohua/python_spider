#!/usr/local/bin/python3
# -*- conding: utf8 -*-
import m_base
from m_grainger import Grainger

grainger = Grainger()


lastPage = grainger.db.select("select page_url from  processed_page where mark = '" + grainger.mark + "' order by id desc limit 1")

startUrl = 'http://item.grainger.cn/s/'
if len(lastPage) > 0:
    startUrl = lastPage[0][0]


grainger.saveCategoryAllProducts(startUrl)

print(startUrl)
exit(1)
