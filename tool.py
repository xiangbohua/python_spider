#!/usr/local/bin/python3
# -*- coding: UTF* -*-

import urllib.request
from bs4 import BeautifulSoup
import pymysql
import os
import gzip
import binascii
import zipfile

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




def zip_dir(file_path,zfile_path):
    '''
    function:压缩
    params:
        file_path:要压缩的件路径,可以是文件夹
        zfile_path:解压缩路径
    description:可以在python2执行
    '''
    filelist = []
    if os.path.isfile(file_path):
        filelist.append(file_path)
    else :
        for root, dirs, files in os.walk(file_path):
            for name in files:
                filelist.append(os.path.join(root, name))
                print('joined:',os.path.join(root, name),dirs)

    zf = zipfile.ZipFile(zfile_path, "w", zipfile.zlib.DEFLATED)
    for tar in filelist:
        arcname = tar[len(file_path):]
        print(arcname,tar)
        zf.write(tar,arcname)
    zf.close()
