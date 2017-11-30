# 更新代理
from scrapy import cmdline

cmdline.execute('python proxiesSec.py'.split())
# 更新热词
cmdline.execute('scrapy crawl  spider_hot_word'.split())
# 更新热文
cmdline.execute('scrapy crawl spider_hot_article'.split())