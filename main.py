#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# import libs
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
import lxml
import json
import time
import math
import sys
import random

# global param
ua = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
        "Mozilla/5.0 (Windows; U; Windows NT 5.2) Gecko/2008070208 Firefox/3.0.1"
        "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
        "Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
        "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11",
        "Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E)",
        "Opera/9.80 (Windows NT 5.1; U; zh-cn) Presto/2.9.168 Version/11.50",
        "Mozilla/5.0 (Windows NT 5.1; rv:5.0) Gecko/20100101 Firefox/5.0",
        "Mozilla/5.0 (Windows NT 5.2) AppleWebKit/534.30 (KHTML, like Gecko) Chrome/12.0.742.122 Safari/534.30",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.11 TaoBrowser/2.0 Safari/536.11",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71 Safari/537.1 LBBROWSER",
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; LBBROWSER)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SV1; QQDownload 732; .NET4.0C; .NET4.0E; 360SE)",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.84 Safari/535.11 SE 2.X MetaSr 1.0",
        "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.2)",
        "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)",
        "Mozilla/4.0 (compatible; MSIE 5.0; Windows NT)",
        "Mozilla/5.0 (Windows; U; Windows NT 5.2) Gecko/2008070208 Firefox/3.0.1",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1) Gecko/20070309 Firefox/2.0.0.3",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1) Gecko/20070803 Firefox/1.5.0.12 "
    ]

DEBUG_URL = "./tools.html"
BASE_URL = "https://www.bunnings.com.au"
START_URL = BASE_URL + "/our-range"

DEBUG_MODE = True

global SeleniumDriver
global ItemsPerPage

# 产品列表页面每页显示的产品数
# 默认是 48
ItemsPerPage = 48

# debug print
# print line without CRLF
def debug_print(*params):
    if DEBUG_MODE :
        for s in params:
            print(s, end='')
    else:
        pass
    return


# print with new line
def debug_printline(*params):
    if DEBUG_MODE:
        for s in params:
            print(s, end='')
        print('')
    else:
        pass
    return


# debug exit with error code/msg
def debug_exit(msg):
    if DEBUG_MODE:
        sys.exit(msg)
    else:
        pass
    return


# debug level
def debug_level(level):
    breadcrumble = ["/our-range",                                                   # 一级页面 - 产品总体分类
                    "/our-range/tools",                                             # 二级页面 -
                    "/our-range/tools/power-tools",                                 # 三级页面 - 三级、四级页面结构一样
                    "/our-range/tools/power-tools/drills",                          # 四级页面 -
                    "our-range/tools/power-tools/drills/cordless-drill-skins",      # 五级页面 - 产品列表
                    "items"                                                         # 六级页面 - 产品详细信息
                   ]
    debug_printline("**** DEBUG LEVEL: ", breadcrumble[level])
    return


# get remote webpage for parsing
# 加载页面
# 适用于一级~五级页面

def load_remote_url(url):
    # load remote file
    time.sleep(1)
    with requests.request('GET', url, headers={'User-agent': random.choice(ua)}) as webpage:
        content = webpage.text
        soup = BeautifulSoup(content, 'lxml')
    return soup


# get remote webpage for parsing
# 使用 selenium 加载页面
# 适用于五级页面

def browser_load_remote_url(url):
    global SeleniumDriver
    # firefox = FirefoxBinary("/usr/bin/firefox")
    SeleniumDriver = webdriver.Firefox()
    # 设置隐性等待时间，最长等待 30 秒
    SeleniumDriver.implicitly_wait(30)
    SeleniumDriver.get(url)
    soup = BeautifulSoup(SeleniumDriver.page_source, 'lxml')
    return soup


# close selenium
# 关闭 selenium 打开的浏览器窗口

def browser_close():
    global SeleniumDriver
    SeleniumDriver.close()
    return


# save product details to file
# 保存产品信息

def save_product_to_file(p_url, p_id, description, price_dollars, price_cents, img):
    '''
    根据 url 创建文件夹和文件名
    ie. /our-range
        ../tools
          ../power-tools
            ../drills
              ../cordless-power-drills
                ../Makita LXT 18V Brushless Cordless Impact Driver - Skin Only.csv
    :param p_url:
    :param p_id:
    :param description:
    :param price_dollars:
    :param price_cents:
    :param img:
    :return:
    '''
    pass


# parse our-range
# 爬取总体分类页面

def parse_our_range(url):
    # INPUT:
    # URL = BASE_URL + /our-range/
    # OUTPUT:
    # URL = BASE_URL + /our-range/tools
    #                          ../...

    # debug print
    debug_printline("**** parse_our_range ****")
    debug_printline(url)
    debug_level(0)

    soup = load_remote_url(url)

    tags_div = soup.find_all('div', 'chalkboard-module-dropdown')
    for tag_div in tags_div:
        tag_a = tag_div.find('a', 'chalkboard-header')
        tag_a_name = tag_a.get_text()
        tag_a_url = BASE_URL + tag_a.get('href')
        # debug print
        debug_printline(tag_a_name)
        debug_printline(tag_a_url)

        # parse each category
        tags_li = tag_div.find('ul', 'chalkboard-menu').find_all('li')
        for tag_li in tags_li:
            tag_li_name = tag_li.get_text()
            # tag_li_url is invalid, so not parsing
            # tag_li_url = tag_li.get('href')
            debug_printline(tag_li_name)
        # parse main categories
        parse_main_categories(tag_a_url)

    # debug print
    debug_exit("**** finished! ****")
    return


# parse main categories

def parse_main_categories(url):
    # INPUT:
    # URL = BASE_URL + /our-range/tools
    #                          ../...
    # OUTPUT:
    # URL = BASE_URL + /our-range/tools/power-tools
    #                                ../...

    # debug print
    debug_printline("**** parse_main_categories ****")
    debug_printline(url)
    debug_level(1)

    soup = load_remote_url(url)

    categories = soup.find_all('div', class_='inside-layout', attrs={"datav3-module-name": "RangeCategories"})
    if categories is not None:
        for cat in categories:
            tag_div = cat.find('div', 'category-block-heading')
            tag_a = tag_div.find('a', 'category-block-heading__title')
            # category title
            cat_name = tag_a.find('h2', 'category-block-heading__text').get_text()
            cat_url = BASE_URL + tag_a.get('href')
            # categories count
            cat_count = int(tag_a.find('span', 'category-block-heading__count').get_text())
            # debug print
            debug_printline(cat_name)
            debug_printline(cat_url)
            debug_printline(cat_count)

            # parse sub categories
            parse_sub_categories(cat_url)
    else:
        debug_printline(url)
        debug_exit("WARNING: parse_main_categories | categories is None")
    return


# parse sub categories
# 爬取子分类

def parse_sub_categories(url):
    # INPUT:
    # URL = BASE_URL + /our-range/tools/power-tools
    #                                ../...
    # OUTPUT:
    # URL = BASE_URL + /our-range/tools/power-tools/drills
    #                                            ../...

    # debug print
    debug_printline('**** parse_sub_categories ****')
    debug_printline(url)
    debug_level(2)

    soup = load_remote_url(url)

    tag_div_container = soup.find('div', class_='content-layout_inside', attrs={"id":"content-layout_inside-anchor"})
    if tag_div_container is not None:
        tags_div = tag_div_container.find_all('div', 'inside-layout')
        if tags_div is not None:
            for tag_div in tags_div:
                tag_ul = tag_div.find('ul', 'not-list')
                if tag_ul is not None:
                    tag_li = tag_ul.find('li', 'sidebar-dropdown-nav')
                    if tag_li is not None:
                        tag_li_ul = tag_li.find('ul')
                        if tag_li_ul is not None:
                            tags_li_ul_li = tag_li_ul.find_all('li')
                            if tags_li_ul_li is not None:
                                for tag_li_ul_li in tags_li_ul_li:
                                    tag_a = tag_li_ul_li.find('a')
                                    tag_a_name = tag_a.get_text()
                                    tag_a_url = BASE_URL + tag_a.get('href')
                                    # debug print
                                    debug_printline(tag_a_name)
                                    debug_printline(tag_a_url)
                                    # parse sub categories
                                    # 爬取子分类
                                    # 页面结构和算法和本方法相同
                                    # 考虑转成递归函数
                                    parse_sub1_categories(tag_a_url)
                            else:
                                debug_printline(url)
                                debug_exit("WARNING: parse_sub_categories | tags_li_ul_li is None")
                        else:
                            debug_printline(url)
                            debug_exit("WARNING: parse_sub_categories | tag_li_ul is None")
                    else:
                        debug_printline(url)
                        debug_exit("WARNING: parse_sub_categories | tags_li is None")
                else:
                    debug_printline(url)
                    debug_exit("WARNING: parse_sub_categories | tag_ul is None")
        else:
            debug_printline(url)
            debug_exit("WARNING: parse_sub_categories | tag_div is None")
    else:
        debug_printline(url)
        debug_exit("WARNING: parse_sub_categories | tag_div_container is None")
    return


# parse sub categories
# 爬取子分类
# 和上一级页面结构和算法相同

def parse_sub1_categories(url):
    # INPUT:
    # URL = BASE_URL + /our-range/tools/power-tools/drills
    #                                            ../...
    # OUTPUT:
    # URL = BASE_URL + /our-range/tools/power-tools/drills/cordless-drill-skins
    #                                                   ../...

    # debug print
    debug_printline('**** parse_sub1_categories ****')
    debug_printline(url)
    debug_level(3)

    soup = load_remote_url(url)

    tag_div_container = soup.find('div', class_='content-layout_inside', attrs={"id":"content-layout_inside-anchor"})
    if tag_div_container is not None:
        tags_div = tag_div_container.find_all('div', 'inside-layout')
        if tags_div is not None:
            for tag_div in tags_div:
                tag_ul = tag_div.find('ul', 'not-list')
                if tag_ul is not None:
                    tag_li = tag_ul.find('li', 'sidebar-dropdown-nav')
                    if tag_li is not None:
                        tag_li_ul = tag_li.find('ul')
                        if tag_li_ul is not None:
                            tags_li_ul_li = tag_li_ul.find_all('li')
                            if tags_li_ul_li is not None:
                                for tag_li_ul_li in tags_li_ul_li:
                                    tag_a = tag_li_ul_li.find('a')
                                    tag_a_name = tag_a.get_text()
                                    tag_a_url = BASE_URL + tag_a.get('href')
                                    # debug print
                                    debug_printline(tag_a_name)
                                    debug_printline(tag_a_url)

                                    # parse sub categories
                                    parse_product_list(tag_a_url)
                            else:
                                debug_printline(url)
                                debug_exit("WARNING: parse_sub1_categories | tags_li_ul_li is None")
                        else:
                            debug_printline(url)
                            debug_exit("WARNING: parse_sub1_categories | tag_li_ul is None")
                    else:
                        debug_printline(url)
                        debug_exit("WARNING: parse_sub1_categories | tags_li is None")
                else:
                    debug_printline(url)
                    debug_exit("WARNING: parse_sub1_categories | tag_ul is None")
        else:
            debug_printline(url)
            debug_exit("WARNING: parse_sub1_categories | tags_div is None")
    else:
        debug_printline(url)
        debug_exit("WARNING: parse_sub_categories | tag_div_container is None")
    return


# parse sub categories
# 爬取产品列表页面

def parse_product_list(url):
    # INPUT:
    # URL = BASE_URL + /our-range/tools/power-tools/drills/cordless-drill-skins
    #                                                   ../...
    # OUTPUT:
    # URL = https://www.bunnings.com.au/makita-lxt-18v-brushless-cordless-impact-driver-skin-only_p6240412
    #                                ../...

    # debug print
    debug_printline('**** parse_product_list ****')
    debug_printline(url)
    debug_level(4)

    soup = load_remote_url(url)

    tag_div_container = soup.find('div', class_='product-list-group paged-items')

    if tag_div_container is not None:
        # this is the product list page
        # find products total counts first, default count/page is 48
        tag_label = soup.find('label', class_="left-sidebar_checkbox_btn", attrs={"for": "fulfillment-order_online"})
        if tag_label is not None:
            tag_label_span = tag_label.find('span', 'left-sidebar_checkbox_count')
            if tag_label_span is not None:
                tag_label_span_str = tag_label_span.get_text()

                productlist_count = int(tag_label_span_str[1:-1])
                debug_printline("**** total products: ", productlist_count)
                page_count = math.ceil(productlist_count/ItemsPerPage)
                debug_printline("**** total pages:", page_count)

                for page_num in range(0, page_count):
                    # 分别爬取每个列表页面
                    # 页面 url = url?page=1 ...
                    page_num += 1
                    page_link = url + '?page=' + str(page_num)
                    debug_printline("page# ", page_num)
                    debug_printline(page_link)

                    # load dynamic url using selenium
                    # 产品列表是动态生成，所以使用 selenium 加载完成之后再爬取
                    soup = browser_load_remote_url(page_link)

                    current_product_index_on_this_page = 0

                    tag_div_container = soup.find('div', class_='product-list-group paged-items')
                    # tag_div_total = tag_div_container.find('div', 'content-layout_inside-anchor')
                    tags_div = tag_div_container.find_all('div', 'js-product-tile-container')
                    for tag_div in tags_div:
                        tag_section = tag_div.find('section', 'product-list')
                        if tag_section is not None:
                            '''
                            每个产品使用 <article></article> 包含
                            '''
                            tags_article = tag_section.find_all('article', class_='codified-product-tile', attrs={"data-product-id"})
                            if tags_article is not None:
                                for tag_article in tags_article:
                                    '''
                                    这里需要等待 selenium 重新加载页面数据
                                    否则会返回错误
                                    已经设置隐性等待时间 30 秒 
                                    '''
                                    # 再设置一次等待时间
                                    time.sleep(5)

                                    debug_print("**** new item **** { ")
                                    current_product_index_on_this_page += 1
                                    debug_print(current_product_index_on_this_page)
                                    debug_print(" } ")

                                    # 产品唯一 7 位数编码
                                    product_id = tag_article.get('data-product-id').strip()
                                    if not product_id:
                                        product_id = "0000000"

                                    tag_a = tag_article.find('a')

                                    if not tag_a:
                                        # 不存在此产品链接
                                        product_url = "/"
                                    else:
                                        # 产品链接
                                        product_url = BASE_URL + tag_a.get('href')

                                        # 产品名称描述
                                        tag_description = tag_a.find('div', 'codified-product-tile__row--title')
                                        if tag_description:
                                            tag_desc_p = tag_description.find('p', 'fn')
                                            if tag_desc_p:
                                                tag_desc_p_span = tag_desc_p.find('span', attrs={'style':'display: block; overflow: hidden; height: 0px; width: 100%;', 'aria-hidden': True})
                                                if tag_desc_p_span:
                                                    # 产品名称
                                                    product_description = tag_desc_p_span.get_text()
                                                else:
                                                    product_description = tag_desc_p.get_text()
                                                    if not product_description:
                                                        product_description = "failed to load product information"

                                        # 产品价格
                                        tag_price = tag_a.find('div', class_='codified-product-tile__row--price-button has-price-value')
                                        if not tag_price:
                                            product_price = 0
                                        else:
                                            tag_price_div = tag_price.find('div', 'codified-product-tile__price')
                                            if tag_price_div:
                                                tag_price_div_div = tag_price_div.find('div', 'codified-product-tile__price--value price-value')
                                                if tag_price_div_div:
                                                    tag_price_div_div_span_dollars = tag_price_div_div.find('span', 'codified-product-tile__price--value--dollars')
                                                    if tag_price_div_div_span_dollars:
                                                        tag_price_dollars_str = tag_price_div_div_span_dollars.get_text().strip().replace(',', '')
                                                        if tag_price_dollars_str:
                                                            tag_price_dollars = int(tag_price_dollars_str)
                                                        else:
                                                            tag_price_dollars = 0
                                                        tag_price_div_div_span_cents = tag_price_div_div.find('span', 'codified-product-tile__price--value--decimal-cents')
                                                        tag_price_cents_str = tag_price_div_div_span_cents.get_text().strip()
                                                        if tag_price_cents_str:
                                                            tag_price_cents = float(tag_price_cents_str)
                                                        else:
                                                            tag_price_cents = 0
                                                        # 产品价格
                                                        product_price = tag_price_dollars + tag_price_cents

                                        # 打印产品信息
                                        # debug_print("====> item details:")
                                        debug_print(product_id)
                                        debug_print(" | ", product_description)
                                        debug_print(" | $", product_price)
                                        debug_print(" | ", product_url)

                                        # 分析产品页面
                                        # parse_items(product_url)

                                    # 换行
                                    debug_printline('')

                    # close selenium browser window
                    browser_close()
            else:
                debug_printline(url)
                debug_exit("WARNING: parse_product_list | tag_label_span is None")
        else:
            debug_printline(url)
            debug_exit("WARNING: parse_product_list | tag_legend is None")
    else:
        debug_printline(url)
        debug_exit("WARNING: parse_product_list | tag_div_container is None")
    return


# parse items
# 爬取产品页面

def parse_items(url):
    # INPUT:
    # URL = https://www.bunnings.com.au/makita-lxt-18v-brushless-cordless-impact-driver-skin-only_p6240412
    #
    # OUTPUT:
    #

    # 详细信息已经可以从产品列表提取出来了，暂时不用分析此页面
    # debug print
    debug_printline("**** parse_items ****")
    debug_printline(url)
    debug_level(5)

    return



# *************************************************************************
# main entry
# *************************************************************************

url = START_URL

if DEBUG_MODE:
    # url = DEBUG_URL
    url = START_URL
else:
    url = START_URL

parse_our_range(url)
