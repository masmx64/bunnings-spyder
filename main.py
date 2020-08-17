#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# import libs
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.firefox.options import Options
import lxml
import json
import time
import math
import sys
import random
import os
import csv
import rich
from rich import print
from rich.console import Console
from rich.table import Column, Table

DEBUG_MODE = True

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

BASE_URL = "https://www.bunnings.com.au"
CAT_URL = "/our-range"
START_URL = BASE_URL + CAT_URL

DEBUG_URL = "./tools.html"

BASE_DIR = "./bunnings-warehouse/"
CAT_FILE_EXT = ".cat"
CSV_FILE_EXT = ".csv"

global WARNING_LOG_FILE
WARNING_LOG_FILE = 'warning.log'
global URL_LOG_FILE
URL_LOG_FILE = 'url.log'

global FOX_DRIVER
global ItemsPerPage
global console
global DEBUG_LEVEL

console = Console()

# 产品列表页面每页显示的产品数
# 默认是 48
ItemsPerPage = 48


# 测试页面类别

def test_url_level(soup):
    if soup.find('div', "chalkboard-module-dropdown"):
        # our-range
        return 1
    elif soup.find('div', attrs={"class": "inside-layout", "datav3-module-name": "RangeCategories"}):
        # main category
        return 2
    elif soup.find('ul', attrs={"class": "not-list"}):
        if not soup.find('div', attrs={"class": "search-result__sub-heading-refresh"}):
            # sub category
            return 3
        else:
            # product list
            return 4
    elif soup.find('div', attrs={"class": "product-detail__container"}):
        # item detail
        return 5
    else:
        return 0
    # return


# debug print
# print line without CRLF
def debug_print(*params):
    if DEBUG_MODE :
        for s in params:
            console.print(s, end='')
    else:
        pass
    return


# print with new line
def debug_printline(*params):
    if DEBUG_MODE:
        for s in params:
            console.print(s, end='')
        console.print('')
    else:
        pass
    return


def log2file(log_file, url, msg):
    with open(log_file, 'a') as log:
        log.writelines(url + '\n')
        if msg:
            log.writelines(msg + '\n')
    return


def debug_log_warning_msg(url, msg):
    # debug exit with error code/msg
    if DEBUG_MODE:
        log2file(WARNING_LOG_FILE, url, msg)
        # sys.exit(msg)
    else:
        pass
    return


def debug_log_url(url, msg):
    if DEBUG_MODE:
        log2file(URL_LOG_FILE, url, msg)
    else:
        pass
    return


# 输出产品列表到表格

def debug_add_table_header(table):
    if DEBUG_MODE:
        table.add_column("ID", style="dim", width=4, justify="right")
        table.add_column("S/N", width=7, justify="left")
        table.add_column("ITEM", width=96, justify="left")
        table.add_column("PRICE", width=12, justify="right")
        table.add_column("URL", width=96, justify="left")
    return


def debug_add_item(table, id, sn, name, price, url):
    if DEBUG_MODE:
        table.add_row(id, sn, name, price, url)
    return


def debug_printtable(table):
    if DEBUG_MODE:
        console.print(table)
    return


# debug level
'''    
breadcrumb = [
                "/our-range",                                                   # 一级页面 - 产品总体分类
                "/our-range/tools",                                             # 二级页面 -
                "/our-range/tools/power-tools",                                 # 三级页面 - 三级、四级页面结构一样
                "/our-range/tools/power-tools/drills",                          # 四级页面 -
                "our-range/tools/power-tools/drills/cordless-drill-skins",      # 五级页面 - 产品列表
                "items"                                                         # 六级页面 - 产品详细信息
              ]
'''


# get remote webpage for parsing
# 加载页面
# 适用于一级~五级页面

def load_remote_url(url):
    # load remote file
    # time.sleep(3)
    with requests.request('GET', url, headers={'User-agent': random.choice(ua)}) as webpage:
        content = webpage.text
        soup = BeautifulSoup(content, 'lxml')
    return soup


# get remote webpage for parsing
# 使用 selenium 加载页面
# 适用于五级页面

def browser_load_remote_url(url):
    global FOX_DRIVER
    # firefox = FirefoxBinary("/usr/bin/firefox")
    options = Options()
    options.headless = True
    FOX_DRIVER = webdriver.Firefox(options=options)
    # 设置隐性等待时间，最长等待 30 秒
    FOX_DRIVER.implicitly_wait(30)
    FOX_DRIVER.get(url)
    soup = BeautifulSoup(FOX_DRIVER.page_source, 'lxml')
    return soup


# close selenium
# 关闭 selenium 打开的浏览器窗口

def browser_close():
    global FOX_DRIVER
    FOX_DRIVER.close()
    return


# save product details to file
# 保存产品信息

def save_product_to_file(p_category, p_id, p_description, p_price, p_url, p_img_url):
    # 根据 url 创建文件夹和文件名
    # ie. /our-range
    #     ../tools
    #       ../power-tools
    #         ../drills
    #           ../cordless-power-drills
    #             ../Makita LXT 18V Brushless Cordless Impact Driver - Skin Only.csv
    # :param p_url:
    # :param p_id:
    # :param p_description:
    # :param p_price:
    # :param p_img_url:
    # :return:

    csv_dir = BASE_DIR + p_category
    csv_file_name = csv_dir + '/' + p_id + CSV_FILE_EXT

    if not os.path.exists(csv_dir):
        # debug_log_warning_msg(p_category, "WARNING: " + p_category + " is not existing")
        os.makedirs(csv_dir)
        # debug_printline("WARNING: " + csv_dir + " is not existing")
        # return
    if not os.path.exists(csv_file_name):
        with open(csv_file_name, 'w') as csv_file:
            csv_file.writelines(p_id + '\n')
            csv_file.writelines(p_description + '\n')
            csv_file.writelines(p_price + '\n')
            csv_file.writelines(p_url + '\n')
            csv_file.writelines(p_img_url + '\n')
    else:
        # debug_printline("WARNING: " + csv_file_name + " is existing")
        pass
    return


# strip category from url
# 从 url 中提取产品类别
# url 如果是完整的 网页链接，则返回 https://www.bunnings.com.au 之后的部分
#     如果是 /our-range/... 格式，则返回整个 url
#     否则返回 False

def get_cat_from_url(url):
    if url.startswith(BASE_URL):
        return url[len(BASE_URL):]
    elif url.startswith(CAT_URL):
        return url
    else:
        return False


# save category url details to file
# 保存商品分类的 URL 信息

def save_cat_url(cat_url, cat_name, productlist_count):
    dest_dir = BASE_DIR + cat_url + '/'
    dest_file = dest_dir + cat_name + CAT_FILE_EXT

    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    if not os.path.exists(dest_file):
        with open(dest_file, 'w') as cat:
            cat.writelines(cat_url + '\n')
            cat.writelines("products = " + str(productlist_count))
            debug_printline("saving | products = " + str(productlist_count))
    return


# 检查产品分类页面是否已经被爬取过

def cat_is_existing(p_url, p_name):
    # 根据 url 创建文件
    # :param p_name:
    # :param p_url:
    # :return:
    #           True    if existing
    #           False   if not existing

    dest_dir = BASE_DIR + p_url
    dest_file_name = dest_dir + '/' + p_name + CAT_FILE_EXT

    if os.path.exists(dest_dir):
        if os.path.exists(dest_file_name):
            with open(dest_file_name, 'r') as cat:
                for line in cat:
                    if line.startswith("products = "):
                        productlist_count = int(line.split(' ')[2])
                        if productlist_count > 0:
                            debug_printline("existing | products = " + str(productlist_count))
                            return True
    return False


# ======== ======== ======== ======== ======== ======== ======== ========
# parse our-range
# 爬取总体分类页面

def parse_our_range(url):
    # INPUT:
    # URL = BASE_URL + /our-range/
    # OUTPUT:
    # URL = BASE_URL + /our-range/tools
    #                          ../...

    # debug print
    debug_printline("==== ==== <our-range> ==== ====")
    debug_printline(url)

    soup = load_remote_url(url)

    tags_div = soup.find_all('div', 'chalkboard-module-dropdown')

    for tag_div in tags_div:
        tag_a = tag_div.find('a', 'chalkboard-header')
        tag_a_name = tag_a.get_text().strip()
        tag_a_url = BASE_URL + tag_a.get('href')
        # debug print
        debug_printline(tag_a_name, " | ", tag_a_url)

        # save to log file
        debug_log_url(tag_a_url, '')

        # parse each category
        tags_li = tag_div.find('ul', 'chalkboard-menu').find_all('li')
        for tag_li in tags_li:
            tag_li_a = tag_li.find('a')
            tag_li_a_name = tag_li_a.get_text().strip()
            tag_li_a_url = tag_li_a.get('href')
            debug_printline(tag_a_name, " | ", tag_li_a_url, " | ", tag_li_a_name)

            # parse_sub_categories(BASE_URL + tag_li_a_url)
        # parse main categories
        parse_main_categories(tag_a_url)

    # debug print
    debug_log_warning_msg(url, "==== ==== </our-range> ==== ====")
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
    debug_printline("==== ==== <main_categories> ==== ====")
    debug_printline(url)

    soup = load_remote_url(url)

    categories = soup.find_all('div', class_='inside-layout', attrs={"datav3-module-name": "RangeCategories"})
    if categories:
        for cat in categories:
            tag_div = cat.find('div', 'category-block-heading')
            tag_a = tag_div.find('a', 'category-block-heading__title')
            # category title
            cat_name = tag_a.find('h2', 'category-block-heading__text').get_text().strip()
            cat_url = tag_a.get('href')
            # categories count
            cat_count = int(tag_a.find('span', 'category-block-heading__count').get_text().strip())
            # debug print
            debug_printline(cat_name, " | ", cat_url, " | ", str(cat_count))

            # save to log file
            debug_log_url(cat_url, cat_name + ' = ' + str(cat_count))

            # parse sub categories
            parse_sub_categories(BASE_URL + cat_url)
    else:
        # debug_printline(url)
        debug_log_warning_msg(url, "WARNING: parse_main_categories | categories is None")
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

    debug_printline("==== ==== <sub-categories> ==== ====")
    debug_printline(url)

    soup = load_remote_url(url)

    tag_ul = soup.find('ul', 'not-list')
    if not tag_ul:
        debug_printline("WARNING: parse_sub_categories | tag_ul is None")
        debug_log_warning_msg(url, "WARNING: parse_sub_categories | tag_ul is None")
    else:
        tag_li = tag_ul.find('li', 'current')
        if not tag_li:
            debug_printline("WARNING: parse_sub_categories | tags_li is None")
            debug_log_warning_msg(url, "WARNING: parse_sub_categories | tags_li is None")
        else:
            tag_li_ul = tag_li.find('ul')
            if not tag_li_ul:
                debug_printline("WARNING: parse_sub_categories | tag_li_ul is None")
                debug_log_warning_msg(url, "WARNING: parse_sub_categories | tag_li_ul is None")
            else:
                tags_li_ul_li = tag_li_ul.find_all('li')
                if not tags_li_ul_li:
                    debug_printline("WARNING: parse_sub_categories | tags_li_ul_li is None")
                    debug_log_warning_msg(url, "WARNING: parse_sub_categories | tags_li_ul_li is None")
                else:
                    for tag_li_ul_li in tags_li_ul_li:
                        tag_a = tag_li_ul_li.find('a')
                        tag_a_name = tag_a.get_text().strip().replace('/', '-')
                        tag_a_url = tag_a.get('href')

                        # debug print
                        debug_printline("..." + tag_a_url + " | " + tag_a_name)

                        # save to log file
                        debug_log_url(tag_a_url, '')

                        # 这里需要判断本页面是子分类页面还是产品列表页面
                        # 判断依据是
                        # tag_div = soup.find('div', 'search-result__sub-heading-refresh')
                        page_level = test_url_level(soup)
                        if page_level == 3:
                            # parse sub categories
                            # 爬取子分类
                            # 页面结构和算法和本方法相同
                            # 这里需要检测该页面是否已经爬取过
                            # 如果已经爬过，则跳过
                            if not cat_is_existing(tag_a_url, tag_a_name):
                                # 爬取子分类页面
                                parse_sub_categories(BASE_URL + tag_a_url)
                        elif page_level == 4:
                            # 这里需要检测该页面是否已经爬取过
                            # 如果已经爬过，则跳过
                            if not cat_is_existing(tag_a_url, tag_a_name):
                                # 爬起产品列表页面
                                productlist_count = parse_product_list(BASE_URL + tag_a_url)
                                # save category url & name
                                save_cat_url(tag_a_url, tag_a_name, productlist_count)
                        else:
                            debug_printline("WARNING: *******************************************")
                            debug_log_warning_msg(url, "Not in sub category or product list page")
    return


# parse product list page
# 爬取产品列表页面

def parse_product_list(url):
    # INPUT:
    # URL = BASE_URL + /our-range/tools/power-tools/drills/cordless-drill-skins
    #                                                   ../...
    # OUTPUT:
    # URL = https://www.bunnings.com.au/makita-lxt-18v-brushless-cordless-impact-driver-skin-only_p6240412
    #                                ../...

    # debug print
    debug_printline("==== ==== <product-list> ==== ====")
    debug_printline(url)

    soup = load_remote_url(url)

    productlist_count = 0

    tag_div_container = soup.find('div', attrs={"class": ["product-list-group", "paged-items"]})

    if not tag_div_container:
        debug_printline("WARNING: ", url)
        debug_printline("WARNING: parse_product_list | tag_div_container is None")
        debug_log_warning_msg(url, "WARNING: parse_product_list | tag_div_container is None")
    else:
        # this is the product list page
        # find products total counts first, default count/page is 48
        tag_div = soup.find('div', 'search-result__sub-heading-refresh')
        if not tag_div:
            debug_printline("WARNING: parse_product_list | tag_legend is None")
            debug_log_warning_msg(url, "WARNING: parse_product_list | tag_legend is None")
        else:
            tag_div_h2 = tag_div.find('h2', 'search-result__sub-heading')
            if not tag_div_h2:
                debug_printline("WARNING: parse_product_list | tag_label_span is None")
                debug_log_warning_msg(url, "WARNING: parse_product_list | tag_label_span is None")
            else:
                tag_div_h2_str = tag_div_h2.get_text().strip()

                productlist_count_str = tag_div_h2_str.split()[0]
                productlist_count = int(productlist_count_str)
                debug_printline(">> total products: ", productlist_count_str)
                page_count = math.ceil(productlist_count/ItemsPerPage)
                debug_printline(">>    total pages: ", str(page_count))

                for page_num in range(0, page_count):
                    # 分别爬取每个列表页面
                    # 页面 url = url?page=1 ...
                    page_num += 1
                    page_num_str = str(page_num)
                    page_link = url + '?page=' + page_num_str
                    # debug_printline("page# ", page_num_str)
                    debug_printline("page# ", page_num_str + " /" + str(page_count))
                    debug_printline(page_link)

                    # load dynamic url using selenium
                    # 产品列表是动态生成，所以使用 selenium 加载完成之后再爬取
                    soup = browser_load_remote_url(page_link)

                    # 添加表格
                    table = Table(show_header=True, header_style="bold magenta")
                    debug_add_table_header(table)

                    current_product_index_on_this_page = 0

                    tag_div_container = soup.find('div', attrs={"class": "product-list-group", "class": "paged-items"})
                    # tag_div_total = tag_div_container.find('div', 'content-layout_inside-anchor')
                    tags_div = tag_div_container.find_all('div', 'js-product-tile-container')
                    for tag_div in tags_div:
                        tag_section = tag_div.find('section', 'product-list')
                        if tag_section:
                            '''
                            每个产品使用 <article></article> 包含
                            '''
                            tags_article = tag_section.find_all('article', class_='codified-product-tile', attrs={"data-product-id"})
                            if tags_article:

                                for tag_article in tags_article:
                                    '''
                                    这里需要等待 selenium 重新加载页面数据
                                    否则会返回错误
                                    已经设置隐性等待时间 30 秒 
                                    '''
                                    # 再设置一次等待时间
                                    # time.sleep(5)

                                    # 更新产品索引
                                    current_product_index_on_this_page += 1

                                    # debug_print("{ ")
                                    # debug_print(current_product_index_on_this_page)
                                    # debug_print(" } ")

                                    # 产品唯一 7 位数编码
                                    product_id = tag_article.get('data-product-id')
                                    if not product_id:
                                        product_id = "0000000"

                                    tag_a = tag_article.find('a')

                                    if not tag_a:
                                        # 不存在此产品链接
                                        product_url = "/"
                                    else:
                                        # 产品链接
                                        product_url = tag_a.get('href')

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
                                                        debug_printline(product_description)

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
                                                else:
                                                    tag_price_dollars = 0
                                                    tag_price_cents = 0
                                            else:
                                                tag_price_dollars = 0
                                                tag_price_cents = 0
                                            # 产品价格
                                            product_price = tag_price_dollars + tag_price_cents

                                        # 打印产品信息
                                        # debug_add_item(table, str(current_product_index_on_this_page), product_id, product_description, "$" + str(product_price), product_url)
                                        debug_add_item(table, f'{current_product_index_on_this_page: 4d}', product_id, product_description, f'${product_price: ,.2f}', product_url)
                                        # debug_print(product_id)
                                        # debug_print(" | ", product_description)
                                        # debug_print(" | $", product_price)
                                        # debug_print(" | ", product_url)

                                        cat_url = get_cat_from_url(url)
                                        if cat_url:
                                            save_product_to_file(cat_url, product_id, product_description, str(product_price), product_url, 'img_url/')

                                        # 分析产品页面
                                        # parse_items(BASE_URL + product_url)

                                    # 换行
                                    # debug_printline('')

                    # 打印表格
                    debug_printtable(table)

                    # close selenium browser window
                    browser_close()
    return productlist_count


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
    debug_printline("==== ==== <item-page> ==== ====")
    debug_printline(url)

    soup = load_remote_url(url)

    page_level = test_url_level(soup)
    if not page_level == 5:
        debug_printline(url, "is not valid item page")
        debug_log_warning_msg(url, "not valid item page")
        return

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

start_time = time.asctime(time.localtime(time.time()))
debug_printline(start_time)

args_num = len(sys.argv)
if args_num > 1:
    for i in range(1, args_num):
        start_time = time.asctime(time.localtime(time.time()))
        debug_log_url(url, start_time)

        url = sys.argv[i]
        if not url.startswith((BASE_URL)):
            if not url.startswith(CAT_URL):
                debug_printline(f'WARNING: {url} is not valid url')
                # exit program
                finish_time = time.asctime(time.localtime(time.time()))
                debug_log_url(url, finish_time)
                sys.exit("Not valid url")
            else:
                # /our-range/...
                # amend url to full https://bunnings.com.au/our-range/...
                url = BASE_URL + url

        soup = load_remote_url(url)
        url_level = test_url_level(soup)

        if url_level == 1:
            debug_printline(">> [ our range ]")
            parse_our_range(url)
        elif url_level == 2:
            debug_printline(">> [ main category ]")
            parse_main_categories(url)
        elif url_level == 3:
            debug_printline(">> [ sub category ]")
            parse_sub_categories(url)
        elif url_level == 4:
            debug_printline(">> [ product list ]")
            parse_product_list(url)
        elif url_level == 5:
            debug_printline(">> [ item details ]")
            parse_items(url)
        else:
            debug_printline("argv[", str(i), "] ", "is not valid url")

        finish_time = time.asctime(time.localtime(time.time()))
        debug_log_url(url, finish_time)

else:
    DEBUG_LEVEL = 0
    parse_our_range(url)

finish_time = time.asctime(time.localtime(time.time()))
debug_printline(finish_time)
debug_log_url(url, finish_time)
