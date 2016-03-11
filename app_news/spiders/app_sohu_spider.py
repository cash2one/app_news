#encoding:utf-8
import sys
import json
import time
import datetime

from scrapy.http import Request
from scrapy.selector import Selector
from scrapy.spider import Spider
from scrapy.conf import settings

from app_news.items import *
from app_news.app_util import *
reload(sys)
sys.setdefaultencoding('utf-8')
class AppSohuSpider(Spider):
    
    name = 'app_sohu'
    #channelIds={'channelid':num}
    channelIds = {'1':1000,'2':240,'3':240,'4':240,'5':200,'6':100,'11':300,'12':200,'16':200,\
                  '23':200,'29':200,'45':200,'46':200,'49':200,'50':200,'65':200,'97':200,'98':100,'177':200,'247':200,'248':200,\
                  '251':200,'954509':100,'959562':100}
    def __init__(self):
	self.appnameid = get_appnameid('sohu')
        settings.set('LOG_FILE', self.name+'.log', priority='cmdline')
    
    def start_requests(self):
        urlmod = 'http://api.k.sohu.com/api/channel/news.go?channelId=%s&num=%d&page=1'
        reqs = []
        for channelid,num in self.channelIds.iteritems():
            url = urlmod%(channelid,num)
            req = Request(url)
            reqs.append(req)
        return reqs
    
    def parse(self,response):
        try:
            content = response.body_as_unicode()
        except:
            content = response.body
        datas = json.loads(content)
        channelId = datas.get('channelId')
        focals = datas.get('focals')
        if focals:
            newsid = focals[0]['newsId']
            commnum = focals[0].get('commentNum',0)
            focals_url = 'http://api.k.sohu.com/api/photos/gallery.go?newsId=%s&channelId=%s'%(newsid,channelId)
	    replyItem = ReplycountItem()
	    replyItem['appnameid'] = self.appnameid
	    replyItem['updatetime'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            replyItem['url'] = focals_url
            replyItem['replyCount'] = commnum
            yield replyItem
            yield Request(focals_url,callback=self.parse_news)
        articles = datas.get('articles')
        for tmp in articles:
            newsId = tmp['newsId']
            commnum = tmp.get('commentNum',0)
            newsurl = 'http://api.k.sohu.com/api/news/article.go?newsId=%s&channelId=%s'%(newsId,channelId)
            replyItem = ReplycountItem()
            replyItem['appnameid'] = self.appnameid
            replyItem['updatetime'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            replyItem['url'] = newsurl
            replyItem['replyCount'] = commnum
            yield replyItem
            yield Request(newsurl,callback=self.parse_news)
    
    def parse_news(self,response):
        url = response.url
        encoding = response.encoding
        http_code = response.status
        try:
            content = response.body_as_unicode()
        except:
            content = response.body
        datas = sohu_parse_xml(content)
        html = structure_html(datas)
        page_info= PageMetaItem()
        url = url+'`@$`'+self.name
        page_info['url'] = url
        page_info['http_code'] = http_code
        page_info['resp_time'] = int(time.time())
        page_info['encoding'] = encoding
        page_info['content'] = html
        yield page_info
               
