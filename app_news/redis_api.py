import redis
import config


class RedisUtil(object):
    
    db = redis.StrictRedis('127.0.0.1',port=6379,db='0')
    def __init__(self):
        self.db.expire(config.UNFETCHING, 8*60*60*24)
    
    def delete_keys(self):
        self.db.delete(config.UNFETCHING)
        
    def add_url(self,url):
        self.db.sadd(config.UNFETCHING,url)
      
    def check_url(self,url):
        return self.db.sismember(config.UNFETCHING, url)
    
if __name__ == '__main__':
    db = RedisUtil()
    db.delete_keys()
