import os
import requests
import re
import threading
import time
import multiprocessing
from retrying import retry


@retry(stop_max_attempt_number=5)
def download(img_url, title, i):
    # 图片下载
    time.sleep(1)
    img_data = requests.get(img_url, timeout=60)
    with open('./美女图片爬取结果/{}/{}.jpg'.format(title, i), 'wb') as file:
        file.write(img_data.content)
    print("{}成功下载一张mm.jpg".format(i))


@retry(stop_max_attempt_number=5)
def get_img_url(content_link, title, i):
    # 获取当前套图的所有内容页中的图片地址
    # https://www.lhjb.net/meinv/5994/ + i + '.html'
    page_link = content_link + '{}'.format(i) + '.html'
    # try:
    time.sleep(1)
    res = requests.get(page_link, timeout=60)
    content_re = re.findall(r'<a href=".*"><img alt=".*" src="(.*)" /></a></span>', res.text)
    # 拼接完整图片地址
    if not content_re:
        return
    img_url = 'https://www.lhjb.net' + content_re[0]
    download(img_url, title, i)


@retry(stop_max_attempt_number=5)
def get_link(p):
    headers = {'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3'}
    # 访问列表页，获取所有内容页链接
    # 下载网页代码
    # try:
    time.sleep(1)
    raw_req = requests.get('https://www.lhjb.net/xinggan/{}.html'.format(p), headers=headers, timeout=60)
    html = raw_req.text
    cate_re = re.findall(r'<a href="(.*)" class="dl-pic"><img class="scrollLoading" width="197px" height="263px" src=".*" alt="(.*)"></a>', html)
    for content_link, title in cate_re:
        # 拼接完整内容页地址
        content_link = 'https://www.lhjb.net' + content_link
        # 访问内容页
        print(content_link)
        # https://www.lhjb.net/meinv/5994/
        try:
            time.sleep(1)
            raw_req = requests.get(content_link, timeout=60)
        except requests.exceptions.ConnectionError:
            continue
        # https://www.lhjb.net/meinv/5994/1.html
        thread_html = raw_req.text
        # 获取内容页地址的页数,通过这里，可以知道一个主体一共有多少个内容页面
        content_re_f = re.findall(r'</a><span class=\"current\">.*共(\d*)张</span>', thread_html)
        page = content_re_f[0]
        if title in os.listdir('./美女图片爬取结果'):
            print("已存在该套图，继续下一个")
            continue
        os.mkdir('./美女图片爬取结果/{}'.format(title))
        for i in range(1, int(page)+1):
            # 遍历所有内容页面，得到内容页面的图片地址
            get_img_url_thread = threading.Thread(target=get_img_url, args=(content_link, title, i))
            get_img_url_thread.start()
            time.sleep(3)


if __name__ == '__main__':
    pool = multiprocessing.Pool(15)
    for i in range(1, 352):
        pool.apply_async(get_link, args=(i,))
    pool.close()
    pool.join()