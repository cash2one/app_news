#encoding:utf-8
import sys
import json
import time
import random
import datetime

from scrapy.http import Request
from scrapy.selector import Selector
from scrapy.spider import Spider
from scrapy import log
from scrapy.conf import settings

from app_news.app_util import *
from app_news.items import *
reload(sys)
sys.setdefaultencoding('utf-8')

from app_news.app_util import *
from app_news.redis_api import RedisUtil

class ToutiaoSpider(Spider):
    
    name = 'app_toutiao'
    '''
    categorys:
       key:头条的分类
       value: min_behot_time:首页的min_behot_time为和中类型，time:事件类型,False:不存在
              last_refresh_sub_entrance_interval:若为time，则为时间类型，若为num则为数字类型，若为False则不存在
    
    categorys = {'news_hot':{'min_behot_time':'time','last_refresh_sub_entrance_interval':'time'},\
                 'news_society':{'min_behot_time':'time','last_refresh_sub_entrance_interval':'num'},\
                 'news_entertainment':{'min_behot_time':'time','last_refresh_sub_entrance_interval':'num'},\
                 }
                '''
    categorys = ['news_hot','news_society','news_entertainment','news_car','news_sports','news_finance',\
                 'news_military','news_world','news_health','news_game','movie','digital','news_fashion',\
                 'news_travel','news_baby','news_regimen','news_food','news_edu']
    TOTAL = 30
    listsnum = 0
    articles = set()
    def __init__(self):
        self.redis = RedisUtil()
	self.appnameid = get_appnameid('toutiao')
        settings.set('LOG_FILE', self.name+'.log', priority='cmdline')
    
    def start_requests(self):
        reqs = []
        user_agent = 'Dalvik/1.6.0 (Linux; U; Android 4.4.2; H60-L01 Build/HDH60-L01) NewsArticle/5.0.0'
        url_mod = 'http://ic.snssdk.com/2/article/v30/stream/?category=%s&count=20&last_refresh_sub_entrance_interval=%s&bd_city=null&bd_latitude=40.047015&bd_longitude=116.307561&bd_loc_time=1448332008&loc_mode=7&loc_time=1448332008&latitude=40.045697248874&longitude=116.30143679662&lac=4530&cid=25002&iid=3189938679&device_id=3351691922&ac=wifi&channel=tengxun&aid=13&app_name=news_article&version_code=500&version_name=5.0.0&device_platform=android&abflag=1&device_type=H60-L01&os_api=19&os_version=4.4.2&uuid=357143047442667&openudid=7be3e538e411a0c7&manifest_version_code=500&resolution=1080*1776&dpi=480'
        next_url_mod = 'http://ic.snssdk.com/2/article/v30/stream/?category=%s&count=20&max_behot_time=%s&last_refresh_sub_entrance_interval=%s&bd_latitude=40.046808&bd_longitude=116.307723&bd_loc_time=1448336123&loc_mode=7&loc_time=1448335299&latitude=40.045912357237&longitude=116.30182934602&lac=4530&cid=25002&iid=3189938679&device_id=3351691922&ac=wifi&channel=tengxun&aid=13&app_name=news_article&version_code=500&version_name=5.0.0&device_platform=android&abflag=1&device_type=H60-L01&os_api=19&os_version=4.4.2&uuid=357143047442667&openudid=7be3e538e411a0c7&manifest_version_code=500&resolution=1080*1776&dpi=480'
        for category in self.categorys:
            #第一页
            #特殊参数：&ssmix=a  该参数会让返回的数据经过特殊处理,所以去掉了url中的&ssmix=a
            now = int(time.time())
            last_refresh_sub_entrance_interval = now
            #min_behot_time = now - 3600*(random.randint(20,24))
            url = url_mod%(category,last_refresh_sub_entrance_interval)
            req = Request(url,headers={'User-Agent':user_agent})
            reqs.append(req)
            self.listsnum += 1
            #翻页
            for i in range(self.TOTAL):
                max_behot_time = now - random.randint(2,4)*(i+1)*3600
                last_refresh_sub_entrance_interval = last_refresh_sub_entrance_interval + i*random.randint(2,4)
                next_url = next_url_mod%(category,max_behot_time,last_refresh_sub_entrance_interval)
                req = Request(next_url,headers={'User-Agent':user_agent})
                reqs.append(req)
                self.listsnum += 1
        return reqs
        
    def parse(self,response):
        self.listsnum = self.listsnum - 1
        try:
            content = response.body_as_unicode()
        except:
            content = response.body
        datas = json.loads(content).get('data')
        if datas:
            for data in datas:
                try:
                    try:
                        news_url = data['share_url']
                    except:
                        news_url = data['url']
                    comment_count = data.get('comment_count',0)
                    replyItem = ReplycountItem()
		    replyItem['appnameid'] = self.appnameid
		    replyItem['updatetime'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    replyItem['url'] = news_url
                    replyItem['replyCount'] = comment_count
                    yield replyItem
                    self.articles.add(news_url)
                    #req = Request(news_url,callback=self.parse_news)
                    #yield req
                except:
                    log.msg('ERROR: %s'%(response.url),log.ERROR)
                    open('error_toutiao.dat','a+').write('%s\n'%(response.url))
                    open('error_toutiao.dat','a+').write(json.dumps(data,indent=4))
                    open('error_toutiao.dat','a+').write('\n')
        if self.listsnum==0:
            open('toutiao_articles.my','w').write('\n'.join(self.articles)) 
            for news_url in self.articles:
                if self.redis.check_url(news_url):
                    continue
                user_agent = 'Dalvik/1.6.0 (Linux; U; Android 4.4.2; H60-L01 Build/HDH60-L01) NewsArticle/5.0.0'
                req = Request(news_url,headers={'User-Agent':user_agent},callback=self.parse_news)
                yield req
            
    def parse_news(self,response):
        url = response.url
        encoding = response.encoding
        http_code = response.status
        try:
            content = response.body_as_unicode()
        except:
            content = response.body
        page_info= PageMetaItem()
        url = url+'`@$`'+self.name
        page_info['url'] = url
        page_info['http_code'] = http_code
        page_info['resp_time'] = int(time.time())
        page_info['encoding'] = encoding
        page_info['content'] = content
        yield page_info
        

