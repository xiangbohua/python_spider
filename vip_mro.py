#!/usr/local/bin/python3
# -*- coding: UTF* -*-
import time
from tool import getHtmlAsSoup
from tool import mkDir
from tool import downloadImg
import re
import string
from dbtool import MySQLCommand
import configparser
import os
import sys

class VipMro(object):
    mainPage = None
    #保存分类信息
    def __init__(self):
        self.url = 'http://www.vipmro.com'
        self.conf = configparser.ConfigParser()
        if not os.path.exists('conf.ini'):
            raise FileNotFoundError
        self.conf.read('conf.ini')

        self.base_path = self.getConfig('db_image_path')
        mkDir(self.base_path)

    def getMainPage(self):
        self.mainPage = getHtmlAsSoup(self.url)

    def fullUrl(self, subUrl):
        return self.url + subUrl

    def saveAllCate(self):
        self.category1 = self.getCate1()
        self.__saveC1()
        for c1 in self.category1:
            cateIndex = c1['cateIndex']

            cate2 = self.getCate2(cateIndex)
            self.__saveC2(cate2, c1['name'])

            for c2 in cate2:
                cate3 = self.getCate3(cateIndex, c2['subCateId'])
                self.__saveC3(cate3, c2['name'])

                for c3 in cate3:
                    cate4 = self.getCate4(c3['name'], c3['url'])
                    self.__saveC4(cate4, c3['name'])

    def saveAllProduct(self):
        db = self.__getDb(True)
        cate4 = db.select('select id, c_url from category where level =4 and processed = 0')
        for categoryUrl in cate4:
            url = categoryUrl[1]
            id = categoryUrl[0]

            next = url

            try:
                while next != None:
                    productList = self.getProductList(next)
                    next = productList['next']
                    urls = productList['urls']

                    for pUrl in urls:
                        fUrl = self.fullUrl(pUrl)
                        try:
                            productInfo = self.processOneProduct(fUrl)
                            self.saveProduct(productInfo)
                        except:
                            newDb = self.__getDb(True)
                            newDb.insert('error_product', {'type': '保存商品', 'error_url':fUrl})

                db = self.__getDb(True)
                db.update('category', "id = " + str(id), {'processed':1})

            except:
                db = self.__getDb(True)
                db.update('category', "id = " + str(id), {'processed': 2})

    #获取所有一级分类
    def getCate1(self):
        soup = self.mainPage
        mainCate = soup.find_all('li', attrs={'attr-type': '2'})
        cate1 = []
        for c in mainCate:
            #c = '<a attr-id="80" href=""><img href="http://www.vipmro.com/s/c-50" attr-id="50"/> 搬运、存储、包材</a>'
            cateIndex = c.a['attr-id'] #[1:0]
            mCateName = c.a.contents[2].strip() #搬运、存储、包材
            url = "/s/c-" + str(cateIndex)

            cate1.append({'name': mCateName, 'url':url,'cateIndex':cateIndex})
        return cate1

    # 获取所有二级分类
    def getCate2(self, cateIndex):
        sub1Cat = self.mainPage.find('div', class_='J_cateBox_'+str(cateIndex)).find_all('a', href=re.compile("/s/c-+"+str(cateIndex) + "\d\d$"))
        cate2 = []
        for sub2 in sub1Cat:
            subCateId = sub2['href'][-2:]
            url2 = self.fullUrl(sub2['href'])
            name2 = sub2.string
            cate2.append({'name':name2, 'url':url2, 'subCateId':subCateId})
        return cate2

    # 获取所有三级分类
    def getCate3(self, cateIndex, subCateId):
        sub2Cat = self.mainPage.find('div', class_='J_cateBox_' + str(cateIndex)).find_all('a', href=re.compile(
            "/s/c-+" + str(cateIndex) + str(subCateId) + "\d\d$"))
        cate3 = []
        for sub3 in sub2Cat:
            url3 = self.fullUrl(sub3['href'])
            name3 = sub3.string

            cate3.append({ 'name': name3, 'url': url3})
        return cate3

    # 获取所有四级分类
    def getCate4(self, name3, url3):
        soupCate4 = getHtmlAsSoup(url3)
        cateLi4 = soupCate4.find_all('a', href=re.compile(url3[-11:] + "\d\d$"))
        cate4 = []
        if len(cateLi4) > 0:
            for ct4 in cateLi4:
                name4 = ct4.string
                url4 = self.fullUrl(ct4['href'])

                cate4.append({'name': name4, 'url': url4})
                # print(mCateName+"|"+ mainUrl+"|"+name2+"|"+url2+"|"+name3+"|"+url3+"|"+name4+"|"+url4)
        else:
            cate4.append({'name': name3, 'url': url3, })
            # print(mCateName + "|" + mainUrl + "|" + name2 + "|" + url2 + "|" + name3 + "|" + url3 )
        return cate4

    #传入第4级分类，然后获取当前分页所有的商品url，并且返回下一页的url，如果没有下一页则返回None
    def getProductList(self, pageUrl):
        product_list_page = getHtmlAsSoup(pageUrl)
        #尝试获取下一页url
        nextPage = product_list_page.find('div', class_='m-pagination').find('a', text='下一页')

        if nextPage != None and len(nextPage) != 0:
            nextPage = self.fullUrl(nextPage['href'])
        else:
            nextPage = None

        #获取商品tag
        productTags = product_list_page.find_all('a', class_='pic', href=re.compile('^/product/\d+$'))

        urls = []
        for a in productTags:
            urls.append(a['href'])

        return {'urls':urls, 'next':nextPage}

    #传入商品Url获取商品详细信息
    def processOneProduct(self, productUrl):
        detailSoup = getHtmlAsSoup(productUrl)
        categoryPathTag = detailSoup.find('div', class_='g-wrapper brand-menu-text')
        categoryPath = ''
        for cpt in categoryPathTag:
            categoryPath += cpt.string.strip()

        productId = productUrl[productUrl.find('product/') + 8:]

        #获取直属分类名称
        categoryName = categoryPath.split('>')
        categoryName = categoryName[-2:-1][0]

        #品名
        productName = detailSoup.find('h1', class_='detail-goods-right-head ft22').string.strip()
        productCode = detailSoup.find('font', class_='J_goodNo').string.strip()

        #价格
        price = detailSoup.find('label', class_='ft24 a weight J_salePrice').text[1:]
        #订货号
        buyNo = detailSoup.find('label', class_='J_buyNo d').string.strip()
        #型号
        model = detailSoup.find('label', class_='J_model d').string.strip()

        brandInfo = detailSoup.find('div', class_='detail-goods-brand')

        brandName = brandInfo.find('a').find('img')['title']
        brandImg = brandInfo.find('a').find('img')['src']
        brandUrl = brandInfo.find('a')['href']

        #保存
        specTag = detailSoup.find('table', class_='detail-attrs-right-attrs fl J_attrs').find_all('tr')
        specInfo = []
        for tr in specTag:
            tr = tr.find_all('td')

            if len(tr[0].text.strip()) > 0:
                specInfo.append({'key':tr[0].text.strip(), 'value':tr[1].text.strip()})
            if len(tr[2].text.strip()) > 0:
                specInfo.append({'key':tr[2].text.strip(), 'value':tr[3].text.strip()})

        imgTags = detailSoup.find('div', class_='detail-attrs-right-body J_body').find_all('img')

        imgUrls = []
        for imgtag in imgTags:
            imgUrls.append(imgtag['src'])

        smallImgUrls = []
        smallImgTag = detailSoup.find('div', class_='detail-goods-left-do-box').find_all('img')
        for smImgTg in smallImgTag:
            smallImgUrls.append(smImgTg['src'])

        imageInfo = imgUrls

        productInfo = {'id':productId,'categoryPath':categoryPath, 'code':productCode, 'url':productUrl,  'name':productName, 'price':price, 'model':model, 'buyCode':buyNo, 'brandname':brandName, 'brandimg':brandImg, 'brandurl':brandUrl, 'spec':specInfo, 'detail':imageInfo, 'small_img':smallImgUrls, 'category_name':categoryName}
        return productInfo

    #保存一条商品数据到数据，立即提交事务版本
    def saveProduct(self, productInfo):
        productData = {'category_path': productInfo['categoryPath'], 'product_id':productInfo['id'], 'product_code':productInfo['code'], 'product_url':productInfo['url'], 'product_name':productInfo['name'], 'price':productInfo['price'], 'model':productInfo['model'], 'buy_code':productInfo['buyCode'], 'brand_name':productInfo['brandname'], 'brand_img':productInfo['brandimg'], 'brand_url':productInfo['brandurl'], 'category_name': productInfo['category_name']}

        db = self.__getDb(True)
        checkExited = db.count("product", "product_code = '" + productInfo['code'] +"'")
        if checkExited > 0 :
            print('已经存在无需保存:' + productInfo['code'])
            return

        imageData = []
        for img in productInfo['detail']:
            imageData.append({'product_code':productInfo['code'], 'product_id':productInfo['id'],'image_url':img,'type':'1'})

        for img in productInfo['small_img']:
            imageData.append({'product_code':productInfo['code'], 'product_id':productInfo['id'],'image_url':img,'type':'2'})


        specData = []
        for spec in productInfo['spec']:
            specData.append({'product_code':productInfo['code'], 'product_id':productInfo['id'],'spec_name':spec['key'], 'spec_value':spec['value']})

        db.begin()
        try:
            db.insert('product', productData)
            if len(imageData) > 0:
                db.insert('product_images', imageData)
            if len(specData) > 0:
                db.insert('product_spec', specData)
            db.commit()
            print('成功保存数据:' + productInfo['code'])
        except BaseException:
            db.rollback()
            print('插入数据失败，已回滚')
            raise


    def downloadImgWithProduct(self, productInfo):
        categoryPath = productInfo['categoryPath'].split('>')
        categoryPath = categoryPath[1:len(categoryPath) - 1]
        nextUrl = self.base_path
        for pathName in categoryPath:
            nextUrl += pathName + '/'
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



    def redoError(self):
        db = self.__getDb(True)
        errors = db.select("select *from error_product where type = '保存商品' and redo = 0")
        for err in errors:
            url = err[2]
            id = err[0]
            product = self.processOneProduct(url)
            self.saveProduct(product)
            db.update('error_product', 'id = ' + str(id), {'redo':'1'})

    #保存一级分类
    def __saveC1(self):
        db = self.__getDb()
        db.connect()
        try:
            for c1 in self.category1:
                db.insertMysql('category',
                               {'c_name': c1['name'], 'c_url': c1['url'], 'c_index': c1['cateIndex'], 'level': 1,
                                'parent_name': ''})
        except:
            raise
        finally:
            db.closeMysql()

    # 保存二级分类
    def __saveC2(self,cate2, parentName):
        db = self.__getDb()
        db.connect()
        try:
            for c2 in cate2:
                db.insert('category',
                               {'c_name': c2['name'], 'c_url': c2['url'], 'c_index': c2['subCateId'], 'level': 2,
                                'parent_name': parentName})
        except:
            raise
        finally:
            db.closeMysql()

    # 保存三级分类
    def __saveC3(self, cate3, parentName):
        db = self.__getDb()
        db.connect()
        try:
            for c3 in cate3:
                db.insert('category',
                               {'c_name': c3['name'], 'c_url': c3['url'], 'c_index': 0, 'level': 3,
                                'parent_name': parentName})
        except:
            raise
        finally:
            db.closeMysql()

    # 保存四级分类
    def __saveC4(self, cate4, parentName):
        db = self.__getDb()
        db.connect()
        try:
            for c4 in cate4:
                db.insert('category',
                               {'c_name': c4['name'], 'c_url': c4['url'], 'c_index': '', 'level': 4,
                                'parent_name': parentName})
        except:
            raise
        finally:
            db.closeMysql()

    #获取数据库对象
    def __getDb(self, connect_now = False):
        host = self.getConfig('db_host')
        port = int(self.getConfig('db_port'))
        user = self.getConfig('db_user')
        password = self.getConfig('db_password')
        db_name = self.getConfig('db_name')
        db = MySQLCommand(host,port,user,password, db_name)
        if connect_now ==  True:
            db.connect()
        return db

    def saveImageWithUrl(self):
        db = self.__getDb(True)
        rows = db.select('select id, product_url from product where image_saved = 0 ')
        for row in rows:
            url = row[1]
            id = row[0]
            try:
                product = self.processOneProduct(url)
                self.downloadImgWithProduct(product)
                db.update('product', ' id = ' + str(id), {'image_saved': 1})
                print('图片已保存' + product['code'])
            except:
                db.update('product', ' id = ' + str(id), {'image_saved': 2})
                print('图片保存失败' + url)


    def getShortName(self, fullPath):
        shortName = fullPath[::-1]
        shortName = shortName[:shortName.find('/')][::-1]
        return shortName

    def getConfig(self, key):
        con = self.conf.get('config', key)
        return con

    def test(self):
        db = self.__getDb(True)
        row = db.select('select id,category_path from product')
        for r in row:
            id = r[0]
            category_name = r[1].split('>')
            category_name = category_name[-2:-1][0]
            db.update('product', 'id=' +str(id), {'category_name':category_name})


