
import codecs
import os
import sys
from datetime import datetime
import time
import shutil
import re
import string

from scrapy import log
from scrapy.exceptions import DropItem
from scrapy.utils.python import unicode_to_str

from items import *
from config import *
from bkdbWrapper import *
import mysql_api  as mysql
from redis_api import RedisUtil


def unicode_to_gbk(src):
    return unicode_to_str(src,'gbk',errors='ignore')

class AppNewsPipeline(object):
    total_cnt = 0
    total = 0
    dbfile_move_target = DBFILE_MOVE_TARGET
    dbfile_making_dir = DBFILE_MAKING_DIR
    nums_in_eachDBFile = 1000
    _pa_reset_encoding = re.compile(r'charset=([\w-]+)', re.I)
    time_stamp = 0

    def __init__(self):
        self.pid = os.getpid()
        self.time_start = datetime.now()
        self.batch_id = string.atoi(time.strftime("%Y%m%d"))
        self.connect()
        self.redis = RedisUtil()
    
    def connect(self):
        self.conn = mysql.connect('app_crawler',host='192.168.241.17')
        self.cursor = self.conn.cursor()
        self.conn.set_character_set('utf8')
        self.cursor.execute('set names utf8mb4')
        self.cursor.execute('SET CHARACTER SET utf8;')
        self.cursor.execute('SET character_set_connection=utf8;')
        self.cursor.execute('set interactive_timeout=24*3600;')
        self.cursor.execute('set wait_timeout=24*3600;')
        
    def _createNewDBFile(self):
        self.time_stamp = time.time()
        db_file_name = "RawData_app_"+str(self.time_stamp)+'_'+str(self.pid)+'.db'
        self.db_file = os.path.join( self.dbfile_making_dir,db_file_name)
        try:
            self.db = BKDB()
            self.db.createDb(self.db_file)
        except:
            log.msg( 'exception in create db',level=log.ERROR)
            sys.exit(-1)

    def open_spider(self,spider):
        self.time_stamp = datetime.now().isoformat()
        self._createNewDBFile()
        self.file = codecs.open("ok_%s_%d.dat"%(time.strftime("%Y%m%d%H%M%S"),os.getpid()),'w','utf-8', errors='ignore')

    def _writeDBFile(self,item):
        try:
            wpd = TWebPageData()
            if item['encoding'] == 'big5':
                self.db.appendToDb(wpd,item['url'], "", item['content'] )
            else:
                gbk_body_charset = self._pa_reset_encoding.sub('charset=gbk',item['content'])
                self.db.appendToDb(wpd,item['url'], "",unicode_to_gbk(gbk_body_charset) )
        except:
            print 'wrong url:',item['url']
            info=sys.exc_info()
            print info[0],":",info[1]

    def process_item(self, item, spider):
        self.total_cnt += 1
        if isinstance(item, PageMetaItem):
            http_code = item['http_code']
            self.file.write(item['url']+'\n')
            self.redis.add_url(item['url'])
            if http_code >= 200 and http_code < 300:
                self.total += 1
                try:
                    if self.total % self.nums_in_eachDBFile == 0:
                        self.db.closeDb()
                        if os.path.exists(self.db_file):
                            shutil.move(self.db_file,self.dbfile_move_target)
                        else:
                            err = '+++no_db_file:',self.db_file
                            print err
                            log.msg(err,level=log.ERROR)
                        self._createNewDBFile()
 
                    if item['url'] and item['content']:
                        self._writeDBFile(item)
                except:
                    print '=URL=',item['url'],'=body=',item['content']
                    info=sys.exc_info()
                    print info[0],":",info[1]
        elif isinstance(item,ReplycountItem):
            url = item['url']
            appnameid = item['appnameid']
            replyCount = item.get('replyCount',0)
            readnum = item.get('readnum',0) 
            likenum = item.get('likenum',0) 
            unlikenum = item.get('unlikenum',0) 
            playnum = item.get('playnum',0) 
            repostsnum = item.get('repostsnum',0) 
            updatetime =  item.get('updatetime',0)
            sql = 'insert into container(url,appnameid,replyCount,readnum,likenum,unlikenum,playnum,repostsnum,updatetime) values("%s",%s,%s,%s,%s,%s,%s,%s,"%s");'
            sql = sql%(url,appnameid,replyCount,readnum,likenum,unlikenum,playnum,repostsnum,updatetime)
            mysql.insert(self.conn, sql)
	    #cursor = self.conn.cursor()
	    #cursor.execute(sql)
            mysql.commit(self.conn)

    def close_spider(self,spider):
        if self.conn:
            mysql.close(self.conn)
        if os.path.exists(self.db_file):
            self.db.closeDb()
            shutil.move(self.db_file,self.dbfile_move_target)
        print 'total_item:%s'%self.total_cnt
        log.msg('time:%s, links: %s'%(self.time_stamp, self.total_cnt),level=log.INFO)

