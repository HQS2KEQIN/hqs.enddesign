import requests
from bs4 import BeautifulSoup
import math
import pymssql
import spacy
from translate import Translator
# url = 'https://arxiv.org/search/?query=ACL+2022&searchtype=all&source=header&start=0'
query=input("输入关键字")
num=int(input("输入你想爬取文章的数量："))
page=math.ceil(num/50)
l1=[]
header = {
    'Host': 'arxiv.org',
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7'
}
l3=[]
for i in range(1,page+1):
    #ps:输入的形式必须为Python/python 2022,不能为Python2021,别问为什么，搜不到
    url=f'https://arxiv.org/search/?query={query}&searchtype=all&source=header&start={(i-1)*50}'
    respon=requests.get(url,header)
    soup=BeautifulSoup(respon.text,'lxml')
    for k in range(1,num-(page-1)*50+1):
        l2=[]
        #通过select路径爬取数据
        website=soup.select(f"#main-container > div.content > ol > li:nth-child({k}) > div > p > a")[0].get('href')
        l1.append(website[-10:])
        title=soup.select(f"#main-container > div.content > ol > li:nth-child({k}) > p.title.is-5.mathjax")[0].get_text().strip()
        translator=Translator(from_lang='english', to_lang='chinese')
        title=translator.translate(title)
        abstract = soup.select(".abstract-full.has-text-grey-dark.mathjax")[0].get_text().strip()
        spacy_nlp = spacy.load("en_core_web_sm")
        doc = spacy_nlp(abstract)
        uurl=f'{website}'
        rrespon=requests.get(uurl,header)
        ssoup=BeautifulSoup(rrespon.text,'xml')
        subject = ssoup.select(".tablecell.subjects")[0].get_text()
        l2.append(title)
        l2.append(website)
        l2.append(subject)
        l2.append(doc)
        l2=tuple(l2)
        print(l2)
        l3.append(l2)
    #name.txt中存放的是每个PDF文件网址的最后10位
    with open('name.txt', 'w') as f:
        for n in range(len(l1)):
            f.write('https://arxiv.org/pdf/' + l1[n] + '\n')


def dataserver(information):
    db = pymssql.connect('LAPTOP-MU69SHNV', 'sa', '123456', 'hqs')
    if db:
        print("连接成功")
    cursor=db.cursor()
    try:
        sql="""IF OBJECT_ID('MYtable', 'U') IS NULL CREATE TABLE MYtable(title varchar(max),website varchar(max),subjects varchar(max),abstract varchar(max))"""
        sql1="""insert into MYtable values (%s,%s,%s,%s)"""
        cursor.execute(sql)
        cursor.executemany(sql1,information)
        db.commit()
        print("存储成功")
    except Exception as e:
        db.rollback()
        print(str(e))
    cursor.close()
    db.close()
dataserver(l3)
