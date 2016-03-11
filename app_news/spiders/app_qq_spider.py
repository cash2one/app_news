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
class AppTXSpider(Spider):
    
    name = 'app_qq'
    
    urlstart = 'http://r.inews.qq.com/getQQNewsIndexAndItems?uid=7be3e538e411a0c7&Cookie=%20lskey%3D%3B%20luin%3D%3B%20skey%3D%3B%20uin%3D%3B%20logintype%3D0%20&qn-rid=1388750078&store=118&hw=HUAWEI_H60-L01&devid=357143047442667&qn-sig=bdaad9f585aafe893e739fed534f2e74&screen_width=1080&mac=80%253A71%253A7a%253A88%253A92%253Ac4&chlid='
    urlend = '&appver=19_android_4.7.3&qqnetwork=wifi&mid=4c47ac7943fad1a0443f87c2a2855ffea98e483a&imsi=460025109745852&apptype=android&screen_height=1776'
    channels = ['news_news_top','news_news_bj&appver','news_news_ent','news_news_sports','news_news_finance','news_news_tech',\
                'news_news_ssh','news_news_mil','news_news_lad','news_news_auto','news_news_game','news_video_main',\
                'news_news_istock','news_news_world','news_news_cul','news_news_anja','news_news_digi','news_news_housebj',\
                'news_news_astro','news_news_edu','news_video_top','news_news_fx','news_news_lic','news_news_ac','news_news_audio',\
                'news_news_msh','news_news_cq','news_news_gd','news_news_cd','news_news_sh','news_news_xian','news_news_hb',\
                'news_news_zj','news_news_henan','news_news_hn','news_news_fj','news_news_js','news_news_ln','news_news_tj',\
                'news_news_heb']
    def __init__(self):
	self.appnameid = get_appnameid('qq')
        settings.set('LOG_FILE', self.name+'.log', priority='cmdline')
    
    def start_requests(self):
        reqs = []
        for channel in self.channels:
            curl = self.urlstart+channel+self.urlend
            req = Request(curl)
            reqs.append(req)
        return reqs
    
    def parse(self,response):
        try:
            content = response.body_as_unicode()
        except:
            content = response.body
        datas = json.loads(content)
        ids = datas.get('idlist')[0].get('ids')
        for tmp in ids:
            id = tmp.get('id')
            commnum = tmp.get('comments',0)
            newsurl = 'http://view.inews.qq.com/a/'+id
	    replyItem = ReplycountItem()
	    replyItem['appnameid'] = self.appnameid
	    replyItem['updatetime'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            replyItem['url'] = newsurl
            replyItem['replyCount'] = commnum
            yield replyItem
            yield Request(newsurl,callback=self.parse_news)
    
    def parse_news(self,response):
        try:
            content = response.body_as_unicode()
        except:
            content = response.body
        url = response.url
        encoding = response.encoding
        http_code = response.status
        page_info= PageMetaItem()
        url = url+'`@$`'+self.name
        page_info['url'] = url
        page_info['http_code'] = http_code
        page_info['resp_time'] = int(time.time())
        page_info['encoding'] = encoding
        page_info['content'] = content
        yield page_info
        
        
        
        
        
        
        
        
        
        
