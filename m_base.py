#!/usr/local/bin/python3
# -*- conding: utf8 -*-

import configparser
import os
import abc

import time

import tool
from dbObject import DbObject
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
    def getProductOne(self, url):
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

    def getSkuOne(self, skuUrl):
        return None

    #保存所有分类
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

    #保存多有商品
    def saveAllProduct(self):
        categories = self.db.select("select id, categoru_url from category + where processed = 0 and level = 4 and mark = '" + self.mark + "'")

        for cate in categories:

            id = cate[0]
            cateUrl = cate[1]

            try:
                self.saveCategoryAllProducts(cateUrl);

                self.db.update('category', "id = " + str(id), {'processed': 1})
            except:
                self.db.update('category', "id = " + str(id), {'processed': 2})


    #获取当前所有分类商品
    def saveCategoryAllProducts(self, listUrl):
        nextUrl = listUrl
        while nextUrl != None:
            productList = self.getProductList(nextUrl)
            nextUrl = productList['next']
            urls = productList['urls']
            for shortUrl in urls:
                #默认获取完成Url
                fullUrl = shortUrl
                checkExited = self.checkProductWithUrl(fullUrl)
                if not checkExited:
                    productInfo = self.getProductOne(fullUrl)
                    self.saveProductAllInfo(productInfo)
                else:
                    print('已经存在无需保存:' + fullUrl)

        #重新尝试保存失败的SPU
        self.redoErrorProduct()
        #重新尝试保存保存信息失败的SKU
        self.redoErrorSaveSku()

    #保存商品所有的信息
    def saveProductAllInfo(self, productInfo):
        try:
            self.saveProduct(productInfo, False)
            self.saveImageWithInfo(productInfo)
            self.saveProductSku(productInfo)
        except Exception as ex:
            print('保存商品信息失败')
            existed = self.db.count('error_product', "mark = '" +self.mark +"' and error_url = '" + productInfo.product_url +"'")
            if existed  == 0:
                self.db.insert('error_product', {'mark': self.mark, 'type': '保存商品', 'error_url': productInfo.product_url})

    #保存单个商品的所有SKU信息，要求商品信息已经保存
    def saveProductSku(self, productInfo):
        if productInfo.skus != None and len(productInfo.skus):
            for sku in productInfo.skus:
                fullUrl = sku.model_url

                skuInfo = self.getSkuOne(fullUrl)
                if skuInfo != None:
                    try:
                        print(skuInfo.saveableObj())
                        self.saveProduct(skuInfo, True)

                        self.saveImageWithInfo(skuInfo)
                        print('保存SKU成功，SPU编码：'+ productInfo.product_code + " SKU编码:" + skuInfo.product_code)
                        self.db.update('product_sku', "product_code = '" + productInfo.product_code + "' and model_url = '" +sku.model_url + "'", {'info_saved': '1'})

                    except Exception as e:
                        print('商品SKU保存失败:' + sku.model_url + ":" + str(e))
                else:
                    print('保存商品SKU失败：未能获取到SKU对象'+ fullUrl)

    #保存分类信息
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

    #保存单个商品基础信息
    def saveProduct(self, productInfo, checkExisted = True):
        raiseIf(not isinstance(productInfo, DbObject))
        productInfo.mark = self.mark
        db = self.getDb()
        if checkExisted:
            checkExited = self.checkProductWithCode(productInfo.product_code)
            if checkExited > 0:
                print('已经存在无需保存:' + productInfo.product_code)
                return

        def setMark(x):
            x.mark = self.mark
            return x

        imageData = self.createSaveObject(map(setMark,productInfo.main_img + productInfo.detail_img))

        db.begin()
        try:
            self.saveData(db, 'product', productInfo.saveableObj())
            self.saveData(db, 'product_images', imageData)
            self.saveData(db, 'product_spec', self.createSaveObject(productInfo.specs))
            self.saveData(db, 'product_sku', self.createSaveObject(map(setMark, productInfo.skus)))
            self.saveData(db, 'product_comment', self.createSaveObject(productInfo.comments))

            db.commit()
            print('成功保存商品数据:' + productInfo.product_code)
        except BaseException:
            db.rollback()
            print('保存商品数据失败，已回滚')
            raise


    #加载配置文件
    def __loadConfig(self, fileName = 'conf.ini'):
        self.conf = configparser.ConfigParser()
        if not os.path.exists(fileName):
            raise FileNotFoundError
        self.conf.read(fileName)


    #准备相关信息
    def __prepareAll(self):
        self.url = self.getRootUrl()
        self.mark = self.getMark()

        self.__prepareBasePath()

    #检查相关信息，失败时报错
    def __checkAll(self):
        raiseIf(self.mark == None)
        raiseIf(self.url == None)
        raiseIf(self.conf == None)
        raiseIf(self.base_path == None)
        raiseIf(not os.path.exists(self.base_path))

    #获取配置属性
    def getConfig(self, key):
        con = self.conf.get('config', key)
        if con == '' or con == None:
            raise ValueError('配置未找到' + str(key))
        return con

    #保存文件存储基础目录
    def __prepareBasePath(self):
        basePath = self.getConfig('db_image_path')

        if basePath[-1:] != '/':
            basePath += '/'
        self.base_path = basePath + self.mark + '/'
        mkDir(basePath)
        mkDir(self.base_path)

    #加载主界面
    def loadMainPage(self):
        self.mainPage = tool.getHtmlAsSoup(self.url)

    #获取新的数据库访问对象
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

    #根据商品Url检查商品是否存在
    def checkProductWithUrl(self, url):
        count = self.db.count('product', "product_url = '" + url + "' and mark = '" + self.mark + "'")
        return count > 0

    #传入商品编码检查商品是否存在
    def checkProductWithCode(self, code):
        count = self.db.count('product', "product_code = '" + code + "' and mark = '" + self.mark + "'")
        return count > 0

    #传入分类Url检测分类是否存在
    def checkCategoryWithUrl(self, categoryUrl):
        count = self.db.count('category', "c_url = '" + categoryUrl + "' and mark = '" + self.mark + "'")
        return count > 0

    #根据从页面获取的商品信息保存其图片
    def saveImageWithInfo(self, productInfo, db = None):
        if db == None:
            db = self.getDb()
        else:
            raiseIf(not isinstance(db, MySQLCommand))

        start = time.time()
        try:
            nextUrl = self.createImagePathTree(productInfo.category_path) + productInfo.product_code

            mkDir(nextUrl)

            if len(productInfo.main_img) > 0:
                mainPath = nextUrl + '/主图/'
                mkDir(mainPath)
                for dbImage in productInfo.main_img:
                    imageUrl = dbImage.image_url
                    imagePath = mainPath + self.getShortName(imageUrl)
                    downloadImg(imageUrl, imagePath)

            if len(productInfo.detail_img) > 0:
                detailPath = nextUrl + '/详情图/'
                mkDir(detailPath)
                for dbImage in productInfo.main_img:
                    imageUrl = dbImage.image_url
                    imagePath = detailPath + self.getShortName(imageUrl)
                    downloadImg(imageUrl, imagePath)

            db.update('product', "mark = '" + self.mark+"' and product_code = '" + str(productInfo.product_code) + "'", {'image_saved': '1'})
            print('保存图片成功：' + productInfo.product_code)
        except Exception as ex:
            print('保存商品图片失败' + str(ex))
            endTime = time.time()
            span = endTime - start
            save_status = '2'
            if span > 5:
                save_status = '3'
            db.update('product', "mark = '" + self.mark + "' and product_code = '" + str(productInfo.product_code) + "'", {'image_saved': str(save_status)})
            print('保存图片失败,' + '耗时' + str(int(span)) + 's， 已标记为' + save_status + ' ' + productInfo.product_code)

    #传入商品Url，保存商品图片
    def saveImageWithUrl(self, productUrl):
        product = self.getProductOne(productUrl)
        self.saveImageWithInfo(product)

    #按商品分类保存
    def createImagePathTree(self, categoryPath):
        nextUrl = self.base_path
        categoryPath = categoryPath.split('>')[:-1]
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

    def getFullUrl(self, shortUrl):
        return self.url + shortUrl

    #保存DbObject格式的对象到数据库
    def saveData(self, db, tableName, data):
        if len(data) > 0:
            db.insert(tableName, data)

    #将DbObject的数组转换成可保存的数组
    def createSaveObject(self, dbObjectList):
        return [x.saveableObj() for x in dbObjectList if isinstance(x, DbObject)]

    #获取文件短名称
    def getShortName(self, fullPath):
        shortName = fullPath[::-1]
        shortName = shortName[:shortName.find('/')][::-1]
        return shortName

    def redoErrorProduct(self):
        errorProductUrls =  self.db.select("select id,error_url from error_product where type = '保存商品' and redo=0 and mark = '" + self.mark +"'" )
        for urlDb in errorProductUrls:
            id = urlDb[0]
            url = urlDb[1]
            try:
                self.saveProductAllInfo(url)
                updateStatus = 1
            except Exception as ex:
                print('重试保存商品再次失败' + str(ex) + ":" + url)
                updateStatus = 2

            self.db.update('error_product', "id = " + str(id), {'redo':str(updateStatus)})


    def redoErrorSaveSku(self):
        errorSku = self.db.select("select id,model_url from product_sku where info_saved =0 and mark = '" + self.mark +"'" )
        for urlDb in errorSku:
            id = urlDb[0]
            url = urlDb[1]
            try:
                skuInfo = self.getSkuOne(url)
                self.saveProductAllInfo(skuInfo)
                updateStatus = 1
            except Exception as ex:
                print('重试保存SKU再次失败' + str(ex) + ":" + url)
                updateStatus = 2

            self.db.update('product_sku', "id = " + str(id), {'info_saved':str(updateStatus)})

    def redoErrorSaveImage(self):
        errorProduct = self.db.select("select id,product_code, category_path from product where image_saved =0 and mark = '" + self.mark + "'")
        for urlDb in errorProduct:
            id = urlDb[0]
            productCode = urlDb[1]
            categoryPath = urlDb[2]
            savePath = self.createImagePathTree(categoryPath) + productCode
            mkDir(savePath)

            try:
                productImages = self.db.select("select image_url,type from product_images where mark = '" + self.mark + "' and product_code = '" +productCode + "'")
                for dbImageUrl in productImages:
                    imageUrl = dbImageUrl[0]
                    type = dbImageUrl[1]
                    if type == 2:
                        mainPath = savePath + '/主图/'
                        mkDir(mainPath)
                        imagePath = mainPath + self.getShortName(imageUrl)
                        downloadImg(imageUrl, imagePath)

                    if type == 1:
                        detailPath = savePath + '/详情图/'
                        mkDir(detailPath)
                        imagePath = detailPath + self.getShortName(imageUrl)
                        downloadImg(imageUrl, imagePath)


                self.db.update('product',"mark = '" + self.mark + "' and product_code = '" + str(productCode) + "'", {'image_saved': '1'})
                updateStatus = 1
            except Exception as ex:
                print('重试保存SKU再次失败' + str(ex) + ":" + productCode)
                updateStatus = 2

            self.db.update('product_sku', "id = " + str(id), {'info_saved': str(updateStatus)})
