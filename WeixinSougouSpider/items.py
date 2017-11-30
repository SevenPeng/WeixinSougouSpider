# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class HotWordItem(scrapy.Item):
    # 热词
    hotword = scrapy.Field()
    # 链接
    hotwordLink = scrapy.Field()
    # 等级
    rank = scrapy.Field()
    # 唯一标识
    uuid = scrapy.Field()


class ToptenRelevantItem(scrapy.Item):
    # 相关标题
    title = scrapy.Field()
    # 介绍
    introduction = scrapy.Field()
    # 相关链接
    contentLink = scrapy.Field()
    # 热词唯一标识
    hotword_uuid = scrapy.Field()
    # 相关标题的源码
    html = scrapy.Field()
    # 发布时间，相较现在的时间
    date_ago = scrapy.Field()
    # 相关标题的所有图片链接
    pic = scrapy.Field()
    # 文件路径的唯一标识
    filePath_uuid = scrapy.Field()


class HotArticleItem(scrapy.Item):
    # 工具栏 热文类别
    toolbar = scrapy.Field()
    contentLink = scrapy.Field()
    introduction = scrapy.Field()
    title = scrapy.Field()
    html = scrapy.Field()
    from_wx_link = scrapy.Field()
    date_ago = scrapy.Field()
    wx_name = scrapy.Field()
    wx_imgLink = scrapy.Field()
    wx_nameImg = scrapy.Field()
    rewenSummary = scrapy.Field()
    pic = scrapy.Field()
    filePath_uuid = scrapy.Field()
