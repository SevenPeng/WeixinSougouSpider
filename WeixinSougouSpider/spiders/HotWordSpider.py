# -*- coding: utf-8 -*-
import json
import uuid

import scrapy

from WeixinSougouSpider.items import HotWordItem, ToptenRelevantItem


class HotWordSpider(scrapy.Spider):
    # 爬虫名称
    name = "spider_hot_word"
    # 开始链接
    start_urls = [
        'http://weixin.sogou.com/',
    ]
    # 是否关闭爬虫
    close_down = False

    # 第一层爬取后处理函数
    def parse(self, response):
        # 提取并处理“搜索热词”
        for result in response.css('div.snb-right > div ol#topwords >li '):
            # 获取item样式
            item = HotWordItem()
            # 提取热词
            item['hotword'] = result.css('a::attr("title")').extract_first()
            # 提取链接
            item['hotwordLink'] = result.css('a::attr("href")').extract_first()
            # 提取等级
            item['rank'] = result.css("i::text").extract_first()
            # 生成唯一标识
            item['uuid'] = str(uuid.uuid1())
            yield item
            # 爬取第二层级
            request = scrapy.Request(item['hotwordLink'], callback=self.parse_item)
            # 传递参数给下一层级
            request.meta['item'] = item
            yield request

    # 第二层爬取后默认处理函数
    def parse_item(self, response):
        # 获取上一层级item
        item = response.meta['item']
        try:
            if response is not None:
                # 提取第一页所有相关的标题
                result = response.css('div.news-box > ul.news-list > li')
                # 只爬取相关热词的前10个标题 -- 第一页
                for i in range(10):
                    # 获取样式
                    toptenItem = ToptenRelevantItem()
                    # 提取标题
                    title = result[i].css('div.txt-box > h3 ').xpath('a/descendant::text()').extract()
                    toptenItem['title'] = ''.join(i.__str__() for i in title)
                    # 提取相关链接
                    toptenItem['contentLink'] = result[i].css('div.txt-box > h3 > a::attr("href")').extract_first()
                    contentLink = result[i].css('div.txt-box > h3 > a::attr("href")').extract_first()
                    # 提取介绍
                    introduction = result[i].css('div.txt-box').xpath('p/descendant::text()').extract()
                    toptenItem['introduction'] = ''.join(i.__str__() for i in introduction)
                    # 热词唯一标识，产生于上一层爬取
                    toptenItem['hotword_uuid'] = item['uuid']
                    # 提取时间
                    toptenItem['date_ago'] = result[i].css('div.txt-box >div.s-p::attr("t")').extract_first()
                    toptenItem['html'] = ''
                    # 产生文件路径的唯一标识
                    toptenItem['filePath_uuid'] = str(uuid.uuid1())
                    print('成功爬取第' + i + "个相关热词内容")
                    # 爬取第三层级，用第二层的item装载
                    request = scrapy.Request(contentLink, meta={'toptenItem': toptenItem}, callback=self.parse_html)
                    yield request
            else:
                yield item
                print('第一层级爬取获得的 response 为空！')
        except IOError as e:
            print('出现IO错误')

    def parse_html(self, response):
        # 获取文章源代码。
        item = response.meta['toptenItem']
        html = response.css('div#js_article').extract()
        # 提取源码
        item['html'] = html
        # 下载图片
        result = response.css('div#js_article')
        pics = []
        # 提取图片标签
        imgs = result.css(".rich_media_content > p >img")
        if imgs is not None:
            for p in imgs:
                # 提取图片链接
                img = p.css('::attr("data-src")')
                if (img):
                    imgUrl = img.extract_first()
                    pics.append(imgUrl)
        # 装载所有图片的链接
        item['pic'] = json.dumps(list(pics))
        yield item
