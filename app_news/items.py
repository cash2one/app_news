# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Field,Item


class PageMetaItem(Item):
    url = Field()
    http_code = Field()
    content = Field()
    resp_time = Field()
    encoding = Field()

class ReplycountItem(Item):
    url = Field()
    appnameid = Field()
    replyCount = Field()
    readnum = Field() 
    likenum = Field() 
    unlikenum = Field() 
    playnum = Field() 
    repostsnum = Field() 
    updatetime = Field()
