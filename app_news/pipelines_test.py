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

class AppNewsPipeline(object):

    def __init__(self):
        self.result = open('result.dat','w')
    
    def process_item(self, item, spider):
        self.result.write(item['url']+'\n')
        self.result.write(item['content']+'\n')
        self.result.flush()
    
    def close_spider(self,spider):
        pass
    