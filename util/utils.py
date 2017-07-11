# _*_ coding: utf-8 _*_

import re
from random import uniform
from time import sleep
from time import time
from time import clock
import hashlib
import requests
from lxml import etree
from selenium import webdriver
from datetime import datetime

from util.config import IN_MEM_MINUTES
from util.logger import Logger
from control.mongodb import DEFAULT_FIELD

requests.packages.urllib3.disable_warnings()
log = Logger(__name__, "logs/utils.log").getLogger()


header = {'Connection': 'keep-alive',
          'Cache-Control': 'max-age=0',
          'Upgrade-Insecure-Requests': '1',
          'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko)',
          'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
          'Accept-Encoding': 'gzip, deflate, sdch',
          'Accept-Language': 'zh-CN,zh;q=0.8',
          }


def create_id():
    m = hashlib.md5(str(clock()).encode('utf-8'))
    return m.hexdigest()


def current_time():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def convert_time(span):
    return datetime.strptime(span, '%Y-%m-%d %H:%M:%S')


def check_http_proxy(http_queue, times):
    for i in range(times):
        if not http_queue.empty():
            ret = http_queue.get()
            http_queue.put(ret)   # 即取即入
            return ret
        sleep(0.1)
    return None


def dispatch_sleep_time():
    value = uniform(0, 2) * 2
    return value


def set_expire():
    now = int(time())
    expire = now + IN_MEM_MINUTES * 60 + 10
    return expire


def get_tree(url, params, proxies, headers):
    try:
        r = requests.get(url=url, params=params, headers=headers,
                         proxies=proxies, timeout=30, verify=False)
        r.raise_for_status()  # 针对 40X 或 50X 抛出异常
        html = r.content
        return etree.HTML(html)
    except Exception as e:
        key = ""
        if params:
            key = params.get("q") if params.get("q") else ""
        log.debug("access %s failed" % key)
        return "404"


def get_html_tree(url, **kwargs):
    try:
        r = requests.get(url=url, headers=header, timeout=30)
        r.raise_for_status()  # 针对 40X 或 50X 抛出异常
        html = r.content
        return etree.HTML(html)
    except Exception as e:
        log.debug("access %s failed" % url)
        # return r.status_code
        return "404"


def get_html_text(url, **kwargs):
    try:
        r = requests.get(url, headers=header, timeout=30)
        r.raise_for_status()  # 针对 40X 或 50X 抛出异常
        r.encoding = r.apparent_encoding
        # print("value: ", r.text)
        return r.text
    except Exception as e:
        log.debug("access %s failed" % url)
        # return r.status_code
        return "404"


def open_browser(url, **kwargs):
    br = webdriver.Chrome()
    try:
        br.get(url)
        return br
    except Exception as e:
        log.debug("access %s failed" % url)
        br.close()
    return None


def check_valid_proxy(proxy):
    proxies = {"https": "http://{proxy}".format(proxy=proxy.get(DEFAULT_FIELD))}
    try:
        r = requests.get("https://www.google.com.hk/", proxies=proxies, headers=header, timeout=30, verify=False)
        if r.status_code == 200:
            return True
        return False
    except Exception as e:
        log.debug("test google with proxy %s failed" % proxy)
        return False


def verify_proxy_format(proxy):
    regex = r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}"
    return True if re.findall(regex, proxy) else False


def split_elements(content):
    ret = content.split('-')
    size = len(ret)
    author = ret[0].strip()
    journal = 'journal'  # set default
    if size >= 2:
        tmp = ret[1].split(',')
        if len(tmp) >= 2:
            journal = tmp[0].strip()
            year = tmp[1].strip()
        else:
            year = tmp[0].strip()
    press = ret[2].strip()
    year = check_year(year)
    return author, journal, year, press


def check_year(content):
    if content.isdigit():
        if len(content) == 4:
            return content

    return get_digits(content)


def get_digits(content):
    regex = r'.*([0-9]{4}).*'
    ret = re.findall(regex, content)
    return ret[0] if len(ret) > 0 else '0'


def check_url_type(url):
    url_type = -1
    if not url:
        return url_type
    url_type = 1 if url.endswith('pdf') or url.endswith('PDF') else 0
    return url_type


if __name__ == "__main__":
    text = """
    <h1>Improved Survival with Vemurafenib in Melanoma with BRAF V600E Mutation</h1>
    <p class="authors">
    <p class="citationLine">
    <span class="citation">N Engl J Med 2011; 364:2507-2516</span>
    <a href="/toc/nejm/364/26/">June 30, 2011</a>
    <span class="doi">DOI: 10.1056/NEJMoa1103782</span>
    </p>
    """
    # regex = r"[DOI|dio]:\s+?([0-9a-zA-Z./]*)"
    # ret = re.findall(regex, text)
    # print(ret)

    text = 'hewoll  woosls , sklsl.d ,,,s 2004,.**&&& hell'
    print(get_digits(text))
