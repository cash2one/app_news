# -*- coding: utf-8 -*-


BOT_NAME = 'app_news'

SPIDER_MODULES = ['app_news.spiders']
NEWSPIDER_MODULE = 'app_news.spiders'

USER_AGENT = 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1'
ITEM_PIPELINES = {
    'app_news.pipelines.AppNewsPipeline':0
}

RANDOMIZE_DOWNLOAD_DELAY=True
DOWNLOAD_DELAY = 3
DOWNLOAD_TIMEOUT = 60

LOG_LEVEL='INFO'
LOG_FILE='scrapy.log'
LOG_ENCODING='utf-8'
COOKIES_ENABLES = False