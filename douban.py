import requests
from lxml import html
import os
import time

__author__ = 'dh_liu'


# 用log函数把所有输出写入到文件
def log(*args, **kwargs):
    t = '%Y/%m/%d %H:%M:%S'
    value = time.localtime(int(time.time()))
    dt = time.strftime(t, value)
    # 中文windows平台默认打开的文件编码是gbk所以需要指定一下
    with open('log.gua.txt', 'a', encoding='utf-8') as f:
        # 通过file参数可以把输出写入到文件f中
        print(dt, *args, file=f, **kwargs)


class Model(object):
    def __repr__(self):
        class_name = self.__class__.__name__
        properties = ('{} = ({})'.format(k, v) for k, v in self.__dict__.items())
        r = '\n<{}:\n {}\n>'.format(class_name, '\n '.join(properties))
        return r


# 定义电影类
class Movie(Model):
    def __init__(self):
        self.name = ''
        self.score = 0
        self.quote = ''
        self.cover_url = ''
        self.rank = 0


# 下载爬取网页的页面数据, 并保存为 html 格式
def cached_url(url):
    filename = url.split('=')[-1] + '.html'
    path = os.path.join('cache', filename)
    # 避免重复下载
    if os.path.exists(path):
        with open(path, 'rb') as f:
            return f.read()
    else:
        r = requests.get(url)
        with open(path, 'wb') as f:
            f.write(r.content)
    return r.content


# 下载电影封面
def download_img(url, name):
    filename = name
    path = os.path.join('image', filename)
    # 避免重复下载
    if not os.path.exists(path):
        r = requests.get(url)
        with open(path, 'wb') as f:
            f.write(r.content)


# save 数据
def save(movies):
    for m in movies:
        download_img(m.cover_url, m.name + 'jpg')


# 获取电影大div中的要爬取的元素
def movie_from_div(div):
    movie = Movie()
    movie.name = div.xpath('.//span[@class="title"]')[0].text
    movie.score = div.xpath('.//span[@class="rating_num"]')[0].text
    try:
        movie.quote = div.xpath('.//span[@class="inq"]')[0].text
    except IndexError as e:
        movie.quote = '消失的爱人竟然没有引用'
    img_url = div.xpath('//div[@class="pic"]/a/img/@src')[0]
    movie.cover_url = img_url
    movie.rank = div.xpath('.//div[@class="pic"]/em')[0].text
    return movie


# 解析单个电影的所有数据(在一个 div 标签中)
def movies_from_url(url):
    # 下载页面
    page = cached_url(url)
    # 下载页面是一个 html 文件, 用函数解析一下, 方便之后进行查找
    root = html.fromstring(page)
    movie_divs = root.xpath('//div[@class="item"]')
    movies = []
    for div in movie_divs:
        movie = movie_from_div(div)
        movies.append(movie)
    return movies


def main():
    for i in range(0, 250, 25):
        url = 'https://movie.douban.com/top250?start={}'.format(i)
        movies = movies_from_url(url)
        log(movies)
        save(movies)


if __name__ == '__main__':
    main()
