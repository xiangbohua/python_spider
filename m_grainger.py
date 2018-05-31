#!/usr/local/bin/python3
# -*- conding: utf8 -*-
import configparser
import os

from pip._vendor.pyparsing import basestring

from m_base import MBase
from product import Product
from product_image import ProductImage
from product_sku import ProductSku
from product_sprc import ProductSpec
from tool import mkDir
from tool import getHtmlAsSoup

class Grainer(MBase):
    def getMark(self):
        return 'grainer'

    def getRootUrl(self):
        return 'https://www.grainger.cn/'

    def getProductOne(self, url):
        soup = getHtmlAsSoup(url)
        categoryPathTag = soup.find('div', class_='node_path').find_all('a')
        categoryPath = ''
        for cpt in categoryPathTag:
            categoryPath += cpt.string.strip() + '>'
        categoryPath = categoryPath[:-1]

        productId = url.split('/')[-2:-1][0]
        # 获取直属分类名称
        categoryName = categoryPath.split('>')
        categoryName = categoryName[-1:][0]

        productName = soup.find('div', id='product-intro').find('h1').string
        productCode = productId

        price = soup.find('div', id='product-intro').find_all('strong', class_='p-price')
        price = '~'.join([x.string[1:] for x in price])
        buyNo = ''
        model = '多种'

        brandTag = soup.find(id='summary-brand')
        brandName = brandTag.find('div', class_='dd').a.string
        brandUrl = brandTag.find('div', class_='dd').a['href']
        brandImg = ''


        productDetailTag = soup.find(id='content_product')

        description = productDetailTag.find('div', class_='property')
        description = ''.join([prop for prop in description.contents if isinstance(prop, basestring)])

        specTag = soup.find('ul', class_='specifications').find_all('div')
        specInfo = []
        for div in specTag:
            specPair = div.string.split('：')
            if len(specPair) == 2:
                dbSpec = ProductSpec({'product_code':productCode,'product_id':productId,'spec_name':str(specPair[0]).strip(), 'spec_value':str(specPair[1]).strip()})
                specInfo.append(dbSpec)


        #保存主图
        mainImage = []
        mainImageTags = soup.find('ul', class_='lh imageThumb').find_all('a')
        for mtag in mainImageTags:
            mainUrl = mtag['rel'][4][1:][:-2]
            dbImage = ProductImage({'product_code': productCode, 'product_id': productId, 'image_url': mainUrl, 'type': '2'})
            mainImage.append(dbImage)

        #保存详情图
        detailImageTags = productDetailTag.find('div', class_='group-picture').find_all('img')
        imageInfo = []
        for imageTag in detailImageTags:
            url = imageTag['data-original']
            dbImage = ProductImage({'product_code':productCode,'product_id':productId,'image_url':url, 'type':'1'})
            imageInfo.append(dbImage)

        #获取SKU信息
        skuInfos = []
        skuTags = soup.find(id='pd_table').find_all('a', target='_blank')
        for skuTag in skuTags:
            skuUrl = skuTag['href']
            skuModel = skuTag.string
            dbProductSku = ProductSku({'product_code':productCode,'product_id':productId,'product_model':skuModel, 'model_url':skuUrl,'info_saved': '0'})
            skuInfos.append(dbProductSku)



        dbProduct = Product({'category_path':categoryPath,
                             'product_id':productId,
                             'product_code':productCode,
                             'product_url': url,
                             'product_name':productName,
                             'price':price,
                             'model':'分SKU',
                             'description':description,
                             'buy_code':'',
                             'brand_name':brandName,
                             'brand_img':'',
                             'brand_url':brandUrl,
                             'image_saved':'0',
                             'product_type':'SPU',

                             'main_img':mainImage,
                             'detail_img':imageInfo,
                             'specs':specInfo,
                             'skus':skuTags,
                             'comments': []})

        return dbProduct