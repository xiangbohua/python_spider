#!/usr/local/bin/python3
# -*- coding: UTF* -*-
from m_grainger import Grainger

grainger = Grainger()


grainger.saveCategoryAllProducts('http://item.grainger.cn/s/')

print('处理完成')