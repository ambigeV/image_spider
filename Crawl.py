import random
import requests
import re
import lxml
from lxml import etree
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import base64
from binascii import b2a_hex
import time
import rsa
import codecs
import csv
import datetime
import urllib
from pathlib import Path
import os
import numpy as np
import pandas as pd
import multiprocessing as mp

# Set Headers
headers = {'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 "
                         "(KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
           'Referer': 'https://www.mzitu.com/'}
# Set Root Path
root_path = "D:\Lisayang\mzitu"
# Set Url of Website
url = 'https://www.mzitu.com'
# Retry
requests.adapters.DEFAULT_RETRIES = 20

def get_worker(url, header=headers):
    """
    To enable a flexible get action, derive a function to 
    do that
    :param url: url 
    :param header: headers
    :return: return a response
    """
    trytimes = 5
    s = requests.session()
    for i in range(trytimes):
        if i == 4:
            time.sleep(5)
        try:
            s.keep_alive = False
            #ss = requests.get(
            #    "http://api.xdaili.cn/xdaili-api//greatRecharge/getGreatIp?"
            #    + "spiderId=2762edd6bf774c259c19282b80276ee2&"
            #    + "orderno=YZ2020341824jBoEWe&returnType=1&count=20")
            #proxy_list = ss.text.replace('\n', "").split('\r')[:-1]

            proxy_list = [
                'rn6sgthtk1' + ':' + 'tth6sozejq' + '@58.221.67.111:23128',
                'f26xjbegaj' + ':' + '48u17zdemy' + '@47.92.132.197:23128',
                'bw18zueu6p' + ':' + 'fnmht2zpt3' + '@47.104.79.229:23128',
                'kldxbohr8i' + ':' + 'j17owluzst' + '@103.45.149.215:23128',
                'gxzui9yss4' + ':' + 'stattee1vj' + '@139.224.228.184:23128',
                'ljrdhcgfvn' + ':' + 'husspuqfjm' + '@115.159.115.30:23128',
                'trv9ku0ehc' + ':' + '1whzchn8jb' + '@123.206.75.195:23128',
                'hdm23dyvsq' + ':' + 'nezdn9mz5b' + '@123.207.170.170:23128'
            ]
            if(len(proxy_list)==8):
                a = random.randint(0, 7)
                b = (a + random.randint(1, 7)) % 8

                s.proxies = {"http": "http://" + proxy_list[a],
                             "https": "https://" + proxy_list[b],
                        }
            else:
                pass

            s.headers = header
            r = s.get(url, proxies=s.proxies, headers=header, timeout=20)
            #print(r.status_code)
            if r.status_code == 200:
                break;
        except:
            print('Request Has Failed')
    return r


def travel_topic(travel_url="https://www.mzitu.com/zhuanti"):
    """
    This function would traverse the topics of the mzitu.com
    and return a list of dictionaries as well as a .csv file.
    The csv file can inform you of the indexing tag of the
    corresponding model.
    :param travel_url: the tag address.
    :return: A list of dictionaries including name, size, and
    the according tag.
    """

    travel_res = get_worker(travel_url, header=headers)
    travel_xp = etree.HTML(travel_res.text)
    items = []

    for item in travel_xp.xpath('//div[@class="postlist"]//dd'):
        link = str(item.xpath('a/@href')).split('/')[-2]
        name = item.xpath('a//text()')[0]

        my_size = str(item.xpath('i/text()'))
        my_size = re.search(r'[0-9]+', my_size).group()

        items.append({
            "link": link,
            "size": my_size,
            "name": name
        })

    file_name = root_path + "\mzitu_index.csv"
    with open(file_name, 'a', newline='', encoding='utf-8-sig') as f:
        f_csv = csv.writer(f)
        for j in items:
            f_csv.writerow(list(j.values()))

    print(items)
    return items


def crawl_image(current='196664', url="https://www.mzitu.com/", speed=0.5):
    """
    This function would crawl all the images under an
    image album in mzitu.com.
    :param current: current is the album number of ...
    mzitu.com
    :param url: url is the url of the mzitu.com, this
    can be omitted if you apply it to a class.
    :param speed: speed is to control the crawling speed
    :return: None
    """
    # Create Dir
    root_path = os.getcwd()
    image_path = root_path + '/' + current + '/'

    if os.path.exists(image_path):
        return
    else:
        os.mkdir(image_path)

    # Get Image URL
    current_url = url + current
    image_res = get_worker(current_url, header=headers)

    # Resolve Image Resource
    image_soup = BeautifulSoup(image_res.text, 'lxml')
    number = image_soup.find('div', class_='pagenavi').find_all('span')[-2].get_text()
    print(number)

    # Get All SRC
    for i in range(eval(number)):
        num = str(i + 1)
        image_url = current_url + '/' + num
        image_res = get_worker(image_url, header=headers)
        image_tree = etree.HTML(image_res.text)
        src_url = image_tree.xpath('//div[@class="main-image"]//a/img/@src')[0]
        src_res = get_worker(src_url, header=headers)
        # Download the JPG File
        final_image_path = image_path + num + '.png'
        with open(final_image_path, 'wb') as f:
            f.write(src_res.content)
        time.sleep(speed)


def crawl_topic(param={'name':'wangyuchun', 'speed':0.5}, url='https://www.mzitu.com', root='D:\Lisayang\mzitu'):
    """
    This function would crawl a topic of images based
    on the tag name which can be found in function ""
    travel topic"".
    :param param: the name and the speed
    :param url: url name
    :param root: root_path of you working environment
    :return: None
    """
    # Decouple the parameters
    name = param['name']
    speed = param['speed']

    # Ready for Dir
    os.chdir(root)
    root_path = os.getcwd()
    image_path = root_path + '/' + name + '/'

    if os.path.exists(image_path):
        pass
    else:
        os.mkdir(image_path)

    os.chdir(image_path)
    print(os.getcwd())

    # Ready for Xpath
    new_url = url + '/tag/' + name + '/'
    new_html = get_worker(new_url, header=headers)
    soup_html = BeautifulSoup(new_html.text, 'lxml')
    some = soup_html.find('div', class_='nav-links').get_text()
    if some == "":
        number = 1
        print(number)
    else:
        number = soup_html.find('div', class_='nav-links').find_all('a')[-2].get_text()
        number = eval(number)
        print(number)

    # Crawl ALL Pages
    for i in range(number):
        page = i + 1
        page_url = new_url + 'page/' + str(page)
        page_html = get_worker(page_url, header=headers)
        sel_html = etree.HTML(page_html.text)
        # List ALL INDEXES
        for sel in sel_html.xpath('//*[@id="pins"]/li'):
            href = (sel.xpath('./a/@href'))[0]

            # Set Index
            image_index = href.split('/')[-1]

            # Crawl Images by Index
            crawl_image(image_index, speed=speed)


if __name__ == '__main__':
    """
    for item in travel_topic():
        print(item['link'])
        crawl_topic(item['link'], url, root_path)
    """
    #crawl_topic("xuweiwei_mia", speed=1)
    topics = pd.read_csv(root_path + "\mzitu_index.csv", header=None)
    pool = mp.Pool(processes=8)
    #print(topics[0])

    for i in topics[0]:
        pool.apply_async(crawl_topic, ({'name': i, 'speed': 0.75},))
        #crawl_topic(i, speed=0.3)

    print("The main's mark")
    pool.close()
    pool.join()
    print("All's done!")
