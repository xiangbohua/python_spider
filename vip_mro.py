#!/usr/local/bin/python3
# -*- coding: UTF* -*-
import time
from tool import getHtmlAsSoup
import re
import string

class VipMro(object):
    #保存分类信息
    category1 = []
    category2 = []
    category3 = []
    category4 = []

    def __init__(self):
        self.url = 'http://www.vipmro.com'
        self.mainPage = getHtmlAsSoup(self.url)

    #保存所有分类信息
    def saveCategory(self):
        soup = self.mainPage
        mainCate = soup.find_all('li', attrs={'attr-type': '2'})
        mainCateData = []
        for c in mainCate:
            #c = '<a attr-id="80" href=""><img href="http://www.vipmro.com/s/c-50" attr-id="50"/> 搬运、存储、包材</a>'
            cateIndex = c.a['attr-id'] #[1:0]
            mCateName = c.a.contents[2].strip() #搬运、存储、包材
            url = "http://www.vipmro.com/s/c-" + str(cateIndex)

            self.category1.append({'name1': mCateName, 'url1':url})

            self.getOneMainCate(cateIndex, mCateName, url)


    #获取二级到三级分类四级分类
    def getOneMainCate(self, cateIndex, mCateName, mainUrl):
        secCateObj = [];
        sub1Cat = self.mainPage.find('div', class_='J_cateBox_'+str(cateIndex)).find_all('a', href=re.compile("/s/c-+"+str(cateIndex) + "\d\d$"))
        for sub2 in sub1Cat:
            subCateId = sub2['href'][-2:]
            url2 = self.url + sub2['href']
            name2 = sub2.string
            self.category2.append({'name1': mCateName, 'url1':mainUrl, 'name2':name2, 'url2':url2})
            sub2Cat = self.mainPage.find('div', class_='J_cateBox_'+str(cateIndex)).find_all('a', href=re.compile("/s/c-+"+str(cateIndex) + subCateId +"\d\d$"))
            for sub3 in sub2Cat:
                url3 = self.url + sub3['href']
                name3 = sub3.string
                self.category3.append({'name1': mCateName, 'url1': mainUrl, 'name2': name2, 'url2': url2, 'name3':name3, 'url3':url3})



    def getProductList(self, pageUrl):
        return ['product1', 'product2']


    def processOneProduct(self, productUrl):
        time.sleep(1)
        print(productUrl)



