#encoding:utf-8
from xml.etree import ElementTree
import json
import mysql_api as mysql

htmlmod = '''
<html>
    <head>
        <title>%s</title>
        <meta http-equiv="content-type" content="text/html; charset=UTF-8" />
    </head>
    <body>
        <date>%s</date>
        %s
    </body>
</html>
'''.decode('utf-8')
def structure_html(datas):
    html = htmlmod%(datas['title'],datas['pubtime'],datas['content'])
    return html

def sohu_parse_xml(xmlString):
    root = ElementTree.fromstring(xmlString)
    #find:查找出一个标签，并且返回一个标签对象node  node.text获取值,node.tag获取标签名称
    title = root.find('title').text
    pubtime = root.find('time').text
    contentroot = root.findall('content')
    if not contentroot:
        contentroot = root.findall('abstract')
    tmps =[tmp.text for tmp in contentroot]
    content = '\n'.join(tmps)
    return {'title':title,'pubtime':pubtime,'content':content}

def w163_parse_normal(docid,content):
    datas = json.loads(content)
    content = datas.get(docid).get('body')
    title = datas.get(docid).get('title')
    pubtime = datas.get(docid).get('ptime')
    return {'title':title,'pubtime':pubtime,'content':content}
    
def w163_parse_photo(content):
    datas = json.loads(content)
    content = datas.get('desc')
    pubtime = datas.get('datatime')
    return {'pubtime':pubtime,'content':content}
    

def get_appnameid(appname):
    sql = 'select id from appname_maps where e_appname="%s";'%(appname)
    conn = mysql.connect('app_crawler', '192.168.241.17')
    id = mysql.query_one(conn, sql)[0]
    mysql.close(conn)
    return id




