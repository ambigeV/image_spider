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

# Set Headers
headers = {'User-Agent':"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 "
                        "(KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
           'Referer':'http://www.mzitu.com/'}
# Set Root Path
root_path = "D:\Lisayang\mzitu"
# Set Url of Website
url = 'http://www.mzitu.com'


def travel_topic(travel_url="http://www.mzitu.com/zhuanti"):
    """
    This function would traverse the topics of the mzitu.com
    and return a list of dictionaries as well as a .csv file.
    The csv file can inform you of the indexing tag of the
    corresponding model.
    :param travel_url: the tag address.
    :return: A list of dictionaries including name, size, and
    the according tag.
    """

    travel_res = requests.get(travel_url, headers=headers)
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


def crawl_image(current='196664', url="https://www.mzitu.com/"):
    """
    This function would crawl all the images under an
    image album in mzitu.com.
    :param current: current is the album number of ...
    mzitu.com
    :param url: url is the url of the mzitu.com, this
    can be omitted if you apply it to a class.
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
    image_res = requests.get(current_url, headers=headers)

    # Resolve Image Resource
    image_soup = BeautifulSoup(image_res.text, 'lxml')
    number = image_soup.find('div', class_='pagenavi').find_all('span')[-2].get_text()
    print(number)

    # Get All SRC
    for i in range(eval(number)):
        num = str(i + 1)
        image_url = current_url + '/' + num
        image_res = requests.get(image_url, headers=headers)
        image_tree = etree.HTML(image_res.text)
        src_url = image_tree.xpath('//div[@class="main-image"]//a/img/@src')[0]
        src_res = requests.get(src_url, headers=headers)
        # Download the JPG File
        final_image_path = image_path + num + '.png'
        with open(final_image_path, 'wb') as f:
            f.write(src_res.content)
        time.sleep(0.7)


def crawl_topic(name='wangyuchun', url='http://www.mzitu.com', root='D:\Lisayang\mzitu'):
    """
    This function would crawl a topic of images based
    on the tag name which can be found in function ""
    travel topic"".
    :param name: the tag name
    :param url: url name
    :param root: root_path of you working environment
    :return: None
    """
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
    new_html = requests.get(new_url, headers=headers)
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
        page_html = requests.get(page_url, headers=headers)
        sel_html = etree.HTML(page_html.text)
        # List ALL INDEXES
        for sel in sel_html.xpath('//*[@id="pins"]/li'):
            href = (sel.xpath('./a/@href'))[0]

            # Set Index
            image_index = href.split('/')[-1]

            # Crawl Images by Index
            crawl_image(image_index)


if __name__ == '__main__':
    for item in travel_topic():
        print(item['link'])
        crawl_topic(item['link'], url, root_path)


