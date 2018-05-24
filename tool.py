#!/usr/local/bin/python3
# -*- coding: UTF* -*-

import urllib.request
from bs4 import BeautifulSoup
import pymysql


def getHtmlAsSoup(url):
    request = urllib.request.Request(url)
    response = urllib.request.urlopen(request)
    html = response.read()
    html = html.decode("utf-8")
    soup = BeautifulSoup(html, 'html.parser')
    return soup


