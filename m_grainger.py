#!/usr/local/bin/python3
# -*- conding: utf8 -*-
import configparser
import os
import re

import bs4
from pip._vendor.pyparsing import basestring

from m_base import MBase
from product import Product
from product_image import ProductImage
from product_sku import ProductSku
from product_sprc import ProductSpec
from tool import mkDir, raiseIf
from tool import getHtmlAsSoup

class Grainger(MBase):
    def getMark(self):
        return 'grainger'

    def getRootUrl(self):
        return 'https://www.grainger.cn/'

    def getProductOne(self, url):
        raiseIf(url.replace('item.grainger.cn', '').find('g') <= 0, '传入的URL不属于SPU')

        soup = getHtmlAsSoup(url)

        productId = url.split('/')[-2:-1][0]

        productName = soup.find('div', id='product-intro').find('h1').string
        productCode = productId

        categoryPathTag = soup.find('div', class_='node_path').find_all('a')[1:]
        categoryPath = ''
        for cpt in categoryPathTag:
            categoryPath += cpt.string.strip() + '>'

        categoryPath += productName


        # 获取直属分类名称
        categoryName = categoryPath.split('>')
        categoryName = categoryName[-2:-1][0]

        productInrtoTag = soup.find('div', id='product-intro').find('ul', id='summary').find_all('li')


        price = ''
        unit_name = ''
        markedPrice = ''
        buyNo = ''
        brandName = ''
        brandUrl = ''
        brandImg = ''
        model = '分SKU'

        for mainInfo in productInrtoTag:
            if mainInfo.find('div').string == '价　　格：':
                price = mainInfo.find('strong', class_='p-price').string[1:]

            if mainInfo.find('div').string == '品　　牌：':
                brandName = mainInfo.find('a').string
                if hasattr(mainInfo.find('a'), 'href'):
                    brandUrl = "http://item.grainger.cn/" + mainInfo.find('a')['href'][1:]


        productDetailTag = soup.find(id='content_product')

        descriptionTag = productDetailTag.find('div', class_='property')

        description = str(descriptionTag).replace('<br/>', '')

        specTag = soup.find('ul', class_='specifications')
        specInfo = []
        if specTag != None:
            for div in specTag.find_all('div'):
                specPair = div.string.split('：')
                if len(specPair) == 2:
                    dbSpec = ProductSpec(
                        {'product_code': productCode, 'product_id': productId, 'spec_name': str(specPair[0]).strip(),
                         'spec_value': str(specPair[1]).strip()})
                    specInfo.append(dbSpec)


        #保存主图
        mainImage = []
        mainImageTags = soup.find('ul', class_='lh imageThumb')
        if mainImageTags != None:
            for mtag in mainImageTags.find_all('a'):
                mainUrl = mtag['rel'][4][1:][:-2]
                dbImage = ProductImage({'product_code': productCode, 'product_id': productId, 'image_url': mainUrl, 'type': '2'})
                mainImage.append(dbImage)

        #保存详情图
        imageInfo = []
        detailImageTags = productDetailTag.find('div', class_='group-picture')
        if detailImageTags != None:
            for imageTag in detailImageTags.find_all('img'):
                imageUrl = imageTag['data-original']
                dbImage = ProductImage({'product_code':productCode,'product_id':productId,'image_url':imageUrl, 'type':'1'})
                imageInfo.append(dbImage)

        #获取SKU信息
        skuInfos = []
        skuTags = soup.find(id='pd_table').tbody

        if skuTags != None:
            for skuTr in skuTags.find_all('tr'):
                skuTag = skuTr.find('a', target='_blank')
                skuUrl = 'http://'+skuTag['href'][2:]

                skuModel = skuTag.string
                stopSaleTag = skuTr.find('span', class_='iconOutOfOrder')
                stopSale = ''
                if stopSaleTag != None:
                    stopSale = '停止销售'

                alternativeProductUrl = ''
                alternativeTag = skuTr.find('td', class_='alternative')
                if alternativeTag != None and alternativeTag.a != None:
                    alternativeProductUrl = alternativeTag.a['href'][2:]

                dbProductSku = ProductSku({'product_code':productCode,'product_id':productId,'product_model':skuModel, 'model_url':skuUrl,'remark': stopSale, 'can_replace':alternativeProductUrl,'info_saved': '0'})
                skuInfos.append(dbProductSku)

        dbProduct = Product({'category_path':categoryPath,
                             'product_id':productId,
                             'product_code':productCode,
                             'product_url': url,
                             'product_name':productName,
                             'price':price,
                             'model':model,
                             'description':description,
                             'buy_code':buyNo,
                             'brand_name':brandName,
                             'brand_img':brandImg,
                             'brand_url':brandUrl,
                             'unit_name':unit_name,
                             'market_price':markedPrice,
                             'image_saved':'0',
                             'product_type':'SPU',
                             'category_name': categoryName,

                             'main_img':mainImage,
                             'detail_img':imageInfo,
                             'specs':specInfo,
                             'skus':skuInfos,
                             'comments': []})


        return dbProduct

    def getSkuOne(self, skuUrl):
        raiseIf(skuUrl.replace('item.grainger.cn', '').find('u') <= 0, '传入的URL不属于SKU')

        soup = getHtmlAsSoup(skuUrl)
        categoryPathTag = soup.find('div', class_='node_path').find_all('a')
        categoryPath = ''
        for cpt in categoryPathTag[1:]:
            categoryPath += cpt.string.strip() + '>'

        categoryPath = categoryPath[:-1]

        productId = skuUrl.split('/')[-2:-1][0]
        # 获取直属分类名称
        categoryName = categoryPath.split('>')
        categoryName = categoryName[-2:-1][0]

        productName = soup.find('div', id='product-intro').find('h1').string
        productCode = productId

        productInrtoTag = soup.find('div', id='product-intro').find('div', class_='line').find_all('dl')
        price = ''
        unit_name = ''
        markedPrice = ''
        buyNo = ''
        brandName = ''
        brandUrl = ''
        brandImg = ''
        model = ''

        for mainInfo in productInrtoTag:
            if mainInfo.find('dt').string == '价　　格':
                price = mainInfo.find('span', class_='p-price').contents[0][1:]
                unit_name = mainInfo.find('span', class_='p-price').contents[1].string[1:]

            if mainInfo.find('dt').string == '面　　价':
                markedPrice = mainInfo.find('dd', class_='p-price-del').string[1:]

            if mainInfo.find('dt').string == '订 货 号':
                buyNo = mainInfo.find('span').string

            if mainInfo.find('dt').string == '品　　牌':
                brandName = mainInfo.find('a').string
                brandUrl = "http:" + mainInfo.find('a')['href'][1:]

            if mainInfo.find('dt').string == '制造商型号':
                model = mainInfo.find('dd').string

        productDetailTag = soup.find(id='content_product')
        descriptionTag = productDetailTag.find('div', class_='property')
        description = str(descriptionTag).replace('<br/>', '')

        specTag = soup.find('ul', class_='specifications')
        specInfo = []
        if specTag != None:
            for div in specTag.find_all('div'):
                specPair = div.string.split('：')
                if len(specPair) == 2:
                    dbSpec = ProductSpec(
                        {'product_code': productCode, 'product_id': productId, 'spec_name': str(specPair[0]).strip(),
                         'spec_value': str(specPair[1]).strip()})
                    specInfo.append(dbSpec)


        #保存主图
        mainImage = []
        mainImageTag = soup.find('div', id='spec-n1')
        if mainImageTag != None:
            mainImageTag = mainImageTag.find('a')
            dbImage = ProductImage({'product_code': productCode, 'product_id': productId, 'image_url': mainImageTag['href'], 'type': '2'})
            mainImage.append(dbImage)

        # 保存详情图
        imageInfo = []
        detailImageTags = productDetailTag.find('div', class_='group-picture')
        if detailImageTags != None:
            for imageTag in detailImageTags.find_all('img'):
                url = imageTag['data-original']
                dbImage = ProductImage(
                    {'product_code': productCode, 'product_id': productId, 'image_url': url, 'type': '1'})
                imageInfo.append(dbImage)

        dbSkuProduct = Product({'mark':self.mark,
                             'category_path': categoryPath,
                             'product_id': productId,
                             'product_code': productCode,
                             'product_url': skuUrl,
                             'product_name': productName,
                             'price': price,
                             'model': model,
                             'description': description,
                             'buy_code': buyNo,
                             'brand_name': brandName,
                             'brand_img': brandImg,
                             'brand_url': brandUrl,
                             'unit_name': unit_name,
                             'market_price': markedPrice,
                             'image_saved': '0',
                             'product_type': 'SKU',
                             'category_name': categoryName,

                             'main_img': mainImage,
                             'detail_img': imageInfo,
                             'specs': specInfo,
                             'skus': [],
                             'comments': []})

        return dbSkuProduct

    def getProductList(self, pageUrl):
        product_list_page = getHtmlAsSoup(pageUrl)
        # 尝试获取下一页url
        nextPage = product_list_page.find('a', class_='page_curl_btn', text='下一页')

        if nextPage != None and hasattr(nextPage, 'href'):
            nextPage = 'http://item.grainger.cn/' + nextPage['href']
        else:
            nextPage = None

        # 获取商品tag
        productTags = product_list_page.find_all('div',  class_='product_grid_image img')
        urls = []
        for div in productTags:
            urlOne = div.a['href']
            urls.append('http://item.grainger.cn' + urlOne)

        return {'urls': urls, 'next': nextPage}


    def zipStartWith(self):
        return ''