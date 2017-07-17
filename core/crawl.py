# _*_ coding:utf-8 _*_

import requests
import re
from uuid import uuid4

from util.config import BASE_URL, DOWNLOADPDF, DOWNLOADHTML, PAGES
from util.logger import Logger
from util.utils import get_tree, split_elements
from util.utils import check_url_type
from control.rabbit_producer import ProduceService
from control.mysql import MySQLClient, CacheClient, DataClient

requests.packages.urllib3.disable_warnings()

log = Logger(__name__, log_name="logs/crawl.log").getLogger()


class GoogleScholarCrawl(object):
    def __init__(self, message):
        proxy = message.get("proxy")
        self.proxies = {"https": "http://{proxy}".format(proxy=proxy)} if proxy else None
        self.headers = message.get("header", None)
        self.params = message.get("param", None)
        self.start = self.params.get("start", 0) if self.params else 0
        self.db = MySQLClient("info", "paper")
        self.cache = CacheClient("info", "middle")
        self.message = DataClient("info", "message")

    def get(self):
        if not self.params:
            print("parmas : ", self.params)
            return

        if not self.proxies: # 避免暴露自身IP地址
            print("proxy: ", self.proxies)
            is_find = self.cache.find('start', 'q', 'oq', self.params)
            if not is_find:  # 数据库中不存在该记录
                self.cache.insert(self.params)
            return

        tree = get_tree(url=BASE_URL, params=self.params, proxies=self.proxies, headers=self.headers)
        if type(tree) == str:  # 访问失败
            if self.start == 0:
                is_find = self.cache.find('start', 'q', 'oq', self.params)
                if not is_find: # 数据库中不存在该记录
                    self.cache.insert(self.params)

                is_find = self.message.find('start', 'q', 'oq', self.params)
                if not is_find:
                    self.message.insert(self.params)
            log.debug("search %s data failed" % self.params.get("q"))
            return  # 返回不进行后续处理
        else:
            elements = tree.xpath('.//div[@id="gs_bdy"]//div[@class="gs_r"]')
            for element in elements:
                self.process_element(element)

            if self.start == 0:  # 第一次时需要传递消息
                is_find = self.message.find('start', 'q', 'oq', self.params)
                if not is_find:
                    self.message.insert(self.params)
        print("test")
        if 0 < self.start < PAGES:  # 处于设置的范围内，则转发请求
            is_find = self.cache.find('start', 'q', 'oq', self.params)
            if not is_find:
                self.params["start"] = self.start+10
                self.cache.insert(self.params)

    def process_element(self, element):
        try:
            sub = element.xpath('./div')
            down_url = None
            if len(sub) > 1:
                down_url = sub[0].xpath('.//div[@class="gs_ggsd"]/a/@href')[0].strip()
                e = sub[1]
            else:
                e = sub[0]
            title_e = e.xpath('./h3[@class="gs_rt"]/a')[0]
            title = title_e.xpath('string(.)')
            url = e.xpath('./h3[@class="gs_rt"]/a/@href')[0].strip()
            info_e = e.xpath('./div[@class="gs_a"]')[0]
            info = info_e.xpath('string(.)')
            author, journal, year, press = split_elements(info)
            snapshot_e = e.xpath('./div[@class="gs_rs"]')[0]
            snapshot = snapshot_e.xpath('string(.)')
            quot = re.split(':|：', e.xpath('./div[@class="gs_fl"]/a/text()')[0])[1].strip()

            gid = self.db.get_id('title', 'author', 'journal', (title, author, journal))
            if not gid:
                uid = uuid4()
                self.db.insert((str(uid), title, url, author, journal, int(year), press, snapshot, int(quot), ''))
                down_url_type = check_url_type(down_url)
                download_value = {"id": str(uid), "url": down_url, "title": title,
                                  "author": author, "journal": journal}
                print("type: ", down_url_type)
                if down_url_type == 0:
                    download_producer = ProduceService(DOWNLOADHTML)
                    download_producer.produce(download_value)
                elif down_url_type == 1:
                    down_producer = ProduceService(DOWNLOADPDF)
                    down_producer.produce(download_value)
            else:  # 更新引用量
                self.db.update("quot", (quot, gid))
        except Exception as e:
            log.debug("extract page %s failed" % self.start)


if __name__ == "__main__":
    loader = {"q": "BRAF V600E",
              "hl": "zh-CN",
              "as_sdt": "0,5",
              "oq": "braf+v600e"}

    proxies = {"https": "http://207.75.166.40:8080"}
    header = {'Connection': 'keep-alive',
              'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0',
              'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
              'Accept-Encoding': 'gzip, deflate, br',
              'Accept-Language': 'zh-CN,zh;q=0.8',
              'host': 'scholar.google.com',
              }

    r = requests.get("https://scholar.google.com/scholar", params=loader,
                     headers=header, proxies=proxies, timeout=30, verify=False)
    print(r.status_code)
    print(r.text)

