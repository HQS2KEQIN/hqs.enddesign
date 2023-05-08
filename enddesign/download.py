import sys
import time
import requests
import threading
import os
import pandas as pd
import re
from bs4 import BeautifulSoup
import pymssql
import keywordget

with open("thesisweb\\user_name.txt", "r", encoding="utf-8") as w:
    username = w.read()
def Handler(start, end, url, filename):
    headers = {'Range': 'bytes=%d-%d' % (start, end)}
    r = requests.get(url, headers=headers, stream=True)
    with open(filename, "r+b") as fp:
        fp.seek(start)
        var = fp.tell()
        fp.write(r.content)

#下载pdf文件，索取arxiv论文PDF文件的网页
def download_file(url_of_file,name,number_of_threads):
    r = requests.head(url_of_file)
    if name:
        file_name = name
    else:
        file_name = url_of_file.split('/')[-1]
    try:
        file_size = int(r.headers['content-length'])
    except:
        print("无效的URL")
        return
    part = int(file_size) / number_of_threads
    fp = open(file_name, "wb")
    fp.close()
    for i in range(number_of_threads):
        start = int(part * i)
        end = int(start + part)
        t = threading.Thread(target=Handler,
            kwargs={'start': start, 'end': end, 'url': url_of_file, 'filename': file_name})
        t.setDaemon(True)
        t.start()

    main_thread = threading.current_thread()
    for t in threading.enumerate():
        if t is main_thread:
            continue
        t.join()

def dataserver(information):
    db = pymssql.connect('LAPTOP-MU69SHNV', 'sa', '123456', 'test')
    if db:
        print("连接成功")
    cursor=db.cursor()
    try:
        sql="IF OBJECT_ID('userdatabase', 'U') IS NULL " \
            "BEGIN " \
            "CREATE TABLE userdatabase" \
            "(id int primary key identity," \
            "username varchar(max)," \
            "queryname varchar(max),"\
            "title varchar(max)," \
            "website varchar(max)," \
            "subjects varchar(max)," \
            "abkey varchar(max)," \
            "number int); " \
            "END"
        sql1="insert into userdatabase values (%s,%s,%s,%s,%s,%s,%s)"
        cursor.execute(sql)
        cursor.executemany(sql1,information)
        db.commit()
        print("存储成功")
    except Exception as e:
        db.rollback()
        print(str(e))
    cursor.close()
    db.close()

#爬取论文标题和摘要部分
def dload(query,num,path):
    header = {
        'Host': 'arxiv.org',
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
    }

    l1=[]
    ll2=[]
    l3=[]
    num = int(num)
    page=num//50+1
    page=int(page)
    url1 = f'https://arxiv.org/search/?query={query}&searchtype=all&source=header&start=0'
    respon1 = requests.get(url1, header)
    soup1 = BeautifulSoup(respon1.text, 'lxml')
    numall= soup1.select(("#main-container > div.level.is-marginless > div.level-left > h1"))
    list1= []
    name = soup1.select(("#main-container > div.content > p.is-size-4.has-text-warning"))
    list2 = []
    for i in name:
        list2.append(i.get_text())
    list2 = [x.strip() for x in list2 if x.strip() != '']
    if list2!=[]:
        return 1
    else:
        for i in numall:
            list1.append(i.get_text())
        list1 = [x.strip() for x in list1 if x.strip() != '']
        Str = list1[0].split()
        allnum = int(Str[3].replace(",", ""))
        if num<=allnum:
            for i in range(1, page + 1):
                # ps:输入的形式必须为Python/python 2022,不能为Python2021,别问为什么，搜不到
                url = f'https://arxiv.org/search/?query={query}&searchtype=all&source=header&start={(i - 1) * 50}'
                respon = requests.get(url, header)
                soup = BeautifulSoup(respon.text, 'lxml')
                for k in range(1, num - (page - 1) * 50 + 1):
                    l2 = []
                    # 通过select路径爬取数据
                    website = soup.select(f"#main-container > div.content > ol > li:nth-child({k}) > div > p > a")[
                        0].get('href')
                    l1.append(website[-10:])
                    title = \
                    soup.select(f"#main-container > div.content > ol > li:nth-child({k}) > p.title.is-5.mathjax")[
                        0].get_text().strip()

                    uurl = f'{website}'
                    rrespon = requests.get(uurl, header)
                    ssoup = BeautifulSoup(rrespon.text, 'xml')
                    subject = ssoup.select(".tablecell.subjects")[0].get_text()
                    abstract = ssoup.select(".abstract.mathjax")[0].get_text().strip()
                    tr4w = keywordget.TextRank4Keyword()
                    tr4w.analyze(abstract, candidate_pos=['NOUN', 'PROPN'], window_size=4, lower=False)
                    adklist = tr4w.get_keywords(1)
                    keyword = adklist[0]
                    number = adklist[1]
                    l2.append(username)
                    l2.append(query)
                    l2.append(title)
                    ll2.append(title)
                    l2.append(website)
                    l2.append(subject)
                    l2.append(keyword)
                    l2.append(number)
                    l2 = tuple(l2)
                    l3.append(l2)
                # name.txt中存放的是每个PDF文件网址的最后10位
                with open('name.txt', 'w') as f:
                    for n in range(len(l1)):
                        f.write('https://arxiv.org/pdf/' + l1[n] + '\n')
            #保存在数据库中
            dataserver(l3)
            df1= pd.DataFrame(ll2,columns=['title'])
            df1.to_excel(f'../enddesign/data/{query}title.xls')
            info_txt_path = '../enddesign/name.txt' # todo:1
            save_path = f'{path}' # todo: 2
            file = open(info_txt_path)
            #此处用到爬虫代码里面的标题Excel为下载的文件重命名
            pf = pd.read_excel(f'../enddesign/data/{query}title.xls')
            l =list(pf['title'])
            l4=[]
            for i in range(len(l)):
                a=re.sub(r'[?:/|\||*<>@"]*','',l[i])
                l4.append(a)
            #由于l是列表文件，而后面download_file函数中name参数使用的str数据类型，所以这里定义一个i=0
            #由于遍历l中的每一个元素
            i=0
            for line in file.readlines():
                line = line.strip("\n")
                pdf_url = line+'.pdf'
                print('文件名:{}.PDF的URL:{}.'.format(l4[i],pdf_url))
                print('\n{}下载中...'.format(l4[i]))
                ts = time.time()
                download_file(url_of_file=pdf_url, name=os.path.join(save_path,l4[i]+'.pdf'),number_of_threads=1)
                i+=1
                te = time.time()
                print('耗时{:.0f}秒  {}下载完成'.format(te-ts, l4[i-1]))
                num-=1
                if num!=0:
                    print(f"还有{num}篇")
                    time.sleep(5)
                else:
                    print("下载完成")
                    sys.exit()
