#!/usr/local/bin/python3
# -*- coding: UTF* -*-
import time
from tool import getHtmlAsSoup
import re
import string
from dbtool import MySQLCommand

class VipMro(object):
    #保存分类信息
    category1 = []
    category2 = []
    category3 = []
    category4 = []

    def __init__(self):
        self.url = 'http://www.vipmro.com'
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
            self.category2 += cate2

            for c2 in self.category2:
                cate3 = self.getCate3(cateIndex, c2['subCateId'])
                self.__saveC3(cate3, c2['name'])

                self.category3 += cate3
                for c3 in self.category3:
                    cate4 = self.getCate4(c3['name'], c3['url'])

                    self.__saveC4(cate4, c3['name'])
                    self.category4 += cate4




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

        if len(nextPage) != 0:
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
        print(categoryPath)
        exit(1)

        productId = productUrl[productUrl.find('product/') + 8:]
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

        imageInfo = {'product_id': productId, 'product_name':productName, 'imgs':imgUrls}

        productInfo = {'id':productId, 'code':productCode, 'url':productUrl,  'name':productName, 'price':price, 'model':model, 'buyCode':buyNo, 'brandname':brandName, 'brandimg':brandImg, 'brandurl':brandUrl, 'spec':specInfo, 'detail':imageInfo}
        return productInfo

    def __saveC1(self):
        db = self.__getDb()
        db.connectMysql()
        try:
            for c1 in self.category1:
                db.insertMysql('category',
                               {'c_name': c1['name'], 'c_url': c1['url'], 'c_index': c1['cateIndex'], 'lavel': 1,
                                'parent_name': ''})
        except:
            raise
        finally:
            db.closeMysql()

    def __saveC2(self,cate2, parentName):
        db = self.__getDb()
        db.connectMysql()
        try:
            for c2 in cate2:
                db.insertMysql('category',
                               {'c_name': c2['name'], 'c_url': c2['url'], 'c_index': c2['subCateId'], 'lavel': 2,
                                'parent_name': parentName})
        except:
            raise
        finally:
            db.closeMysql()


    def __saveC3(self, cate3, parentName):
        db = self.__getDb()
        db.connectMysql()
        try:
            for c3 in cate3:
                db.insertMysql('category',
                               {'c_name': c3['name'], 'c_url': c3['url'], 'c_index': 0, 'lavel': 3,
                                'parent_name': parentName})
        except:
            raise
        finally:
            db.closeMysql()

    def __saveC4(self, cate4, parentName):
        db = self.__getDb()
        db.connectMysql()
        try:
            for c4 in cate4:
                db.insertMysql('category',
                               {'c_name': c4['name'], 'c_url': c4['url'], 'c_index': '', 'lavel': 4,
                                'parent_name': parentName})
        except:
            raise
        finally:
            db.closeMysql()


    def __getDb(self):
        host = '127.0.0.1'
        port = 8889
        password = 'root1'
        user = 'root'
        return MySQLCommand(host,port,user,password,'python')
