#!/usr/local/bin/python3
# -*- conding: utf8 -*-

import configparser
import os
import abc

import time

import tool
from tool import downloadImg

from dbtool import MySQLCommand

from tool import mkDir, raiseIf


class MBase(object):
    __metaclass__ = abc.ABCMeta

    #首页的soup对象
    mainPage = None

    #网站首页地址
    url = None

    #配置文件对象
    conf = None

    #要抓取的网站标志
    mark = None

    #当前网页的保存跟目录
    base_path = None

    def __init__(self):
        self.__loadConfig()

        self.__prepareAll()
        self.__checkAll()

    @abc.abstractmethod
    def getRootUrl(self):
        raise Exception('方法必须实现')

    @abc.abstractmethod
    def getMark(self):
        raise Exception('方法必须实现')

    @abc.abstractmethod
    def getOneProduct(self, url):
        raise Exception('方法必须实现')

    @abc.abstractmethod
    def saveOneProduct(self, productInfo):
        raise Exception('方法必须实现')

    @abc.abstractmethod
    def getCategory1(self):
        raise Exception('方法必须实现')

    @abc.abstractmethod
    def getCategory2(self, cate1Info):
        raise Exception('方法必须实现')

    @abc.abstractmethod
    def getCategory3(self, cate2Info):
        raise Exception('方法必须实现')

    @abc.abstractmethod
    def getCategory4(self, cate3Info):
        raise Exception('方法必须实现')

    @abc.abstractmethod
    def getProductList(self, url):
        raise Exception('方法必须实现')

    @abc.abstractmethod
    def getCategoryPathList(self, categoryPathStr):
        raise Exception('方法必须实现')

    def saveAllCategory(self):
        category1 = self.getCategory1()
        for cate1 in category1:
            self.saveCategory(cate1)
            category2 = self.getCategory2(cate1)

            for cate2 in category2:
                self.saveCategory(cate2)
                category3 = self.getCategory3(cate2)

                for cate3 in category3:
                    self.saveCategory(cate3)
                    category4 = self.getCategory4(cate3)
                    for cate4 in category4:
                        self.saveCategory(cate4)


    def saveAllProduct(self):
        categories = self.db.select("select id, categoru_url from category + where processed = 0 and level = 4 and mark = '" + self.mark + "'")

        for cate in categories:

            id = cate[0]
            cateUrl = cate[1]

            try:
                self.saveOneCategoryProducts(cateUrl);

                self.db.update('category', "id = " + str(id), {'processed': 1})
            except:
                self.db.update('category', "id = " + str(id), {'processed': 2})


    #获取当前所有分类商品
    def saveOneCategoryProducts(self, listUrl):
        nextUrl = listUrl
        while nextUrl != None:
            productList = self.getProductList(nextUrl)
            nextUrl = productList['next']
            urls = productList['urls']

            for shortUrl in urls:
                fullUrl = self.getFullUrl(shortUrl)
                checkExited = self.checkProductWithCode(productInfo['code'])
                if not checkExited:
                    try:
                        productInfo = self.getOneProduct(fullUrl)
                        self.saveProduct(productInfo, False)
                    except:
                        self.db.insert('error_product', {'type': '保存商品', 'error_url': fullUrl})
                else:
                    print('已经存在无需保存:' + urls)


    def saveCategory(self, categoryInfo, db = None):
        categoryInfo.append('mark', self.mark)

        if db == None:
            db = self.db
        else:
            raiseIf(not isinstance(db, MySQLCommand))

        existed = self.checkCategoryWithUrl(categoryInfo['c_url'])
        if not existed:
            db.insert('category', categoryInfo)
        else:
            print('分类已存在' + categoryInfo['c_url'])

    def saveProduct(self, productInfo, checkExisted = True):
        raiseIf(not isinstance(productInfo, dict))
        db = self.getDb()
        if checkExisted:
            existed = self.checkProductWithCode(productInfo['code'])
            if existed:
                print('已经存在无需保存:' + productInfo['code'])
                return

        productInfo.append('mark', self.mark)
        imageData = []
        for img in productInfo['detail']:
            imageData.append(
                {'product_code': productInfo['code'], 'product_id': productInfo['id'], 'image_url': img, 'type': '1'})

        for img in productInfo['small_img']:
            imageData.append(
                {'product_code': productInfo['code'], 'product_id': productInfo['id'], 'image_url': img, 'type': '2'})

        specData = []
        for spec in productInfo['spec']:
            specData.append(
                {'product_code': productInfo['code'], 'product_id': productInfo['id'], 'spec_name': spec['key'],
                 'spec_value': spec['value']})

        commentData = []
        if 'comment' in productInfo.keys():
            for com in productInfo['comment']:
                commentData.append(
                    {'product_code': productInfo['code'], 'product_id': productInfo['id'], 'mark': self.mark,
                     'p_comment': com})

        db.begin()
        try:
            db.insert('product', productInfo)
            if len(imageData) > 0:
                db.insert('product_images', imageData)
            if len(specData) > 0:
                db.insert('product_spec', specData)
            if len(commentData) > 0:
                db.insert('product_comment', commentData)

            db.commit()
            print('成功保存数据:' + productInfo['code'])
        except BaseException:
            db.rollback()
            print('插入数据失败，已回滚')
            raise

    def __loadConfig(self, fileName = 'conf.ini'):
        self.conf = configparser.ConfigParser()
        if not os.path.exists(fileName):
            raise FileNotFoundError
        self.conf.read(fileName)


    def __prepareAll(self):
        self.url = self.getRootUrl()
        self.mark = self.getMark()

        self.__prepareBasePath()


    def __checkAll(self):
        raiseIf(self.mark == None)
        raiseIf(self.url == None)
        raiseIf(self.conf == None)
        raiseIf(self.base_path == None)
        raiseIf(not os.path.exists(self.base_path))

    def getConfig(self, key):
        con = self.conf.get('config', key)
        if con == '' or con == None:
            raise ValueError('配置未找到' + str(key))
        return con

    def __prepareBasePath(self):
        basePath = self.getConfig('db_image_path')

        if basePath[-1:] != '/':
            basePath += '/'
        self.base_path = basePath + self.mark + '/'
        mkDir(basePath)
        mkDir(self.base_path)

    def loadMainPage(self):
        self.mainPage = tool.getHtmlAsSoup(self.url)

    def getDb(self):
        host = self.getConfig('db_host')
        port = int(self.getConfig('db_port'))
        user = self.getConfig('db_user')
        password = self.getConfig('db_password')
        db_name = self.getConfig('db_name')
        db = MySQLCommand(host, port, user, password, db_name)
        db.connect()
        return db

    #定义属性
    db = property(fget=getDb, fset=None, doc='获取数据库对象')

    def checkProductWithUrl(self, url):
        count = self.db.count('product', 'product_url = ' + url + " and mark = '" + self.mark + "'")
        return count > 0

    def checkProductWithCode(self, code):
        count = self.db.count('product', 'product_code = ' + code + " and mark = '" + self.mark + "'")
        return count > 0

    def checkCategoryWithUrl(self, categoryUrl):
        count = self.db.count('category', 'c_url = ' + categoryUrl + " and mark = '" + self.mark + "'")
        return count > 0

    def saveImageWithInfo(self, productInfo, db = None):
        if db == None:
            db = self.getDb()
        else:
            raiseIf(not isinstance(db, MySQLCommand))

        start = time.time()
        try:
            categoryPath = productInfo['categoryPath'].split('>')
            categoryPath = categoryPath[1:len(categoryPath) - 1]
            nextUrl = self.base_path
            for pathName in categoryPath:
                nextUrl += pathName.replace('/', '\\') + '/'
                mkDir(nextUrl)

            mkDir(nextUrl + productInfo['code'])
            if len(productInfo['detail']) > 0:
                detailPath = nextUrl + productInfo['code'] + '/详情图/'
                mkDir(detailPath)
                for imageUrl in productInfo['detail']:
                    imagePath = detailPath + self.getShortName(imageUrl)
                    downloadImg(imageUrl, imagePath)

            if len(productInfo['small_img']) > 0:
                mainPath = nextUrl + productInfo['code'] + '/主图/'
                mkDir(mainPath)
                for imageUrl in productInfo['small_img']:
                    imagePath = mainPath + self.getShortName(imageUrl)
                    downloadImg(imageUrl, imagePath)

            db.update('product', ' product_code = ' + str(productInfo['code']), {'image_saved': 1})
            print('保存图片成功：' + productInfo['code'])
        except:
            endTime = time.time()
            span = endTime - start
            save_status = '2'
            if span > 5:
                save_status = '3'

            db.update('product', ' product_code = ' + str(productInfo['code']), {'image_saved': save_status})
            print('保存图片失败,' + '耗时' + str(int(span)) + 's， 已标记为' + save_status + ' ' + productInfo['code'])

    def saveImageWithUrl(self, productUrl):
        product = self.getOneProduct(productUrl)
        self.saveImageWithInfo(product)

    #按商品分类保存
    def createImagePathTree(self, categoryPath):
        raiseIf(not isinstance(categoryPath, list))
        nextUrl = self.base_path
        for pathName in categoryPath:
            nextUrl += pathName.replace('/', '\\') + '/'
            mkDir(nextUrl)
        return nextUrl

    #创建图片保存目录，并且返回图片的保存路径
    def getProductImageSavePath(self, productInfo, imageUrl):
        catePathList = self.getCategoryPathList(productInfo['category_path'])
        pathPrefix = self.createImagePathTree(catePathList)
        return pathPrefix + self.getShortFileName(imageUrl)


    #传入图片完整路径，返回文件名
    #传入：http://www.baidu.com/img/01.jpg
    # 返回:01.jpg
    def getShortFileName(self, fullPath):
        shortName = fullPath[::-1]
        shortName = shortName[:shortName.find('/')][::-1]
        return shortName

    def getFullUrl(self, sortUrl):
        return self.url + sortUrl


