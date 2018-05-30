#!/usr/local/bin/python3
# -*- coding: UTF* -*-

import urllib.request

import time

from m_base import MBase
from m_grainger import Grainer
from m_vipmro import VipMro
from bs4 import BeautifulSoup
from dbtool import MySQLCommand

from tool import is_gz_file


m = Grainer()

m.db.count('product')

db = m.getDb()
db.connect()
print(db.count('product'))

db.closeMysql()

db.connect()
print(db.count('product'))



print('处理完成')


