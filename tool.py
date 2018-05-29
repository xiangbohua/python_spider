#!/usr/local/bin/python3
# -*- coding: UTF* -*-

import urllib.request
from bs4 import BeautifulSoup
import pymysql
import os

def getHtmlAsSoup(url):
    request = urllib.request.Request(url)
    response = urllib.request.urlopen(request)
    html = response.read()
    html = html.decode("utf-8")
    soup = BeautifulSoup(html, 'html.parser')
    return soup

def mkDir(fullPath):
    if not os.path.exists(fullPath):
        os.mkdir(fullPath)

def downloadImg(imageUrl, savePath):
    print(imageUrl)

    url = 'http://www.someserver.com/cgi-bin/register.cgi'
    user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'
    values = {'name': 'Michael Foord',
              'location': 'Northampton',
              'language': 'Python'}
    headers = {'User-Agent': user_agent}

    req = urllib.request.Request(url, {}, headers)

    f = open(savePath, 'wb')
    f.write(img_url.content)
    f.close()
    exit()