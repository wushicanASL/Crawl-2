#coding=UTF-8
import os
import urllib
import argparse
import requests
from MyThread import MyThread
from urllib import request
from bs4 import BeautifulSoup


def get_html(url_address):
    """
    通过url_address得到网页内容
    :param url_address:请求的网页地址
    :return :html
    """
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
    req = urllib.request.Request(url=url_address,headers=headers)
    return urllib.request.urlopen(req)


def get_soup(html):
    """
    把网页内容封装到BeautifulSoup中并返回BeautifulSoup对象
    :param: html:网页内容
    :return :BeautifulSoup Object
    """
    if html == None:
        return
    return BeautifulSoup(html.read(),'html.parser')


def get_img_dirs(soup):
    """
    获取所有相册的标题和链接
    :param :soup:BeautifulSoup 实例
    :return 字典{key:标题，value:内容}
    """

    if soup == None:
        return
    lis = soup.find(id="pins").findAll(name='li')
    if lis!=None:
        img_dirs={};
        for li in lis:
            links=li.find('a')
            title=links.find('img').attrs['alt']
            t = links.attrs['href']
            img_dirs[title]=t
        print(img_dirs)
        return img_dirs
    return None

def save_file(d,filename,img_url):
    """
    保存图片文件
    :param d:文件路径 filename:文件名 img_url:图片地址
    """
    print(img_url+"=========")
    img = requests.get(img_url)
    name = str(d+"/"+filename)
    with open(name,'wb') as f:
        f.write(img.content)

def download_img_from_page(title,page_url):
    dir_html = get_html(page_url)
    dir_soup = get_soup(dir_html)

    #获取当前图片
    main_image= dir_soup.findAll(name='div',attrs={'class':'main-image'})
    if main_image !=None:
        for image_parent in main_image:
            imgs = image_parent.findAll(name='img')
            if imgs!=None:
                img_url=str(imgs[0].attrs['src'])
                filename=img_url.split('/')[-1]
                print('开始下载：'+img_url+",保存为:"+filename)
                save_file(title,filename,img_url)

def download_imgs(info):
    """
    下载整个图册
    """
    if info ==None:
        return

    title=info[0]
    link = info[1]

    if title==None or link ==None:
        return

    print("创建图册:"+title+" "+link)
    try:
        os.mkdir(title)
    except Exception as e:
        print("文件夹"+title+"已存在")


    print("开始获取相册《"+title+"》内，图片的数量")

    dir_html=get_html(link)
    dir_soup=get_soup(dir_html)
    img_page_num = get_dir_img_page_num(link, dir_soup)

    for n in range(img_page_num):
        download_img_from_page(title,link+'/'+str(n+1))


def get_dir_img_page_num(l, dir_soup):
    """
    获取相册里面的图片数量
    :param l:相册链接地址
    :param dir_soup:BeautifulSoup对象
    :return :相册图片数量
    """

    divs = dir_soup.findAll(name='div',attrs={'class':'pagenavi'})
    navi = divs[0]

    links = navi.findAll(name='a')
    if links == None:
        return

    a=[]
    url_link =[]
    lk=str(links[-2]['href'])
    num=int(lk.split('/')[-1])
    return num

def get_full_page_num(l,dir_soup):

    divs = dir_soup.findAll(name='div',attrs={'class':'nav-links'})
    navi=divs[0]

    links = navi.findAll(name='a')
    if links==None:
        return
    lk=str(links[-2]['href'])
    num=int(lk.split('/')[-1])
    return num

def main_test(url):
    html=get_html(url)
    soup = get_soup(html)
    img_dirs = get_img_dirs(soup)
    if img_dirs ==None:
        print("无法获取该页面下的图册内容...")

    else:
        for d in img_dirs:
            my_thread = MyThread(download_imgs,(d,img_dirs.get(d)))
            my_thread.start()
            my_thread.join()

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("echo")

    args = parser.parse_args()
    url = str(args.echo)
    print("开始解析："+url)

    html=get_html(url)
    soup = get_soup(html)
    num=get_full_page_num(html,soup)

    for i in range(num):
        main_test(url+'/page/'+str(i+1))

            
