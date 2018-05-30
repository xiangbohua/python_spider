#!/usr/local/bin/python3
# -*- coding: UTF* -*-

import urllib.request

import time

from m_grainger import Grainer
from m_vipmro import VipMro
from bs4 import BeautifulSoup
from dbtool import MySQLCommand

from tool import is_gz_file



vip = VipMro()


vip.reSaveMainImage()



print('处理完成')


