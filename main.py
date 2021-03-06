import urllib.request, urllib.parse, urllib.error
from bs4 import BeautifulSoup
import re
import time
import xlwt
import sqlite3
import random
import os



start = time.perf_counter()
baseurl = 'https://movie.douban.com/top250?start='
savepath = 'top250.xls'
dbPath = 'database/top250.db'
findLink = re.compile(r'<a href="(.*?)">')
findSrc = re.compile(r'<img.*src="(.*?)"', re.S)
findTitle = re.compile(r'<span class="title">(.*)</span>')
findRate = re.compile(r'<span class="rating_num" property="v:average">(.*)?</span>')
findJudge = re.compile(r'<span>(\d*)人评价</span>')
findInq = re.compile(r'<span class="inq">(.*)?</span>')
findBd = re.compile(r'<p class="">(.*?)</p>', re.S)


# 获取数据

def askUrl(url):
    html = ''

    try:
        u = url
        d = bytes(urllib.parse.urlencode({'mother': 'judy', 'father': 'martin'}), encoding='utf-8')
        h = {
            "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36\
             (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36',
            "Cookie": 'bid=XiB86MEvs1g; douban-fav-remind=1;\
             _pk_id.100001.8cb4=db56cb766cf56658.1602506374.1.1602506374.1602506374.;\
              __utma=30149280.91083374.1602506375.1602506375.1602506375.1; ll="108258";\
               viewed="25635441_20392525_27110924_30430012_10810770_30467343_34797966_\
               34614119_34815690_34788620"; push_doumail_num=0; ps=y; push_noty_num=0;\
                dbcl2="207247574:cfHcm+aTzHY"; ck=iwBr; ap_v=0,6.0'
        }
        req = urllib.request.Request(url=u, method='GET', headers=h, data=d)
        res = urllib.request.urlopen(req)
        html = res.read().decode('utf-8')
    except urllib.error.URLError as e:
        print('Go Wrong!')
        if hasattr(e, 'code'):
            print(e.code)
        if hasattr(e, 'reason'):
            print(e.reason)

    return html


# 处理数据

def getData(baseurl):
    datalist = []
    for i in range(10):
        url = baseurl + str(i * 25)
        html = askUrl(url)
        time.sleep(random.random()*3)  # 速率仿真
        soup = BeautifulSoup(html, 'html.parser')
        for item in soup.find_all('div', class_='item'):
            data = []
            items = str(item)
            link = re.findall(findLink, items)[0]
            data.append(link)
            imgSrc = re.findall(findSrc, items)[0]
            imgSrc_new = imgSrc[:-3]+'webp'
            data.append(imgSrc_new)
            titles = re.findall(findTitle, items)
            if len(titles) == 2:
                ctitle = titles[0]
                data.append(ctitle)
                otitle = titles[1].replace('/', '')  # 去掉无关符号
                data.append(otitle.strip())
            else:
                data.append(titles[0])
                data.append(' ')  # 外国名留空
            rating = re.findall(findRate, items)[0]
            data.append(rating)
            judge = re.findall(findJudge, items)[0]
            data.append(judge)
            inq = re.findall(findInq, items)
            if len(inq) != 0:
                inq = inq[0].replace('。', '')
                data.append(inq)
            else:
                data.append(' ')
            bd = re.findall(findBd, items)[0]
            bd = re.sub('<br/>(\s+)?', ' ', bd)  # 去掉<br/>，(\s+)?表示可能存在的空格
            bd = re.sub('/', '', bd)
            bd = re.sub('\s\s+', ' ', bd)
            data.append(bd.strip())
            datalist.append(data)
    return datalist


# 保存数据（excel）

def savedata(datalist,savepath):
    book = xlwt.Workbook(encoding='utf-8', style_compression=0)
    sheet = book.add_sheet('top250', cell_overwrite_ok=True)
    col=('电影链接','图片链接','中文名','外国名','评分','评价数','概况','相关信息')
    sheet.col(7).width = 30000
    for i in range(0,8):
        sheet.write(0,i,col[i])
    for i in range(0,250):
        data = datalist[i]
        for j in range(0,8):
            sheet.write(i+1,j,data[j])
    book.save(savepath)


# SQL初始化数据

def init_db(path):
    sql = '''
    create table movie
	(id integer primary key autoincrement,
	info_link text,
	pic_link text,
	cname varchar,
	ename varchar,
	score numeric,
	rated numeric,
	instroduction text,
	info text)
    '''
    con = sqlite3.connect(path)
    cursor = con.cursor()
    cursor.execute(sql)
    con.commit()
    con.close()


# 保存数据（SQL）

def savedb(datalist,path):
    if not os.path.exists('database/top250.db'):
        init_db(path)
    con = sqlite3.connect(path)
    cur = con.cursor()
    for data in datalist:
        for idx in range(len(data)):
            if idx==4 or idx==5:
                continue
            data[idx] = repr(data[idx])
        sql='''
        insert into movie (info_link, pic_link, cname, ename, score, rated, instroduction, info)
        values (%s)
        '''%','.join(data)
        cur.execute(sql)
        con.commit()
    cur.close()
    con.close()


if __name__ == '__main__':

    datalist = getData(baseurl)
    savedata(datalist, savepath)
    savedb(datalist, dbPath)
    end=time.perf_counter()
    print('Runtime: ', end-start)
