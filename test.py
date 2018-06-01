#!/usr/local/bin/python3
# -*- conding: utf8 -*-
import m_base
from m_grainger import Grainger

g = Grainger()



g.saveCategoryAllProducts('http://item.grainger.cn/s/c-203905/')


print('处理完成')