# -*- coding: utf-8 -*-
import json
import re
import uuid

import scrapy

from WeixinSougouSpider.items import HotArticleItem


class HotArticleSpider(scrapy.Spider):
    # 爬虫名称
    name = "spider_hot_article"
    # 起始链接
    start_urls = [
        'http://weixin.sogou.com/',
    ]
    # 是否关闭爬虫
    close_down = False

    # 第一层爬取后处理函数，不需要保存数据
    def parse(self, response):
        # 装载所有热文类型
        sumtoolbar = []
        # 提取直接显示的热文类型
        for result in response.css('.fieed-box ').xpath('a[re:test(@uigs,"type_pc_\d")]//text()').extract():
            sumtoolbar.append(result)

        # 提取“更多”内的热文类型
        for result2 in response.css('.fieed-box >div.tab-box-pop').xpath(
                'a[re:test(@uigs,"type_pc_\d")]//text()').extract():
            sumtoolbar.append(result2)

        # 提取热文类型下的相关内容
        for result in response.css('div.main-left > div.news-box'):
            # 提取热文类型的id
            id = result.css('::attr("id")').extract_first()
            str = re.sub(r'\D', "", id)
            # 构造爬取的链接
            base_url = "http://weixin.sogou.com/pcindex/pc/pc_?/pc_?.html"
            go_url = base_url.replace("?", str)

            # 发送新的请求到异步请求
            request = scrapy.Request(go_url, self.parseToSaveHotArticle)
            yield request

    def parseToSaveHotArticle(self, response):
        # 提取具体的热文
        resultSec = response.css("ul.news-list > li")
        # 单类型只爬取前5个热文
        for i in range(5):
            item = HotArticleItem()
            toolbarTemp = resultSec[i].css('div.txt-box >h3>a::attr("uigs")').extract_first()
            item['toolbar'] = toolbarTemp.split('_', 3)[1]
            item['title'] = resultSec[i].css('div.txt-box >h3>a::text').extract_first()
            item['introduction'] = resultSec[i].css("div.txt-box > p.txt-info::text").extract_first()
            item['from_wx_link'] = resultSec[i].css('div.txt-box >div.s-p >a::attr("href")').extract_first()
            item['date_ago'] = resultSec[i].css('div.txt-box >div.s-p >span.s2::attr("t")').extract_first()
            item['contentLink'] = resultSec[i].css('div.txt-box >h3>a::attr("href")').extract_first()
            item['wx_name'] = ''
            item['wx_nameImg'] = ''
            item['wx_imgLink'] = ''
            item['filePath_uuid'] = str(uuid.uuid1())
            from_wx_link = resultSec[i].css('div.txt-box >div.s-p >a::attr("href")').extract_first()
            contentLink = resultSec[i].css('div.txt-box >h3>a::attr("href")').extract_first()
            request = scrapy.Request(contentLink, self.parse_html)
            request.meta['item'] = item
            yield request

    def toGongzhonghaoDetail(self, response):
        tosaveItem = response.meta['item']
        url = tosaveItem['from_wx_link']
        result = response.css('div.profile_info_area').css('div.profile_info_area')
        if result is not None and result.__len__() > 0:
            temp = result.css("div.profile_info_group > div.profile_info > strong::text").extract_first()
            if temp is not None and temp is not '':
                tosaveItem['wx_name'] = result.css("strong.profile_nickname::text").extract_first().strip()
                tosaveItem['wx_imgLink'] = result.css(
                    'div.profile_info_group > span > img::attr("src")').extract_first().strip()
        else:
            scrapy.Request(url, meta={'item': tosaveItem}, callback=self.toGongzhonghaoDetail)
        yield tosaveItem

    # 获取文章源代码。
    def parse_html(self, response):
        item = response.meta['item']
        html = response.css('div#js_article').extract()
        item['html'] = html
        result = response.css('div#js_article')
        pics = []
        imgs = result.css(".rich_media_content > p >img")
        if imgs is not None:
            for p in imgs:
                img = p.css('::attr("data-src")')
                if (img):
                    imgUrl = img.extract_first()
                    pics.append(imgUrl)
        item['pic'] = json.dumps(list(pics))
        yield item
