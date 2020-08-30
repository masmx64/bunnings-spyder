#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# import libs
import lib as lib
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
# import random
import os
import csv
import rich
from rich import print
from rich.console import Console
from rich.table import Table
from rich.traceback import install

# from lib import bunnings_debug

install()

# ======== ======== ======== ======== ======== ======== ======== ======== ======== ======== ======== ========
# Global STATIC VARIABLES
# ======== ======== ======== ======== ======== ======== ======== ======== ======== ======== ======== ========


# ======== ======== ======== ======== ======== ======== ======== ======== ======== ======== ======== ========
# class DEBUG
# ======== ======== ======== ======== ======== ======== ======== ======== ======== ======== ======== ========


class Debug:
    # DEBUG_MODE
    # console

    BASE_DIR = "./bunnings-warehouse"
    CAT_FILE_EXT = ".cat"
    CSV_FILE_EXT = ".csv"

    LOG_FILE = 'warning.log'
    URL_FILE = 'url.log'

    SAVED_ITEMS = {
                'category': 'category=', 
                'path': 'path=',
                'url': 'url=', 
                'listed': 'listed=',
                'saved': 'saved=', 
                'uid': 's/n=', 
                'product': 'product=',
                'price': 'price=', 
                'unit': 'unit=', 
                'img': 'img=',
                'img_small': 'img_small=',
                'img_medium': 'img_medium=',
                'img_large': 'img_large=', 
                'brand': 'brand=', 
                'logo': 'logo='
                }

    SPACE = ' '
    CRLF = "\n"

    DEBUG_MODES = [True, False]
    FILE_OPT_MODES = ['r', 'w', 'a', 'rb', 'wb']

    # start_time = time.asctime(time.localtime(time.time()))
    # finish_time = time.asctime(time.localtime(time.time()))

    def __init__(self, mode=True):
        # init debug
        # debug mode default is ON
        self.DEBUG_MODE = mode
        self.console = Console(record=mode)
        self.table = None
        return

    # debug display functions
    # -----------------------
    def print(self, *params):
        # print line
        if self.DEBUG_MODE:
            for param in params:
                self.console.print(param)
        return

    def log(self, *msgs):
        # log debug message to file
        for msg in msgs:
            self.console.log(msg)
        return

    def warning(self, *msgs, time_stamp=False):
        # display & log warning msg to a file
        if self.DEBUG_MODE:
            for msg in msgs:
                if time_stamp:
                    log_msg = f'{time.asctime(time.localtime(time.time()))} | [b yellow]WARNING[/] | {msg}'
                else:
                    log_msg = f'[b yellow]WARNING[/] | {msg}'
                self.console.log(log_msg)
                self.console.save_text(self.LOG_FILE)
        return

    def error(self, *msgs, time_stamp=False, exit_on_err=False, err_code=-1):
        # display/log error msg
        if self.DEBUG_MODE:
            for msg in msgs:
                if time_stamp:
                    log_msg = f'{time.asctime(time.localtime(time.time()))} | [b red]ERROR[/] | {msg}'
                else:
                    log_msg = f'[b red]ERROR[/] | {msg}'
                self.console.log(log_msg)
                self.console.save_text(self.LOG_FILE)
            if exit_on_err:
                sys.exit(err_code)
        return

    def init_table(self, title=''):
        # init table
        # output result in a more readable format

        if len(title) > 0:
            self.table = Table(title=title)
        else:
            self.table = Table()
        self.table.show_header = True
        self.table.header_style = 'bold magenta'
        self.table.add_column("ID", style="dim", width=4, justify="right")
        self.table.add_column("S/N", width=7, justify="left")
        self.table.add_column("ITEM", width=96, justify="left")
        self.table.add_column("PRICE", width=12, justify="right")
        self.table.add_column("UNIT", width=12, justify="left")
        self.table.add_column("URL", width=96, justify="left")
        return

    def add_table_item(self, item_id, sn, name, price, unit, p_url):
        self.table.add_row(item_id, sn, name, price, unit, p_url)
        return

    def print_table(self):
        self.console.print(self.table)
        return

    # debug logging functions
    # -----------------------
    def log2file(self, log_file, *params, mode='a'):
        # log msg to a file
        try:
            with open(log_file, mode=mode) as f_log:
                for param in params:
                    f_log.writelines(param)
        except IOError:
            self.error(f'[b r]EXCEPTION | {log_file}', exit_on_err=True)
        return

    def log_url(self, *params, mode='a'):
        self.log2file(self.URL_FILE, params, mode)
        return

    def make_dest_file(self, cat_url, cat_name, file_ext):
        dest_dir = self.BASE_DIR + cat_url
        dest_file = dest_dir + '/' + cat_name + file_ext
        return  dest_dir, dest_file

    def save_product_info(self, p_category, p_id, p_description, p_price, p_unit, p_url, p_img_url):
        # create folder & file based on url
        # ie. /our-range
        #     ../tools
        #       ../power-tools
        #         ../drills
        #           ../cordless-power-drills
        #             ../Makita LXT 18V Brushless Cordless Impact Driver - Skin Only.csv
        # in:       p_url   -   product url
        #           p_id    -   product 7-digits unique serial number
        #           p_description   -   product name/description
        #           p_price -   product price
        #           p_unit  -   product unit
        #           p_img_url   -   product image url
        # out:

        dest_dir, dest_file_name = self.make_dest_file(p_category, p_id, self.CSV_FILE_EXT)

        status_msg = dest_file_name

        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
            status_msg += ' | DIR CREATED'
        if not os.path.exists(dest_file_name):
            status_msg += ' | [b i green]SAVED[/]'
        else:
            status_msg += ' | [b i green]UPDATED[/]'
        self.log2file(
                        dest_file_name, 
                        f'{self.SAVED_ITEMS["uid"]}{self.SPACE}{p_id}', 
                        f'{self.SAVED_ITEMS["product"]}{self.SPACE}{p_description}', 
                        f'{self.SAVED_ITEMS["price"]}{self.SPACE}{p_price}', 
                        f'{self.SAVED_ITEMS["unit"]}{self.SPACE}{p_unit}', 
                        f'{self.SAVED_ITEMS["url"]}{self.SPACE}{p_url}', 
                        f'{self.SAVED_ITEMS["img"]}{self.SPACE}{p_img_url}'
                    )
        self.log(f'{status_msg} | {p_description} | ${float(p_price): .2f}')
        return

    def save_cat_info(self, cat_url, cat_name, product_list_count, saved_count):
        # save category details to file after saving all listed products under this category

        dest_dir, dest_file = self.make_dest_file(cat_url, cat_name, self.CAT_FILE_EXT)

        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
            self.warning(f'{dest_dir}| [b]FOLDER CREATED[/]')
        # if not os.path.exists(dest_file):
        self.log2file(
                        dest_file, 
                        f'{self.SAVED_ITEMS["category"]}{self.SPACE}{cat_name}',
                        f'{self.SAVED_ITEMS["path"]}{self.SPACE}{cat_url}',
                        f'{self.SAVED_ITEMS["listed"]}{self.SPACE}{product_list_count}', 
                        f'{self.SAVED_ITEMS["saved"]}{self.SPACE}{saved_count}'
                    )
        self.log(f'{dest_file} | {cat_name} | {saved_count} of {product_list_count} saved')
        return

    def check_cat_status(self, cat_url, cat_name):
        # check if category is already existing
        #
        # in:       cat_url - category url
        #           cat_name - category name
        # out:      0                   -   folder or file not existing, or file is empty
        #           product_list_count  -   folder existing & category items saved properly
        #           < 0                 -   difference (saved_items_count - product_list_count)

        dest_dir, dest_file = self.make_dest_file(cat_url, cat_name, self.CAT_FILE_EXT)

        product_list_count = 0
        saved_items_count = 0
        is_empty_file = True

        if not os.path.exists(dest_dir):
            # folder not existing, return 0
            return 0
        else:
            if not os.path.exists(dest_file):
                # file not existing, return 0
                return 0
            else:
                # file exists, then check if all listed products were saved correctly
                with open(dest_file, 'rw') as cat:
                    for line in cat:
                        if line.startswith(self.SAVED_ITEMS['listed']):
                            is_empty_file = False
                            # check listed products number
                            element = line.split('=')[-1].strip()
                            if element.isdigit():
                                product_list_count = int(element)
                        elif line.startswith(self.SAVED_ITEMS['saved']):
                            is_empty_file = False
                            # check saved products number
                            element = line.split('=')[-1].strip()
                            if element.isdigit():
                                saved_items_count = int(element)
                if is_empty_file:
                    # file is empty, then return 0
                    return 0
                else:
                    # check if listed == saved
                    if product_list_count == saved_items_count:
                        if saved_items_count > 0:
                            return saved_items_count
                    else:
                        return saved_items_count - product_list_count
        # return


# ======== ======== ======== ======== ======== ======== ======== ======== ======== ======== ======== ========
# class URL
# ======== ======== ======== ======== ======== ======== ======== ======== ======== ======== ======== ========


class URL:

    URLS = {
            'BASE_URL': 'https://www.bunnings.com.au',
            'CATEGORY_URL': '/our-range/',
            'START_URL': 'https://www.bunnings.com.au/our-range'
            }

    URL_STATS = {
                'URL_STARTS_WITH_HTTPS': 1,
                'URL_STARTS_WITH_CATEGORY': 2,
                'URL_CONTAINS_CATEGORY': 3
                }

    def validate(self, target_url):
        # check if a given url is starting with
        # https://www.bunnings.com.au, or
        # /our-range/...
        #
        # in:   url
        # out:  1:      starting with https://www...
        #       2:      starting with /our-range/...
        #       3:      starting with https:// but also contains ../our-range/..
        #       False:  not starting with either of the above

        if target_url.startswith(self.URLS['BASE_URL']):
            sub_url = target_url[len(self.URLS['BASE_URL']):]
            if sub_url.startswith(self.URLS['CATEGORY_URL']):
                return self.URL_STATS['URL_CONTAINS_CATEGORY']
            return self.URL_STATS['URL_STARTS_WITH_HTTPS']
        elif target_url.startswith(self.URLS['CATEGORY_URL']):
            return self.URL_STATS['URL_STARTS_WITH_CATEGORY']
        else:
            return False

    def get_relative_url(self, target_url):
        # strip a bunnings webpage url, &
        # get the relative path starting with /our-range/...
        #
        # in:   url
        # out:  success:    the '/our-range/...' part of the full webpage url
        #       fail:       False

        result = False
        valid = self.validate(target_url)
        if valid == self.URL_STATS['URL_STARTS_WITH_HTTPS'] or valid == self.URL_STATS['URL_CONTAINS_CATEGORY']:
            result = target_url[len(self.URLS['BASE_URL']):]
        elif valid == self.URL_STATS['URL_STARTS_WITH_CATEGORY']:
            result = target_url
        else:
            result = False
        return result

    def get_path_from_url(self, target_url):
        # return the category part of the url
        # in:       url to product category starting with https://www.bunnings.com.au/our-range/...
        # out:      /our-range/...

        return self.get_relative_url(target_url)

    def get_cat_name_from_url(self, target_url):
        # return the last part of a url

        path = self.get_path_from_url(target_url)
        if isinstance(path, str):
            element = path.split('/')[-1].strip()
            return element
        else:
            return False

    def complete_url(self, target_url):
        # complete leading part of url to make it a full valid bunnings website link
        # in:   url
        # out:  success https://www.bunnings.com.au/our-range/...
        #       fail    False

        valid = self.validate(target_url)
        if valid == self.URL_STATS['URL_STARTS_WITH_HTTPS'] or valid == self.URL_STATS['URL_CONTAINS_CATEGORY']:
            return target_url
        elif valid == self.URL_STATS['URL_STARTS_WITH_CATEGORY']:
            return self.URLS['BASE_URL'] + url
        else:
            return False
        # return

    def __init__(self, target_url=None):
        if target_url is None:
            self.current_url = self.URLS['START_URL']
        else:
            self.current_url = self.complete_url(target_url)

        self.pool = []
        self.visited = []
        self.pool.append(self.current_url)
        self.cur_pos = 0
        return

    def get_current_url(self):
        # return the url in the current pool position by cur_pos
        return self.pool[self.cur_pos]

    def get_default_start_url(self):
        return self.URLS['START_URL']

    def add(self, target_url):
        # add url to the end of pool
        if target_url not in self.pool:
            self.pool.append(target_url)
        return

    def pop(self, pos):
        # return & remove the url at the given position
        result = self.pool[pos]
        self.pool.pop(pos)

    def remove(self, target_url):
        self.pool.remove(target_url)
        return

    def is_existing(self, target_url):
        if target_url in self.pool:
            return True
        else:
            return False

# ======== ======== ======== ======== ======== ======== ======== ======== ======== ======== ======== ========
# class BROWSER
# ======== ======== ======== ======== ======== ======== ======== ======== ======== ======== ======== ========


class SilentFireFox:

    PAGE_LEVEL = {
                    'PAGE_OUR_RANGE': 1, 
                    'PAGE_MAIN_CATEGORY': 2,
                    'PAGE_SUB_CATEGORY': 3,
                    'PAGE_PRODUCT_LIST': 4,
                    'PAGE_ITEM_DETAIL': 5
                }
    EXCEPTION_CODE = {
                    'TIMEOUT_ERROR': 'TimeoutError',
                    'ATTRIBUTE_ERROR': 'AttributeError'
                }

    # init selenium firefox with headless mode
    def __init__(self):
        # firefox = FirefoxBinary("/usr/bin/firefox")
        options = Options()
        options.headless = True
        # options.add_argument('disable-blink-features=AutomationControlled')
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36')
        self.fox_driver = webdriver.Firefox(options=options)
        self.fox_driver.implicitly_wait(30)
        self.soup = None
        self.url = URL()
        self.debug = Debug()
        self.exception_occurred = False
        self.exception_code = 0
        return

    def __del__(self):
        self.fox_driver.close()
        return

    def set_exception_code(self, exception_code):
        self.exception_occurred = True
        self.exception_code = exception_code

    def clear_exception_status(self):
        self.exception_occurred = False
        self.exception_code = 0
        return

    def load_url(self, target_url):
        # get remote webpage using selenium headless mode
        try:
            self.clear_exception_status()
            self.fox_driver.get(self.url.complete_url(target_url))
            self.soup = BeautifulSoup(self.fox_driver.page_source, 'lxml')
        except TimeoutError:
            self.set_exception_code(self.EXCEPTION_CODE['TIMEOUT_ERROR'])
        finally:
            if self.exception_occurred:
                self.debug.error(f'EXCEPTION: {self.exception_code} | load_url | {target_url}', time_stamp=True, exit_on_err=True)
        return self.soup

    def find_tag_attrs(self, tag, key, value, find_all=False):
        # find tag attributes
        # with one pair of tag & attribute
        # (this function may be combined with the following two functions by using tuple/dictionary/set etc)
        # find_tag_attrs2() & find_tag_attrs4()

        try:
            self.clear_exception_status()
            if find_all:
                return self.soup.find_all(tag, attrs={key, value})
            else:
                return self.soup.find(tag, attrs={key, value})
        except TimeoutError:
            self.set_exception_code(self.EXCEPTION_CODE['TIMEOUT_ERROR'])
        except AttributeError:
            self.set_exception_code(self.EXCEPTION_CODE['ATTRIBUTE_ERROR'])
        finally:
            if self.exception_occurred:
                self.debug.error(f'EXCEPTION: {self.exception_code} | find_tag_attrs | <{tag} {key}=\"{value}\">', time_stamp=True, exit_on_err=True)
        # return

    def find_tag_attrs2(self, tag, key, value1, value2, find_all=False):
        # find tag attributes
        try:
            self.clear_exception_status()
            if find_all:
                return self.soup.find_all(tag, attrs={key: [value1, value2]})
            else:
                return self.soup.find(tag, attrs={key: [value1, value2]})
        except TimeoutError:
            self.set_exception_code(self.EXCEPTION_CODE['TIMEOUT_ERROR'])
        except AttributeError:
            self.set_exception_code(self.EXCEPTION_CODE['ATTRIBUTE_ERROR'])
        finally:
            if self.exception_occurred:
                self.debug.error(f'EXCEPTION: {self.exception_code} | find_tag_attrs2 | <{tag} {key}=\"{value1} {value2}\">', time_stamp=True, exit_on_err=True)
        # return

    def find_tag_attrs4(self, tag, key1, value1, key2, value2, find_all=False):
        # find tag attributes
        try:
            self.clear_exception_status()
            if find_all:
                return self.soup.find_all(tag, attrs={key1: value1, key2: value2})
            else:
                return self.soup.find(tag, attrs={key1: value1, key2: value2})
        except TimeoutError:
            self.set_exception_code(self.EXCEPTION_CODE['TIMEOUT_ERROR'])
        except AttributeError:
            self.set_exception_code(self.EXCEPTION_CODE['ATTRIBUTE_ERROR'])
        finally:
            if self.exception_occurred:
                self.debug.error(f'EXCEPTION: {self.exception_code} | find_tag_attrs4 | <{tag} {key1}=\"{value1}\" {key2}=\"{value2}\">', time_stamp=True, exit_on_err=True)
        # return

    def test_page_our_category(self):
        # check the position of a given url
        # by looking up specific 'div' tag attributes
        #
        # input:    soup
        # output:   int - page level
        #           1: /our-rage landing page
        #           2: main-category page
        #           3: sub-category page
        #           4: product-list page
        #           5: product detail page
        #           0: not on any of the above pages

        if self.find_tag_attrs('div', 'class', 'chalkboard-module-dropdown'):
            # our-range
            return self.PAGE_LEVEL['PAGE_OUR_RANGE']
        else:
            return False

    def test_page_main_category(self):
        # check the position of a given url
        # by looking up specific 'div' tag attributes
        #
        # input:    soup
        # output:   int - page level
        #           1: /our-rage landing page
        #           2: main-category page
        #           3: sub-category page
        #           4: product-list page
        #           5: product detail page
        #           0: not on any of the above pages

        if self.find_tag_attrs4('div', 'class', 'inside-layout', 'datav3-module-name', 'RangeCategories'):
            # main category
            return self.PAGE_LEVEL['PAGE_MAIN_CATEGORY']
        else:
            return False

    def test_page_sub_category(self):
        # check the position of a given url
        # by looking up specific 'div' tag attributes
        #
        # input:    soup
        # output:   int - page level
        #           1: /our-rage landing page
        #           2: main-category page
        #           3: sub-category page
        #           4: product-list page
        #           5: product detail page
        #           0: not on any of the above pages

        if self.find_tag_attrs('ul', 'class', 'not-list'):
            # need to double check this condition
            # "not-list" may be a universal fit condition
            if self.find_tag_attrs('div', 'class', 'search-result__sub-heading-refresh'):
                # product list
                return self.PAGE_LEVEL['PAGE_PRODUCT_LIST']
            else:
                # sub category
                return self.PAGE_LEVEL['PAGE_SUB_CATEGORY']
        else:
            return False

    def test_page_product_list(self):
        # check the position of a given url
        # by looking up specific 'div' tag attributes
        #
        # input:    soup
        # output:   int - page level
        #           1: /our-rage landing page
        #           2: main-category page
        #           3: sub-category page
        #           4: product-list page
        #           5: product detail page
        #           0: not on any of the above pages

        if self.find_tag_attrs2('div', 'class', 'product-list-group', 'paged-items'):
            # product list
            return self.PAGE_LEVEL['PAGE_PRODUCT_LIST']
        elif self.find_tag_attrs('ul', 'class', 'not-list'):
            # need to double check this condition
            # "not-list" may be a universal fit condition
            if self.find_tag_attrs('div', 'class', 'search-result__sub-heading-refresh'):
                # product list
                return self.PAGE_LEVEL['PAGE_PRODUCT_LIST']
            else:
                # sub category
                return self.PAGE_LEVEL['PAGE_SUB_CATEGORY']
        else:
            return False

    def test_page_item_detail(self):
        # check the position of a given url
        # by looking up specific 'div' tag attributes
        #
        # input:    soup
        # output:   int - page level
        #           1: /our-rage landing page
        #           2: main-category page
        #           3: sub-category page
        #           4: product-list page
        #           5: product detail page
        #           0: not on any of the above pages

        if self.find_tag_attrs('div', 'class', 'product-detail__container'):
            # item detail
            return self.PAGE_LEVEL['PAGE_ITEM_DETAIL']
        else:
            return False

    def test_page_level(self):
        # check the position of a given url
        # by looking up specific 'div' tag attributes
        #
        # input:    soup
        # output:   int - page level
        #           1: /our-rage landing page
        #           2: main-category page
        #           3: sub-category page
        #           4: product-list page
        #           5: product detail page
        #           0: not on any of the above pages

        if self.test_page_our_category() == self.PAGE_LEVEL['PAGE_OUR_RANGE']:
            # our-range
            return self.PAGE_LEVEL['PAGE_OUR_RANGE']
        elif self.test_page_main_category() == self.PAGE_LEVEL['PAGE_MAIN_CATEGORY']:
            # main category
            return self.PAGE_LEVEL['PAGE_MAIN_CATEGORY']
        elif self.test_page_sub_category() == self.PAGE_LEVEL['PAGE_SUB_CATEGORY']:
            # sub category
            return self.PAGE_LEVEL['PAGE_SUB_CATEGORY']
        elif self.test_page_product_list() == self.PAGE_LEVEL['PAGE_PRODUCT_LIST']:
            # product list
            return self.PAGE_LEVEL['PAGE_PRODUCT_LIST']
        elif self.test_page_item_detail() == self.PAGE_LEVEL['PAGE_ITEM_DETAIL']:
            # item detail
            return self.PAGE_LEVEL['PAGE_ITEM_DETAIL']
        else:
            return False

# ======== ======== ======== ======== ======== ======== ======== ======== ======== ======== ======== ========
# class BUNNINGS
# ======== ======== ======== ======== ======== ======== ======== ======== ======== ======== ======== ========


class Bunnings:

    ITEMS_PER_PAGE = 48

    def __init__(self):
        self.debug = Debug()
        self.url = URL()
        self.browser = SilentFireFox()

    def parse_our_range(self):
        # INPUT:
        # URL = BASE_URL + /our-range/
        # OUTPUT:
        # URL = BASE_URL + /our-range/tools
        #                          ../...

        init_url = self.url.get_default_start_url()
        self.browser.load_url(init_url)

        main_categories_count = 0
        sub_categories_count = 0
        sub_category_index = 0

        page_level = self.browser.test_page_level()
        self.debug.log(f'Page Level = {page_level} | <our-range> | {init_url}')

        tags_div = self.browser.find_tag_attrs('div', 'class', 'chalkboard-module-dropdown', True)
        for tag_div in tags_div:
            tag_a = tag_div.find('a', attrs={'class': 'chalkboard-header'})
            tag_a_name = tag_a.get_text().strip()
            # find each main category url
            # & save to url pool
            tag_a_url = tag_a.get('href').strip()
            if not self.url.is_existing(tag_a_url):
                self.url.add(tag_a_url)

            # // debug code
            main_categories_count += 1
            sub_category_index = 0
            self.debug.log(f'{main_categories_count}: {tag_a_name}| {tag_a_url}')

            tags_li = tag_div.find('ul', attrs={'class': 'chalkboard-menu'}).find_all('li')
            for tag_li in tags_li:
                tag_li_a = tag_li.find('a')
                tag_li_a_name = tag_li_a.get_text().strip()
                tag_li_a_url = tag_li_a.get('href').strip()

                sub_categories_count += 1
                sub_category_index += 1
                self.debug.log(f'\t{sub_category_index}: {tag_li_a_name} | {tag_li_a_url}')

                # parse_sub_categories(BASE_URL + tag_li_a_url)

            # parse main categories
            # self.parse_main_categories(tag_a_url)

        # debug print
        self.debug.log(f'</our-range> | {sub_categories_count} sub-categories found in {main_categories_count} main-categories\n')
        return

    def parse_main_categories(self, page_url):
        # INPUT:
        # URL = BASE_URL + /our-range/tools
        #                          ../...
        # OUTPUT:
        # URL = BASE_URL + /our-range/tools/power-tools
        #                                ../...

        self.browser.load_url(page_url)

        page_level = self.browser.test_page_level()
        main_category_name = self.url.get_cat_name_from_url(page_url)
        self.debug.log(f'Page Level = {page_level} | {main_category_name} | {page_url}')

        sub_category_index = 0
        categories = self.browser.find_tag_attrs4('div', 'class', 'inside-layout', 'datav3-module-name', 'RangeCategories', find_all=True)
        if categories:
            for cat in categories:
                tag_div = cat.find('div', attrs={'class': 'category-block-heading'})
                tag_div_a = tag_div.find('a', attrs={'class': 'category-block-heading__title'})
                # category title
                cat_name = tag_div_a.find('h2', 'category-block-heading__text').get_text().strip()
                # category url
                cat_url = tag_div_a.get('href')
                if not self.url.is_existing(cat_url):
                    self.url.add(cat_url)
                # categories count
                cat_count = int(tag_div_a.find('span', 'category-block-heading__count').get_text().strip())

                # debug print
                sub_category_index += 1
                self.debug.log(f'\t{sub_category_index}: {cat_name}  |  {cat_url}  |  {str(cat_count)} products')

                # save to log file
                self.debug.log_url(cat_url, cat_name, str(cat_count))

                # parse sub categories
                # self.parse_sub_categories(self.browser.url.complete_url(cat_url))
        else:
            self.debug.warning(f'Page Level = {page_level} | parse_main_categories | CATEGORY \"{main_category_name}\" NOT FOUND | {page_url}')

        return

    def parse_sub_categories(self, page_url):
        # INPUT:
        # URL = BASE_URL + /our-range/tools/power-tools
        #                                ../...
        # OUTPUT:
        # URL = BASE_URL + /our-range/tools/power-tools/drills
        #                                            ../...

        page_list_num = 0
        saved_num = 0

        self.browser.load_url(page_url)

        page_level = self.browser.test_page_level()
        sub_category_name = self.url.get_cat_name_from_url(page_url)
        self.debug.log(f'Page Level = {page_level} | {sub_category_name} | {page_url}')

        if page_level == self.browser.PAGE_LEVEL['PAGE_SUB_CATEGORY']:
            # on a sub-category page
            tag_ul = self.browser.find_tag_attrs('ul', 'class', 'not-list')
            if not tag_ul:
                self.debug.warning(f'parse_sub_categories | tag_ul not found | {page_url}')
            else:
                tag_li = tag_ul.find('li', 'current')
                if not tag_li:
                    self.debug.warning(f'parse_sub_categories | tags_li not found | {page_url}')
                else:
                    tag_li_ul = tag_li.find('ul')
                    if not tag_li_ul:
                        self.debug.warning(f'parse_sub_categories | tag_li_ul not found | {page_url}')
                    else:
                        tags_li_ul_li = tag_li_ul.find_all('li')
                        if not tags_li_ul_li:
                            self.debug.warning(f'parse_sub_categories | tags_li_ul_li not found | {page_url}')
                        else:
                            sub_category_index = 0
                            for tag_li_ul_li in tags_li_ul_li:
                                tag_a = tag_li_ul_li.find('a')
                                # sub-category name
                                tag_a_name = tag_a.get_text().strip().replace('/', '-')
                                # sub-category url
                                tag_a_url = tag_a.get('href')
                                if not self.url.is_existing(tag_a_url):
                                    self.url.add(tag_a_url)
                                sub_category_index += 1
                                self.debug.log(f'\t{sub_category_index}: {tag_a_name} | {tag_a_url}')

                                # save to log file
                                self.debug.log_url(tag_a_url)

                                # page_list_num, saved_num = self.debug.check_cat_status(tag_a_url, tag_a_name)

                                # if page_list_num == 0 or page_list_num != saved_num:
                                # page_list_num, saved_num = self.parse_sub_categories(self.browser.url.complete_url(tag_a_url))
                                # self.debug.save_cat_url(tag_a_url, tag_a_name, page_list_num, saved_num)
                                # self.debug.log(f'SAVING CATEGORY | {saved_num} / {page_list_num} products saved')
        # elif page_level == self.browser.PAGE_LEVEL['PAGE_PRODUCT_LIST']:
        #     # on a product-list page
        #     # parse product-list
        #     page_list_num, saved_num = self.parse_product_list(page_url)
        #     tmp_path = self.browser.url.get_path_from_url(page_url)
        #     tmp_name = self.browser.url.get_cat_name_from_url(page_url)
        #     # self.debug.save_cat_url(tmp_path, tmp_name, page_list_num, saved_num)
        #     self.debug.log(f'{page_url} | {saved_num} of {page_list_num} saved')
        #
        else:
            self.debug.warning(f'{page_url} | NOT ON A SUB-CATEGORY PAGE')

        return # page_list_num, saved_num

    def parse_product_list(self, page_url):
        # INPUT:
        # URL = BASE_URL + /our-range/tools/power-tools/drills/cordless-drill-skins
        #                                                   ../...
        # OUTPUT:
        # URL = https://www.bunnings.com.au/makita-lxt-18v-brushless-cordless-impact-driver-skin-only_p6240412
        #                                ../...

        self.browser.load_url(page_url)

        page_level = self.browser.test_page_level()
        sub_category_name = self.url.get_cat_name_from_url(page_url)
        self.debug.log(f'Page Level = {page_level} | {sub_category_name} | {page_url}')

        if page_level != self.browser.PAGE_LEVEL['PAGE_PRODUCT_LIST']:
            return False

        product_list_count = 0
        saved_product_count = 0
        page_count = 0
        cat_path = self.browser.url.get_path_from_url(page_url)

        tag_div_container = self.browser.find_tag_attrs2('div', 'class', 'product-list-group', 'paged-items')

        if not tag_div_container:
            self.debug.warning(f'parse_product_list | tag_div_container not found | {page_url}')
        else:
            # this is the product list page
            # find products total counts first, default count/page is 48
            tag_div = self.browser.find_tag_attrs('div', 'class', 'search-result__sub-heading-refresh')
            if not tag_div:
                self.debug.warning(f'parse_product_list | tag_legend not found | {page_url}')
            else:
                tag_div_h2 = tag_div.find('h2', 'search-result__sub-heading')
                if not tag_div_h2:
                    self.debug.warning(f'parse_product_list | tag_label_span not found | {page_url}')
                else:
                    tag_div_h2_str = tag_div_h2.get_text().lstrip()

                    product_list_count_str = tag_div_h2_str.split()[0]
                    if product_list_count_str.isdigit():
                        product_list_count = int(product_list_count_str)
                        page_count = math.ceil(product_list_count/self.ITEMS_PER_PAGE)
                    if page_count > 1:
                        self.debug.log(f'\ttotal products: {product_list_count_str} on {str(page_count)} pages')
                    else:
                        self.debug.log(f'\ttotal products: {product_list_count_str} on {str(page_count)} page')

                    for page_num in range(0, page_count):
                        # page url = url?page=1 ...
                        page_num += 1
                        page_num_str = str(page_num)
                        page_link = url + '?page=' + page_num_str
                        if not self.url.is_existing(page_link):
                            self.url.add(page_link)

                        item_num_left = product_list_count - (page_num - 1) * self.ITEMS_PER_PAGE
                        if item_num_left > self.ITEMS_PER_PAGE:
                            self.debug.log(f'\t\ttotal {self.ITEMS_PER_PAGE} products on page# {page_num_str}/{str(page_count)} | {page_link}')
                        else:
                            if item_num_left > 1:
                                self.debug.log(f'\t\ttotal {item_num_left} products on page# {page_num_str}/{str(page_count)} | {page_link}')
                            else:
                                self.debug.log(f'\t\ttotal {item_num_left} product on page# {page_num_str}/{str(page_count)} | {page_link}')

                        # self.parse_product_list_page(page_link)
        return True

    def parse_product_list_page(self, page_url):
        self.browser.load_url(page_url)
        page_level = self.browser.test_page_level()
        sub_category_name = self.url.get_cat_name_from_url(page_url)
        self.debug.log(f'Page Level = {page_level} | {sub_category_name} | {page_url}')
        if page_level != self.browser.PAGE_LEVEL['PAGE_PRODUCT_LIST']:
            self.debug.warning(f'{page_url} | NOT ON A PRODUCT-LIST PAGE')
            return False

        # init table output
        self.debug.table = None
        self.debug.init_table()

        current_product_index_on_this_page = 0
        page_num = page_url.split('=')[-1]

        tag_div_container = self.browser.find_tag_attrs2('div', 'class', 'product-list-group', 'paged-items')
        if not tag_div_container:
            self.debug.warning(f'page {page_num} | {page_url} | <div class="product-list-group paged-items"> | NOT FOUND')
        tags_div = tag_div_container.find_all('div', 'js-product-tile-container')
        if not tags_div:
            self.debug.warning(f'page {page_num} | {page_url} | <div class="js-product-tile-container"> | NOT FOUND')
        for tag_div in tags_div:
            tag_section = tag_div.find('section', 'product-list')
            if not tag_section:
                self.debug.warning(f'page {page_num} | {page_url} | <section class="product-list"> | NOT FOUND')
                break
            if tag_section:
                # each product is wrapped with <article></article>
                # tags_article = tag_section.find_all('article', attrs={'class': 'codified-product-tile', 'data-product-id': True})
                tags_article = tag_section.find_all('article', attrs={'class': ['codified-product-list', 'hproduct'], 'data-product-id': True})
                if not tags_article:
                    self.debug.warning(f'Page: {page_num} | {page_url} | <article class="codified-product-list hproduct" data-product-id="..."> | NOT FOUND')
                    break
                if tags_article:
                    for tag_article in tags_article:
                        # update the product index on this page
                        current_product_index_on_this_page += 1
                        self.parse_product_items(page_url, tag_article)
        # format output
        # self.debug.print_table()
        return

    def parse_product_items(self, page_url, tag_article):
        # product unique 7-digits id number
        product_id = tag_article.get('data-product-id')
        if not product_id:
            product_id = "0000000"
            self.debug.warning(f'PRODUCT ID NOT EXISTING | {page_url}')

        # product url
        tag_a = tag_article.find('a')
        if not tag_a:
            product_url = "/"
            self.debug.warning(f'{page_url} | PRODUCT LINK NOT EXISTING')
        else:
            product_url = tag_a.get('href').strip()
            if not self.url.is_existing(product_url):
                self.url.add(product_url)

            # product description
            product_description = 'n/a'
            tag_description = tag_a.find('div', 'codified-product-tile__row--title')
            if tag_description:
                tag_desc_p = tag_description.find('p', 'fn')
                if tag_desc_p:
                    tag_desc_p_span = tag_desc_p.find('span', attrs={'style': 'display: block; overflow: hidden; height: 0px; width: 100%;', 'aria-hidden': True})
                    if tag_desc_p_span:
                        product_description = tag_desc_p_span.get_text()
                    else:
                        product_description = tag_desc_p.get_text()
                        if not product_description:
                            product_description = "N/A"
                            self.debug.warning(f'PRODUCT INFORMATION NOT EXISTING | {page_url}')

            # product price
            product_price = 0
            tag_price = tag_a.find('div', attrs={'class': ['codified-product-tile__row--price-button', 'has-price-value']})
            if not tag_price:
                self.debug.warning(f'PRODUCT PRICE NOT EXIST | {page_url}')
            else:
                tag_price_dollars = 0
                tag_price_cents = 0
                tag_price_div = tag_price.find('div', 'codified-product-tile__price')
                if tag_price_div:
                    tag_price_div_div = tag_price_div.find('div', 'codified-product-tile__price--value price-value')
                    if tag_price_div_div:
                        # price dollars
                        tag_price_div_div_span_dollars = tag_price_div_div.find('span', 'codified-product-tile__price--value--dollars')
                        if tag_price_div_div_span_dollars:
                            tag_price_dollars_str = tag_price_div_div_span_dollars.get_text().strip().replace(',', '')
                            try:
                                tag_price_dollars = int(tag_price_dollars_str)
                            except ValueError:
                                tag_price_dollars = 0
                        # price cents
                        tag_price_div_div_span_cents = tag_price_div_div.find('span', 'codified-product-tile__price--value--decimal-cents')
                        if tag_price_div_div_span_cents:
                            tag_price_cents_str = tag_price_div_div_span_cents.get_text().strip()
                            try:
                                tag_price_cents = float(tag_price_cents_str)
                            except ValueError:
                                tag_price_cents = 0
                # combine dollars & cents
                product_price = tag_price_dollars + tag_price_cents

            # product unit
            product_price_unit = "/ea"
            tag_price_value_unit_measurement = tag_a.find('div', 'codified-product-tile__price--value--unit-measurement')
            if tag_price_value_unit_measurement:
                tag_price_value_unit_measurement_str = tag_price_value_unit_measurement.find('p')
                if tag_price_value_unit_measurement_str:
                    product_price_unit = tag_price_value_unit_measurement_str.get_text().strip()
                    if len(product_price_unit) == 0:
                        product_price_unit = "/ea"

            # save product info
            # self.debug.add_table_item(f'{current_product_index_on_this_page: 4d}', product_id, product_description, f'${product_price: ,.2f}', product_price_unit, product_url)
            cat_path = self.url.get_path_from_url(page_url)
            self.debug.save_product_info(cat_path, product_id, product_description, str(product_price), product_price_unit, product_url, '/img_url')
            self.debug.log(f'\t{product_id}: {product_description} | ${str(product_price)}')

            # parse each product
            # parse_items(BASE_URL + product_url)
            return

    def parse_items(self, product_url):
        # INPUT:
        # URL = https://www.bunnings.com.au/makita-lxt-18v-brushless-cordless-impact-driver-skin-only_p6240412
        #
        # OUTPUT:
        #
        # 详细信息已经可以从产品列表提取出来了，暂时不用分析此页面

        self.browser.load_url(product_url)
        page_level = self.browser.test_page_level()
        item_name = product_url.replace('-', ' ')
        if page_level != self.browser.PAGE_LEVEL['PAGE_ITEM_DETAIL']:
            self.debug.warning(f'{product_url} | NOT ON A PRODUCT DETAIL PAGE')
            return False
        self.debug.log(f'\tPage Level = {page_level} | {item_name}')
        return


# ======== ======== ======== ======== ======== ======== ======== ======== ======== ======== ======== ========
# MAIN ENTRY
# ======== ======== ======== ======== ======== ======== ======== ======== ======== ======== ======== ========
if __name__ == '__main__':
    bunnings = Bunnings()

    args_num = len(sys.argv)
    if args_num > 1:
        for i in range(1, args_num):
            arg = sys.argv[i]

            if arg.startswith('/h') or arg.startswith('/H') or arg.startswith('--help') or arg.startswith('--HELP'):
                bunnings.debug.print('USAGE: [param] [url]')
                bunnings.debug.error('USAGE: [param] [url]')
            elif arg.startswith(bunnings.browser.url.URLS['BASE_URL']) or arg.startswith(bunnings.browser.url.URLS['CATEGORY_URL']):
                bunnings.browser.url.add(arg)
            elif arg.startswith('/d=') or arg.startswith('/D=') or arg.startswith('--DEBUG=') or arg.startswith('--debug='):
                sig = arg[int(arg.rfind('=')):]
                bunnings.debug.print(f'DEBUG MODE = {sig}')
            else:
                bunnings.debug.print(f'"argv[{str(i)}] is not a valid parameter')
    else:
        bunnings.debug.print(f'Starting with {bunnings.browser.url.get_default_start_url()}')

    total_url_count = 0
    total_main_categories_count = 0
    total_sub_categories_count = 0
    total_products_count = 0

    for url in bunnings.url.pool:
        bunnings.browser.load_url(url)
        page = bunnings.browser.test_page_level()

        if page == bunnings.browser.PAGE_LEVEL['PAGE_OUR_RANGE']:
            bunnings.parse_our_range()
        elif page == bunnings.browser.PAGE_LEVEL['PAGE_MAIN_CATEGORY']:
            bunnings.parse_main_categories(url)
            total_main_categories_count += 1
        elif page == bunnings.browser.PAGE_LEVEL['PAGE_SUB_CATEGORY']:
            bunnings.parse_sub_categories(url)
            total_sub_categories_count += 1
        elif page == bunnings.browser.PAGE_LEVEL['PAGE_PRODUCT_LIST']:
            bunnings.parse_product_list(url)
        elif page == bunnings.browser.PAGE_LEVEL['PAGE_ITEM_DETAIL']:
            bunnings.parse_items(url)
            total_products_count += 1
        else:
            bunnings.debug.error(f'{url} | COULD NOT BE PROCESSED')

    bunnings.debug.log(f'Total {total_main_categories_count} main categories, {total_sub_categories_count} sub categories & {total_products_count} products')
