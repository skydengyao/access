# _*_ coding: utf-8 _*_

import re
import os
from random import uniform
from time import sleep
from time import time
from time import clock
import hashlib
import requests
from lxml import etree
from selenium import webdriver
from datetime import datetime
import shutil
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


def check_directory(base, sub):
    path = os.path.join(base, sub)
    if not os.path.exists(path):
        os.mkdir(path)
    return path


def update_download_file(base, path, id):
    try:
        files = os.listdir(path)
        for f in files:
            if f.endswith('.pdf'):
                shutil.move(os.path.join(path, f), os.path.join(base, (id+'.pdf')))
        shutil.rmtree(path)
    except Exception as e:
        log.debug("update %s failed" % path)


def wait_for_download(path):
    try:
        times = 3
        while times >= 0:
            files = os.listdir(path)
            for f in files:
                if f.endswith('.pdf'):
                    return
            sleep(10)
            times = times-1
    except Exception as e:
        log.debug("wait % download failed" %path)


def current_time():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


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
        return "404"


def get_html_text(url, **kwargs):
    try:
        r = requests.get(url, headers=header, timeout=30)
        r.raise_for_status()  # 针对 40X 或 50X 抛出异常
        r.encoding = r.apparent_encoding
        return r.text
    except Exception as e:
        log.debug("access %s failed" % url)
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
    #url = 'https://www.researchgate.net/profile/Robert_Steen/publication/14988409_A_genetic_linkage_map_of_the_mouse_current_applications_and_future_prospects/links/0deec5165ac5d7ea6a000000/A-genetic-linkage-map-of-the-mouse-current-applications-and-future-prospects.pdf'
    url = 'https://www.researchgate.net/profile/Frank_Sharp/publication/11276136_Genomic_responses_of_the_brain_to_ischemic_stroke_intracerebral_haemorrhage_kainate_seizures_hypoglycemia_and_hypoxia/links/591e082eaca272d31bcda35a/Genomic-responses-of-the-brain-to-ischemic-stroke-intracerebral-haemorrhage-kainate-seizures-hypoglycemia-and-hypoxia.pdf'
    url = 'https://www.researchgate.net/profile/Rudi_Beschorner/publication/11350831_Infiltrating_CD14_monocytes_and_expression_of_CD14_by_activated_parenchymal_microgliamacrophages_contribute_to_the_pool_of_CD14_cells_in_ischemic_brain_lesions/links/0fcfd50c9c3ecc34cc000000.pdf'
    try:
        r = requests.get(url)
        print('status code: ', r.status_code)
        r.raise_for_status()
    except Exception as e:
        print("here now")
