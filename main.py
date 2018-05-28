#!/usr/local/bin/python3
# -*- coding: UTF* -*-

import urllib.request
from vip_mro import VipMro
from bs4 import BeautifulSoup
from dbtool import MySQLCommand

host = '127.0.0.1'
port = 8889
password = 'root1'
user = 'root'

db = MySQLCommand(host, port,user, password, 'python')
db.connectMysql()
db.insertMysql('category', [{'c_name':'test', 'c_url':'test'},{'c_name':'test', 'c_url':'test'}])
#db.insertMysql('category', {'c_name':'test', 'c_url':'test'})
print(db)

exit()


