# -*- encoding:utf-8 -*
import os
#配置文件

'''
scrapy_pattern.so库文件必须放置于conf目录中，运行crawler时，也需到conf目录下运行
eg:
    cd ../scrapy_genaral/conf
    scrapy crawl you -a seed=seed.urls -a sites=sites.dat -a single_scrapy=true 
'''
PROJECT = os.path.split(os.path.dirname(os.path.realpath(__file__)))[0]
#pipelines.py  --->path_par
DATA_FILES = PROJECT +'/data_files'
#DBFILE_MOVE_TARGET = DATA_FILES + '/output_eb/'
DBFILE_MAKING_DIR = DATA_FILES + '/list_crawler/'
DBFILE_MOVE_TARGET = '/disk2/list_crawler/output/'
#DBFILE_MAKING_DIR = '/disk2/list_crawler/'

UNFETCHING = 'app_unfetching'
