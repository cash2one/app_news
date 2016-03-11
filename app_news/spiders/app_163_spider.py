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
reload(sys)
sys.setdefaultencoding('utf-8')

from app_news.app_util import *
class AppSohuSpider(Spider):
    
    name = 'app_wangyi'
    seeds = [
# 汽车：
'http://c.m.163.com/nc/auto/list/5YyX5Lqs/0-100.html',
# 房产：
'http://c.m.163.com/nc/article/house/5YyX5Lqs/0-100.html',
# 头条：
'http://c.m.163.com/nc/article/headline/T1348647909107/0-100.html',
# 娱乐：
'http://c.m.163.com/nc/article/list/T1348648517839/0-100.html',
# 体育：
'http://c.m.163.com/nc/article/list/T1348649079062/0-100.html',
# 财经：
'http://c.m.163.com/nc/article/list/T1348648756099/0-100.html',
# 科技：
'http://c.m.163.com/nc/article/list/T1348649580692/0-100.html',
# 时尚：
'http://c.m.163.com/nc/article/list/T1348650593803/0-100.html',
# 轻松一刻：
'http://c.m.163.com/nc/article/list/T1350383429665/0-100.html',
# 军事：
'http://c.m.163.com/nc/article/list/T1348648141035/0-100.html',
# 历史：
'http://c.m.163.com/nc/article/list/T1368497029546/0-100.html',
# 家居：
'http://c.m.163.com/nc/article/list/T1348654105308/0-100.html',
# 原创：
'http://c.m.163.com/nc/article/list/T1370583240249/0-100.html',
# 画报：
'http://c.m.163.com/nc/article/list/T1422935072191/0-100.html',
# 游戏：
'http://c.m.163.com/nc/article/list/T1348654151579/0-100.html',
# 健康：
'http://c.m.163.com/nc/article/list/T1414389941036/0-100.html',
# 政务：
'http://c.m.163.com/nc/article/list/T1414142214384/0-100.html',
# 漫画：
'http://c.m.163.com/nc/article/list/T1444270454635/0-100.html',
# 哒哒：
'http://c.m.163.com/nc/article/list/T1444289532601/0-100.html',
# 彩票：
'http://c.m.163.com/nc/article/list/T1356600029035/0-100.html',
# NBA：
'http://c.m.163.com/nc/article/list/T1348649145984/0-100.html',
# 社会：
'http://c.m.163.com/nc/article/list/T1348648037603/0-100.html',
# 影视：
'http://c.m.163.com/nc/article/list/T1348648650048/0-100.html',
# 中国足球：
'http://c.m.163.com/nc/article/list/T1348649503389/0-100.html',
# 国际足球：
'http://c.m.163.com/nc/article/list/T1348649176279/0-100.html',
# CBA：
'http://c.m.163.com/nc/article/list/T1348649475931/0-100.html',
# 跑步：
'http://c.m.163.com/nc/article/list/T1411113472760/0-100.html',
# 手机：
'http://c.m.163.com/nc/article/list/T1348649654285/0-100.html',
# 数码：
'http://c.m.163.com/nc/article/list/T1348649776727/0-100.html',
# 移动互联：
'http://c.m.163.com/nc/article/list/T1351233117091/0-100.html',
# 云课堂：
'http://c.m.163.com/nc/article/list/T1421997195219/0-100.html',
# 旅游：
'http://c.m.163.com/nc/article/list/T1348654204705/0-100.html',
# 读书：
'http://c.m.163.com/nc/article/list/T1401272877187/0-100.html',
# 酒香：
'http://c.m.163.com/nc/article/list/T1385429690972/0-100.html',
# 教育：
'http://c.m.163.com/nc/article/list/T1348654225495/0-100.html',
# 亲子：
'http://c.m.163.com/nc/article/list/T1397116135282/0-100.html',
# 情感：
'http://c.m.163.com/nc/article/list/T1348650839000/0-100.html',
# 论坛：
'http://c.m.163.com/nc/article/list/T1349837670307/0-100.html',
# 博客：
'http://c.m.163.com/nc/article/list/T1349837698345/0-100.html'
]
    def __init__(self):
        self.appnameid = get_appnameid('wangyi')
	settings.set('LOG_FILE', self.name+'.log', priority='cmdline')
    
    def start_requests(self):
        reqs = []
        for url in self.seeds:
            reqs.append(Request(url))
        return reqs
        
    def parse(self,response):
        try:
            content = response.body_as_unicode()
        except:
            content = response.body
        datas = json.loads(content)
        if not datas:
            return
        key = datas.keys()[0]
        if len(datas.keys())>1:
            key = 'list'
        data = datas[key]
        for tmp in data:
            skipType = tmp.get('skipType','')
            if skipType=='photoset':
                #图片类型
                #http://c.m.163.com/photo/api/set/0003/575964.json
                title = tmp['title']
                photosetID = tmp['photosetID'] #00AJ0003|576036
                replyCount = tmp['replyCount']
                photosetID1 = photosetID.split('|')[0][-4:]
                photosetID2 = photosetID.split('|')[1]
                news_url = 'http://c.m.163.com/photo/api/set/%s/%s.json'%(photosetID1,photosetID2)
                req = Request(news_url,callback=self.parse_news,meta={'type':'photo',title:'title'})
                open('163_photo.my','a+').write(news_url+'\n')
                yield req
                replyItem = ReplycountItem()
                replyItem['appnameid'] = self.appnameid
                replyItem['url'] = news_url
                replyItem['replyCount'] = replyCount
		replyItem['updatetime'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                yield replyItem
            elif skipType =='live':
                #网络文字直播类型
                #http://data.live.126.net/liveAll/69862.json
                skipID = tmp['skipID']
                news_url = 'http://data.live.126.net/liveAll/%s.json'%(skipID)
                open('163_live.my','a+').write(news_url+'\n')
                pass
#             elif skipType=='special':
#                 #专题系列
#                 #http://c.m.163.com/nc/special/S1445582274703.html
#                 skipID = tmp['skipID']
#                 news_url = 'http://c.m.163.com/nc/special/%s.html'%(skipID)
#                 pass
            else:
                #http://c.m.163.com/nc/article/B7314G7I00031H2L/full.html
                docid = tmp['docid']
                if len(docid)>20:
                    continue
                replyCount = tmp['replyCount']
                news_url = 'http://c.m.163.com/nc/article/%s/full.html'%(docid)
                req = Request(news_url,callback=self.parse_news,meta={'type':'normal','docid':docid})
                open('163_normal.my','a+').write(news_url+'\t'+skipType+'\n')
                yield req
                replyItem = ReplycountItem()
		replyItem['appnameid'] = self.appnameid
                replyItem['url'] = news_url
                replyItem['replyCount'] = replyCount
                replyItem['updatetime'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                yield replyItem
    def parse_news(self,response):
        type = response.request.meta['type']
        docid = response.request.meta.get('docid')
        title = response.request.meta.get('title')
        url = response.url
        encoding = response.encoding
        http_code = response.status
        try:
            content = response.body_as_unicode()
        except:
            content = response.body
        if type=='normal':
            datas = w163_parse_normal(docid,content)
        elif type=='photo':
            datas = w163_parse_photo(content)
            datas.update({'title':title})
        html = structure_html(datas)
        page_info= PageMetaItem()
	url = url+'`@$`'+self.name
        page_info['url'] = url
        page_info['http_code'] = http_code
        page_info['resp_time'] = int(time.time())
        page_info['encoding'] = encoding
        page_info['content'] = html
        yield page_info

