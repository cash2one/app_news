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
from app_news.redis_api import RedisUtil 
reload(sys)
sys.setdefaultencoding('utf-8')
class AppSinaSpider(Spider):
    name = 'app_sina'
    
    channels = {'news_toutiao':20,'news_ent':10,'news_sports':10,'news_finance':10,\
                'news_auto':20,'news_tech':10,'news_funny':10,'news_mil':10,'news_sh':10,\
                'news_eladies':10,'news_fashion':10,'news_blog':10,'news_edu':10,'news_digital':10,\
                'news_nba':10,'news_health':10,'news_baby':10,'news_history':10,'news_home':10,'zhuanlan_recommend':10}
    listsnum = 0    
    def __init__(self):
        self.redis = RedisUtil()
        self.article_reqs = []
	self.appnameid = get_appnameid('sina')
        settings.set('LOG_FILE', self.name+'.log', priority='cmdline')
    
    def start_requests(self):
        urlmod = 'http://api.sina.cn/sinago/list.json?uid=82a5a90a39670893&loading_ad_timestamp=0&platfrom_version=4.4.2&wm=b207&oldchwm=12010_0002&imei=357143047442667&from=6048295012&connection_type=2&chwm=12010_0002&AndroidID=571ad625b3af8b5c867bbc073c6aa80b&v=1&IMEI=e87875308b37d509378ffacaf9ac3011&user_uid=3815417154&MAC=4f4f13bcd710d1abd957d196a463510f&s=20&channel=%s&p=%s'
        header = {'User-Agent': 'H60-L01__sinanews__4.8.2__android__4.4.2'}
        reqs = []
        for channel,page in self.channels.iteritems():
            for i in range(page):
                url = urlmod%(channel,i+1)
                req = Request(url,headers=header)
                reqs.append(req)
                self.listsnum += 1
        return reqs
    
    def parse(self,response):
        self.listsnum -= 1
        try:
            content = response.body_as_unicode()
        except:
            content = response.body
        datas = json.loads(content)
        articleinfos = datas['data']['list']
        for ainfo in articleinfos:
#             title = ainfo['title']
#             id = ainfo['id']
            try:
                link = ainfo['link']
                #以http://sax.sina.com.cn开头的属于广告类似的文章
                if link.startswith('http://sax.sina.com.cn'):
                    continue
                if self.redis.check_url(link):
                    continue
                comment_count_info = ainfo.get('comment_count_info')
                pubDate = ainfo['pubDate']
                if comment_count_info:
                    comment_count = comment_count_info['show']
                    replyItem = ReplycountItem()
		    replyItem['appnameid'] = self.appnameid
		    replyItem['updatetime'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    replyItem['url'] = link
                    replyItem['replyCount'] = comment_count
                    yield replyItem
                header = {'User-Agent': 'H60-L01__sinanews__4.8.2__android__4.4.2'}
                req = Request(link,headers=header,meta={'pubDate':pubDate},callback=self.parse_news)
                self.article_reqs.append(req)
            except:
                open('sina_error.dat','a+').write('%s\n'%(response.url))
                open('sina_error.dat','a+').write(json.dumps(ainfo, indent=4))
                open('sina_error.dat','a+').write('\n')
        if self.listsnum==0:
            for req in self.article_reqs:
                yield req
            
    def parse_news(self,response):
        pubDate = response.request.meta['pubDate']
        url = response.url
        encoding = response.encoding
        http_code = response.status
        try:
            content = response.body_as_unicode()
        except:
            content = response.body
        try:
            sel = Selector(text=content)
            title = sel.xpath('//div[@class="main"]/h4/text()').extract()[0]
            body = sel.xpath('//div[@class="main"]').extract()[0].replace('<h4>%s</h4>'%(title),'')
            pubtime = datetime.datetime(* time.localtime(pubDate)[:6]).strftime('%Y-%m-%d %H:%M:%S')
            html = structure_html({'title':title,'pubtime':pubtime,'content':body})
        except:
            html = content
        page_info= PageMetaItem()
        url = url+'`@$`'+self.name
        page_info['url'] = url
        page_info['http_code'] = http_code
        page_info['resp_time'] = int(time.time())
        page_info['encoding'] = encoding
        page_info['content'] = html
        yield page_info
                
                
                
                
