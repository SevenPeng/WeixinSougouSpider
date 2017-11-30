# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import datetime
import json
import os
import uuid

import pymysql
import scrapy
from scrapy.exceptions import DropItem
from scrapy.pipelines.images import ImagesPipeline
from scrapy.spidermiddlewares import referer
from twisted.enterprise import adbapi

from WeixinSougouSpider.items import HotWordItem, ToptenRelevantItem


class Wxsou1016Pipeline(object):
    '''保存到数据库中对应的class
       1、在settings.py文件中配置
       2、在自己实现的爬虫类中yield item,会自动执行'''

    wxsougou_key = ['hotword', 'hotwordLink', 'rank']
    wxsougou_topten_key = ['contentLink', 'title', 'uuid']

    insertWxsougou_sql = '''insert into wxsougou (%s) values (%s)'''
    insertWxsougou_topten_sql = '''insert into wxsougou_topten (%s) values (%s)'''
    feed_query_sql = "select * from MeiziFeed where feedId = %s"
    user_query_sql = "select * from MeiziUser where userId = %s"
    feed_seen_sql = "select feedId from MeiziFeed"
    user_seen_sql = "select userId from MeiziUser"

    close = False

    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        '''1、@classmethod声明一个类方法，而对于平常我们见到的则叫做实例方法。
           2、类方法的第一个参数cls（class的缩写，指这个类本身），而实例方法的第一个参数是self，表示该类的一个实例
           3、可以通过类来调用，就像C.f()，相当于java中的静态方法'''
        dbparams = dict(
            host=settings['MYSQL_HOST'],  # 读取settings中的配置
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PASSWD'],
            charset='utf8',  # 编码要加上，否则可能出现中文乱码问题
            cursorclass=pymysql.cursors.DictCursor,
            use_unicode=False,
        )

        dbpool = adbapi.ConnectionPool('pymysql', **dbparams)  # **表示将字典扩展为关键字参数,相当于host=xxx,db=yyy....
        return cls(dbpool)  # 相当于dbpool付给了这个类，self中可以得到

    # pipeline默认调用
    def process_item(self, item, spider):
        if spider.name == 'ws_hotword':
            if isinstance(item, HotWordItem):
                query = self.dbpool.runInteraction(self._conditional_insertHotword, item)  # 调用插入的方法
                query.addErrback(self._handle_error, item, spider)  # 调用异常处理方法
            elif isinstance(item, ToptenRelevantItem):
                query = self.dbpool.runInteraction(self._conditional_insertHotwordTopten, item)  # 调用插入的方法
                query.addErrback(self._handle_error, item, spider)  # 调用异常处理方法
        elif spider.name == 'ws_rewen':
            query = self.dbpool.runInteraction(self._conditional_insertRewen, item)  # 调用插入的方法
            query.addErrback(self._handle_error, item, spider)  # 调用异常处理方法
        return item

    # 写入数据库中
    def _conditional_insertHotword(self, tx, item):
        # 首先去重
        querysql = "select * from yx_wxsougou where hotword = %s "
        tx.execute(querysql, (item['hotword']))
        result = tx.fetchone()
        # insert
        if result == None:
            dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sql = "insert into yx_wxsougou(hotword,hotwordLink,rank,uuid,createDate) values(%s,%s,%s,%s,%s)"
            paramsHotword = (item["hotword"], item["hotwordLink"], item['rank'], item['uuid'], dt)
            tx.execute(sql, paramsHotword)
        else:
            ##update
            hid = [int(result['id'])][0]
            dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            updateSql = "update yx_wxsougou set hotword=%s,hotwordLink=%s,rank=%s,uuid=%s,createDate=%s where id=%s"
            paramsHotword = (item["hotword"], item["hotwordLink"], item['rank'], item['uuid'], dt, str(hid))
            tx.execute(updateSql, paramsHotword)

    def _conditional_insertHotwordTopten(self, tx, item):
        # 去重
        querysql = "select * from yx_wxsougou_topten where title=%s and introduction=%s"
        tx.execute(querysql, (item['title'], item['introduction']))
        result = tx.fetchone()
        if result == None:
            # insert
            sqltopten = "insert into yx_wxsougou_topten(title,contentLink,hotword_uuid,introduction,html,date_ago,filePath_uuid)values(%s,%s,%s,%s,%s,%s,%s)"
            paramsTopten = (
                item['title'], item['contentLink'], item['hotword_uuid'], item['introduction'], item['html'],
                item['date_ago'], item['filePath_uuid'])
            tx.execute(sqltopten, paramsTopten)
        else:
            # update
            hid = [int(result['id'])][0]
            dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            updateSql = "update yx_wxsougou_topten set title=%s,contentLink=%s,hotword_uuid=%s,introduction=%s,html=%s,date_ago=%s where id=%s"
            paramsTopten = (
                item['title'], item['contentLink'], item['hotword_uuid'], item['introduction'], item['html'],
                item['date_ago'])
            tx.execute(updateSql, paramsTopten)
            print("文章一样需要更新")

    def _conditional_insertRewen(self, tx, item):
        # 首先进行去重
        querysql = "select * from yx_wxsougou_rewen where title=%s and introduction=%s"
        tx.execute(querysql, (item['title'], item['introduction']))
        result = tx.fetchone()
        if result == None:
            dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            item['wx_nameImg'] = str(uuid.uuid1()).replace("-", '')
            sql = "insert into yx_wxsougou_rewen(toolbar,contentLink,introduction,title,from_wx_link,wx_name,wx_nameImg,wx_imgLink,createTime,date_ago,html,filePath_uuid) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            paramsRewen = (
                item["toolbar"], item["contentLink"], item['introduction'], item['title'], item['from_wx_link'],
                item['wx_name'], item['wx_nameImg'], item['wx_imgLink'], dt, item['date_ago'], item['html'],
                item['filePath_uuid'])
            tx.execute(sql, paramsRewen)
        else:
            # update
            print("文章一样不需要重新插入")

    def insert_data(self, item, insert, sql_key):
        fields = u','.join(sql_key)
        qm = u','.join([u'%s'] * len(sql_key))
        sql = insert % (fields, qm)
        data = [item[k] for k in sql_key]
        return self.dbpool.runOperation(sql, data)

    # 错误处理方法
    def _handle_error(self, failue, item, spider):
        print("--------------database operation exception!!-----------------")
        failue


class ImageCachePipeline(ImagesPipeline):
    def file_path(self, request, response=None, info=None):
        """
        :param request: 每一个图片下载管道请求
        :param response:
        :param info:
        :param strip :清洗Windows系统的文件夹非法字符，避免无法创建目录
        :return: 每套图的分类目录
        """
        item = request.meta['item']
        # 文件夹
        filePath_uuid = item['filePath_uuid'].strip()
        # 文件名
        filename = str(uuid.uuid1()).strip()
        # if os.path.isdir('D:/picture/'+filename):
        if os.path.isdir('/usr/local/jm_spider/picture/' + filename):
            pass
        else:
            filename = u'{0}/{1}{2}'.format(filePath_uuid, filename, '.jpg')
            return filename

    def get_media_requests(self, item, info):
        pics = item['pic']
        if pics is not None:
            list = json.loads(pics)
            for image_url in list:
                yield scrapy.Request(image_url, meta={'item': item, 'referer': referer})

    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok, x in results if ok]
        if not image_paths:
            print("图片未下载好:%s" % image_paths)
            raise DropItem('图片未下载好 %s' % image_paths)
