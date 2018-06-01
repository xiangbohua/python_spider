#!/usr/local/bin/python3
# -*- coding: UTF* -*-

import urllib.request
from bs4 import BeautifulSoup
import pymysql
import os
import gzip
import binascii

from my_exceptions import LogicException


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
    from urllib.request import urlretrieve
    #文件不存在时访问图片下载
    if not os.path.exists(savePath):
        urlretrieve(imageUrl, savePath)
        #当文件是GZIP文件时才尝试解压
        if is_gz_file(savePath):
            zipData = read_gz_file(savePath)
            f = open(savePath, 'wb')  # 若是'wb'就表示写二进制文件
            f.write(zipData)
            f.close()

def read_gz_file(path):
    '''read the existing gzip-format file,and return the content of this file'''
    if os.path.exists(path):
        #the function open(filename, mode = 'rb'),so the mode argument is default is 'rb'
        with gzip.open(path, 'rb') as pf:
            return pf.read()
    else:
        print(path + '文件不存在')

def is_gz_file(filepath):
    with open(filepath, 'rb') as test_f:
        return binascii.hexlify(test_f.read(2)) == b'1f8b'


def raiseIf(checkCandition, msg = '逻辑校验失败'):
    if checkCandition:
        raise LogicException(msg)