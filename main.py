import json
import sqlite3
import bs4
import requests





class zimuzu():
    def getserch(self, name):
        # 影片名精确查找

        ret = requests.get(
            'http://www.zimuzu.tv/search?keyword=%s&type=resource' % (name))
        beautiful = bs4.BeautifulSoup(ret.text, 'html.parser')
        return beautiful.find(class_="t f14")

    def getpage(self):
        # 获取影片总页数
        text = requests.get(
            'http://www.zimuzu.tv/resourcelist/?page=1&channel=tv&area=%E7%BE%8E%E5%9B%BD&category=&year=&tvstation=&sort=').text
        beautiful = bs4.BeautifulSoup(text, 'html.parser')
        bs_page = beautiful.find(class_="pages").find_all('a')
        page = bs_page[-1].get_text()
        return int(page.replace('.', ''))

    def getmeiju(self, page=1):
        # 获取某一页数的所有影视
        url = 'http://www.zimuzu.tv/resourcelist/?page=xwkxwk&channel=tv&area=%E7%BE%8E%E5%9B%BD&category=&year=&tvstation=&sort='.replace(
            'xwkxwk', str(page))
        text = requests.get(url).text
        beautiful = bs4.BeautifulSoup(text, 'html.parser')
        dict = {}
        for x in beautiful.find_all('h3'):
            dict.update({x.a.get_text(): int(x.a['href'][10:])})
        return dict

    def geturl(self, code):
        # 通过code获取影片下载链接页面url
        ret = requests.get(
            'http://www.zimuzu.tv/resource/index_json/rid/%s/channel/tv' % code)
        txt = ret.text.replace('var index_info=', '')
        json_url = json.loads(txt)
        soup = bs4.BeautifulSoup(json_url['resource_content'], 'html.parser')
        return soup.find('a')['href']

    def getmag(self, url):
        # 获取影片下载链接页面下载地址
        ret = requests.get(url)
        soup = bs4.BeautifulSoup(ret.text, 'html.parser')
        import re
        list = []
        for x in soup.find_all(
                attrs={'id': re.compile(r'tab-g\d{1,3}-MP4|tab-g\d{1,3}-HR-HDTV|tab-g\d{1,3}-WEB-720P')}):
            for y in x.find_all(attrs={'itemid': re.compile(r'\d{0,6}')}):
                megurl = ''
                for x in y.find_all(class_='btn'):
                    if 'thunder' in str(x):
                        megurl = x['href']

                try:
                    episode = y.find(class_="episode").text.replace(' ', '-')
                    list.append({'filesize': y.find(class_="filesize").text,
                                 'file': y.find(class_="filename").text,
                                 'episode': episode,
                                 'url': megurl})
                except:
                    list.append({'filesize': y.find(class_="filesize").text,
                                 'file': y.find(class_="filename").text,
                                 'url': megurl})

        return list


def geturl(meiju, seson, leve):
    conn = sqlite3.connect('meiju.db')
    con = conn.execute(
        "SELECT url FROM %s WHERE episode>='第%d季-第%d集'" % (meiju, seson, leve))
    for x in con.fetchall():
        print(x[0])


def update(movie):
    copybord = ''

    for x in movie:
        code = zimuzu().getserch(x).a['href'].replace('/resource/', '')
        url = zimuzu().geturl(code)
        js = zimuzu().getmag(url)
        # print(js)

        try:
            with sqlite3.connect('meiju.db') as conn:
                conn.execute(
                    'CREATE TABLE %s (episode PRIMARY KEY,file,url,filesize);' % (x))
            print('新增美剧:' + x)
        except:
            import time
        for o in range(0, len(js)):
            try:
                with sqlite3.connect('meiju.db') as conn:
                    conn.execute("INSERT INTO %s VALUES('%s','%s','%s','%s');" % (
                        x, js[o]['episode'], js[o]['file'], js[o]['url'], js[o]['filesize']))
                    conn.commit()
                print(js[o]['url'])
                copybord = copybord + js[o]['url'] + '\n'
            except:
                import time
        print('结束:%s有%d' % (x, len(js)))
    import pyperclip
    pyperclip.copy(copybord)



def getall():
    zimuzu().getpage()
    for x in range(0, zimuzu().getpage()):

        import sqlite3

        meiju_dict = zimuzu().getmeiju(page=x)
        print(meiju_dict)
        for y in meiju_dict:
            try:
                with sqlite3.connect('code.db') as conn:

                    conn.execute("INSERT INTO code VALUES (%d,'%s');" %
                                 (meiju_dict[y], y))

                    conn.commit()
            except:
                import time


def getallmovie():
    concode = sqlite3.connect('code.db')
    conncode = concode.execute('SELECT * FROM code')
    dict1 = conncode.fetchall()

    conncode.close()
    r = 0

    for x in dict1[400:]:
        r = r + 1
        print('当前操作%s代码为%d位置为%d' % (x[1], x[0], r))

        try:

            conn = sqlite3.connect('AllMeiju.db')
            conn.execute(
                "CREATE TABLE '%d' (episode PRIMARY KEY,file,url,filesize);" % (x[0]))
            conn.close()
            print('新增美剧:' + x[1])
        except:
            print('%s创建失败' % (x[1]))
        movie_dict = zimuzu().getmag(zimuzu().geturl(x[0]))
        # 736+400

        for o in range(0, len(movie_dict)):
            try:
                conn = sqlite3.connect('AllMeiju.db')
                conn.execute("INSERT INTO '%d' VALUES('%s','%s','%s','%s');" % (
                    x[0], movie_dict[o]['episode'], movie_dict[o]['file'], movie_dict[o]['url'],
                    movie_dict[o]['filesize']))
                conn.commit()
                conn.close()
                # print('成功!!!!!%s---%s' % (movie_dict[o]['file'], movie_dict[o]['url']))
            except:

                print('失败!!!!%s---%s' %
                      (movie_dict[o]['file'], movie_dict[o]['url']))

        print('结束:%s有%d====%d' % (x[1], len(movie_dict), x[0]))


if __name__ == '__main__':
    # geturl('怪奇物语',1,1)
    #sqlite3.connect('sql.db')
    update(['闪电侠','神盾局特工','少年谢尔顿','氪星'])


    import tushare

    # print(zimuzu().getmeiju(page=7))


    # getallmovie()

    # getall()
    # print(zimuzu().getmag(zimuzu().geturl('33266')))
