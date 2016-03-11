#encoding:utf-8
import sys
import json
import time
import datetime

from scrapy.http import Request
from scrapy.selector import Selector
from scrapy.spider import Spider
from scrapy.conf import settings
from scrapy import log

from app_news.items import *
from app_news.app_util import *
reload(sys)
sys.setdefaultencoding('utf-8')
class AppIfengSpider(Spider):
    
    name = 'app_ifeng'
    #channelIds={'channelid':num}
    id_pages= {'SYLB10,SYDT10,SYRECOMMEND':10,'YL53,FOCUSYL53':10,'CJ33,FOCUSCJ33':10,'SZPD,FOCUSSZPD':10,\
               'JS83,FOCUSJS83':10,'TY43,FOCUSTY43,TYLIVE':10,'LS153,FOCUSLS153':10,\
                  'KJ123,FOCUSKJ123':10,'QC45,FOCUSQC45':10,'SS78,FOCUSSS78':10,'DZPD,FOCUSDZPD':10,'NXWPD,FOCUSNXWPD':10,\
                  'JK36,FOCUSJK36':10,'WH25,FOCUSWH25':10,'PBPD,PBPDFOCUS':10,'YX11,FOCUSYX11':10,'DYPD':10,\
                  'GJPD':10,'LY67,FOCUSLY67':10,'SM66,FOCUSSM66':10}
    #id_pages= {'SYLB10,SYDT10,SYRECOMMEND':10}
    def __init__(self):
	self.appnameid = get_appnameid('ifeng')
        settings.set('LOG_FILE', self.name+'.log', priority='cmdline')
    
    def start_requests(self):
        urlmod = 'http://api.iclient.ifeng.com/ClientNews?id=%s&page=%d'
	urlend = '&gv=4.4.8&av=4.4.8&uid=357143047442667&deviceid=357143047442667&proid=ifengnews&os=android_19&df=androidphone&vt=5&screen=1080x1776&publishid=5006'
        reqs = []
        for id,pagenum in self.id_pages.iteritems():
            for i in range(pagenum):
                page = i + 1
                url = urlmod%(id,page)
		url = url + urlend
                req = Request(url)
		open('ifeng_test.my','a+').write('%s\n'%(url))
                reqs.append(req)
        return reqs
    
    def parse(self,response):
        try:
            content = response.body_as_unicode()
        except:
            content = response.body
        datas = json.loads(content)
        for data in datas:
            curdata = data.get('item')
            if curdata:
                for tmp in curdata:
                    news_url = tmp['id']
		    if not news_url.startswith('http'):
			continue
                    yield Request(news_url,callback=self.parse_news)
                    replyCount = tmp.get('commentsall','N')
                    if replyCount!='N':
                        replyItem = ReplycountItem()
			replyItem['appnameid'] = self.appnameid
                        replyItem['url'] = news_url
                        replyItem['replyCount'] = replyCount
			replyItem['updatetime'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        yield replyItem
    
    def parse_news(self,response):
        url = response.url
        encoding = response.encoding
        http_code = response.status
        try:
            content = response.body_as_unicode()
        except:
            content = response.body
        try:
            datas = json.loads(content)
            title = datas['body']['title']
            content = datas['body']['text'] 
            pubtime = datas['body']['editTime']
            html = structure_html({'title':title,'content':content,'pubtime':pubtime})
            page_info= PageMetaItem()
            url = url+'`@$`'+self.name
            page_info['url'] = url
            page_info['http_code'] = http_code
            page_info['resp_time'] = int(time.time())
            page_info['encoding'] = encoding
            page_info['content'] = html
            yield page_info
        except:
            log.msg('%s  %s'%(http_code,url))
            open('ifeng_error.dat','a+').write('%s\n'%(url))
            open('ifeng_error.dat','a+').write(content)
            open('ifeng_error.dat','a+').write('\n')

