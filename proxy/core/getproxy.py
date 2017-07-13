# _*_ coding: utf-8 _*_

import requests
import re
from time import sleep

from util.utils import get_html_text, get_html_tree, open_browser
from util.utils import header, dispatch_sleep_time
from util.logger import Logger

log = Logger(__name__, "logs/get_proxy.log").getLogger()


class GetProxy(object):
    def __init__(self):
        pass

    @staticmethod
    def kuaidaili_proxy(number=8):
        url = "http://www.kuaidaili.com/proxylist/{page}/"
        target_url = [url.format(page=page) for page in range(1, number)]
        for target in target_url:
            tree = get_html_tree(target)
            try:
                proxy_list = tree.xpath('.//div[@id="index_free_list"]//tbody/tr')
                for proxy in proxy_list:
                    yield ':'.join(proxy.xpath('./td/text()')[0:2])
            except Exception as e:
                log.debug("%s get xpath failed" % target)
            sleep(dispatch_sleep_time())

    @staticmethod
    def kdldiff_proxy(number=8):
        url_list = ["http://www.kuaidaili.com/free/outha/{page}/",
                    "http://www.kuaidaili.com/free/outtr/{page}/"]
        target_list = [url.format(page=page) for url in url_list for page in range(1, number)]
        for target in target_list:
            tree = get_html_tree(target)
            try:
                proxy_list = tree.xpath('.//div[@id="list"]//tbody/tr')
                for proxy in proxy_list:
                    yield ':'.join(proxy.xpath('./td/text()')[0:2])
            except Exception as e:
                log.debug("%s get xpath failed" % target)
            sleep(dispatch_sleep_time())

    @staticmethod
    def doublesix_proxy(number=80):
        url = "http://m.66ip.cn/mo.php?sxb=&tqsl={}&port=&export=&ktip=&sxa=&submit=%CC%E1++%C8%A1&textarea=".format(number)
        html = get_html_text(url)
        proxy_list = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}', html)
        for proxy in proxy_list:
            yield proxy

    @staticmethod
    def youdaili_proxy(number=1):
        url = "http://www.youdaili.net/Daili/http/"
        tree = get_html_tree(url)
        url_list = tree.xpath('.//div[@class="chunlist"]/ul/li/p/a/@href')[0:number]
        for target in url_list:
            try:
                html = requests.get(target, headers=header, timeout=30).text  # 获取Unicode数据
                proxy_list = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}', html)
                for proxy in proxy_list:
                    yield proxy
            except Exception as e:
                log.debug("%s get xpath failed" % target)
            sleep(dispatch_sleep_time())

    @staticmethod
    def xici_proxy():
        url_list = ['http://www.xicidaili.com/nn',  # 高匿
                    'http://www.xicidaili.com/nt',  # 透明
                    ]
        for url in url_list:
            tree = get_html_tree(url)
            try:
                proxy_list = tree.xpath('.//table[@id="ip_list"]//tr')
                for proxy in proxy_list:
                    yield ':'.join(proxy.xpath('./td/text()')[0:2])
            except Exception as e:
                log.debug("%s get xpath failed" % url)
            sleep(dispatch_sleep_time())

    @staticmethod
    def goubanjia_proxy(number=8):
        url = "http://www.goubanjia.com/free/gwgn/index{page}.shtml"
        for page in range(1, number):
            target = url.format(page=page)
            br = open_browser(target)
            try:
                proxy_list = br.find_elements_by_xpath('.//td[@class="ip"]')
                for proxy in proxy_list:
                    yield proxy.text
            except Exception as e:
                log.debug("%s get xpath failed" % target)
            br.close()

    @staticmethod
    def data5u_proxy(number=8):
        url = "http://www.data5u.com/free/gwpt/index{page}.shtml"
        for page in range(1, number):
            target = url.format(page=page)
            tree = get_html_tree(target)
            try:
                proxy_list = tree.xpath('.//div[@class="wlist"]//ul[@class="l2"]')
                for proxy in proxy_list:
                    yield ':'.join(proxy.xpath('.//li/text()')[0:2])
            except Exception as e:
                log.debug("%s get xpath failed" % target)
            sleep(dispatch_sleep_time())

    @staticmethod
    def xdaili_proxy():
        url = "http://www.xdaili.cn/freeproxy.html"
        br = open_browser(url)
        try:
            proxy_list = br.find_elements_by_xpath('.//tbody[@id="target"]/tr')
            for proxy in proxy_list:
                sub_list = [sub.text for sub in proxy.find_elements_by_xpath('./td')]
                yield ':'.join(sub_list[0:2])
        except Exception as e:
            log.debug("%s get xpath failed" % url)
        br.close()

    @staticmethod
    def ipaddress_proxy():
        url = "http://www.ip-adress.com/proxy_list"
        tree = get_html_tree(url)
        try:
            proxy_list = tree.xpath('.//table[@class="proxylist"]//tr[@class="odd"]')
            for proxy in proxy_list:
                yield proxy.xpath('./td/text()')[0]
        except Exception as e:
            log.debug("%s get xpath failed" % url)

    @staticmethod
    def us_proxy():
        url = "https://www.us-proxy.org/"
        tree = get_html_tree(url)
        try:
            proxy_list = tree.xpath('.//table[@id="proxylisttable"]/tbody/tr')
            for proxy in proxy_list:
                yield ':'.join(proxy.xpath('./td/text()')[0:2])
        except Exception as e:
            log.debug("%s get xpath failed" % url)

    @staticmethod
    def kubobo_proxy(number=8):
        url = "http://www.coobobo.com/free-http-proxy/{page}"
        for page in range(1, number):
            target = url.format(page=page)
            br = open_browser(target)
            try:
                proxy_list = br.find_elements_by_xpath('.//div[@class="col-md-12"]//tbody/tr')
                for proxy in proxy_list:
                    sub_list = [sub.text for sub in proxy.find_elements_by_xpath('./td')]
                    yield ':'.join(sub_list[0:2])
            except Exception as e:
                log.debug("%s get xpath failed" % target)
            br.close()

    @staticmethod
    def ip181_proxy():
        url = "http://www.ip181.com/"
        tree = get_html_tree(url)
        try:
            proxy_list = tree.xpath('//div[@class="row"]//tbody/tr')
            for proxy in proxy_list[1:]:
                yield ':'.join(proxy.xpath('./td/text()')[0:2])
        except Exception as e:
            log.debug("%s get xpath failed" % url)

    @staticmethod
    def swei360_proxy():
        url = ["http://www.swei360.com/free/?stype=3",
               "http://www.swei360.com/free/?stype=4"]
        for target in url:
            tree = get_html_tree(target)
            try:
                proxy_list = tree.xpath('.//div[@id="list"]//tbody/tr')
                for proxy in proxy_list:
                    yield ':'.join(proxy.xpath('./td/text()')[0:2])
            except Exception as e:
                log.debug("%s get xpath failed" % target)
            sleep(dispatch_sleep_time())

    @staticmethod
    def ip3366_proxy(number=8):
        url = "http://www.ip3366.net/?stype=3&page={page}"
        for page in range(1, number):
            target = url.format(page=page)
            tree = get_html_tree(target)
            try:
                proxy_list = tree.xpath('//div[@id="list"]//tbody/tr')
                for proxy in proxy_list:
                    yield ':'.join(proxy.xpath('./td/text()')[0:2])
            except Exception as e:
                log.debug("%s get xpath failed" % target)
            sleep(dispatch_sleep_time())

    @staticmethod
    def kxdaili_proxy(number=8):
        url_list = ["http://www.kxdaili.com/dailiip/1/{page}.html#ip",
                    "http://www.kxdaili.com/dailiip/2/{page}.html#ip"]
        for url in url_list:
            for page in range(1, number):
                target = url.format(page=page)
                tree = get_html_tree(target)
                try:
                    proxy_list = tree.xpath('.//div[@class="tab_c_box buy_tab_box"]//tbody/tr')
                    for proxy in proxy_list:
                        yield ':'.join(proxy.xpath('./td/text()')[0:2])
                except Exception as e:
                    log.debug("%s get xpath failed" % target)
                sleep(dispatch_sleep_time())

    @staticmethod
    def ssl_proxy():
        url = "https://www.sslproxies.org/"
        tree = get_html_tree(url)
        try:
            proxy_list = tree.xpath('.//table[@id="proxylisttable"]/tbody/tr')
            for proxy in proxy_list:
                yield ':'.join(proxy.xpath('./td/text()')[0:2])
        except Exception as e:
            log.debug("%s get xpath failed" % url)

    @staticmethod
    def listplus_proxy(number=4):
        url = "https://list.proxylistplus.com/SSL-List-{page}"
        for page in range(1, number):
            target = url.format(page=page)
            tree = get_html_tree(target)
            try:
                proxy_list = tree.xpath('.//table[@class="bg"]//tr[@class="cells"]')
                for proxy in proxy_list:
                    yield ':'.join(proxy.xpath('./td/text()')[0:2])
            except Exception as e:
                log.debug("%s get xpath failed" % target)
            sleep(dispatch_sleep_time())

    @staticmethod
    def listplushttp_proxy(number=6):
        url = "https://list.proxylistplus.com/Fresh-HTTP-Proxy-List-{page}"
        for page in range(1, number):
            target = url.format(page=page)
            tree = get_html_tree(target)
            try:
                proxy_list = tree.xpath('.//table[@class="bg"]//tr[@class="cells"]')
                for proxy in proxy_list:
                    yield ':'.join(proxy.xpath('./td/text()')[0:2])
            except Exception as e:
                log.debug("%s get xpath failed" % target)
            sleep(dispatch_sleep_time())

    @staticmethod
    def db_proxy(number=20):
        url = "http://proxydb.net/?offset={offset}"
        for page in range(0, number):
            offset = page * 15
            target = url.format(offset=offset)
            tree = get_html_tree(target)
            try:
                proxy_list = tree.xpath('.//table[@class="table table-sm"]/tbody/tr')
                for proxy in proxy_list:
                    yield proxy.xpath('./td/a/text()')[0]
            except Exception as e:
                log.debug("%s get xpath failed" % target)
            sleep(dispatch_sleep_time()*2)


    @staticmethod
    def cool_proxy(number=5):
        url = "http://www.cool-proxy.net/proxies/http_proxy_list/sort:score/direction:desc/page:{page}"
        for page in range(1, number):
            target = url.format(page=page)
            br = open_browser(target)
            try:
                proxy_list = br.find_elements_by_xpath('.//div[@id="main"]/table/tbody/tr')
                for proxy in proxy_list[1:]:
                    sub_list = [sub.text for sub in proxy.find_elements_by_xpath('./td')]
                    yield ':'.join(sub_list[0:2])
            except Exception as e:
                log.debug("%s get xpath failed" % target)
            br.close()
            sleep(dispatch_sleep_time()*2)

    @staticmethod
    def free_proxy(number=5):
        url = "https://free-proxy-list.com/?page={page}&port=&up_time=0"
        for page in range(1, number):
            target = url.format(page=page)
            br = open_browser(target)
            try:
                proxy_list = br.find_elements_by_xpath(
                    './/div[@class="section"]/div[@class="table-responsive"]//tbody/tr')
                for proxy in proxy_list:
                    sub = proxy.find_elements_by_xpath('./td')[0]
                    yield ':'.join([sub.find_element_by_xpath('./a').text, "80"])  # 默认端口为80
            except Exception as e:
                log.debug("%s get xpath failed" % target)
            br.close()
            sleep(dispatch_sleep_time()*2)


if __name__ == "__main__":
    # for e in GetProxy.doublesix_proxy():
    #     print(e)

    # for e in GetProxy.goubanjia_proxy():
    #     print(e)

    # for e in GetProxy.kuaidaili_proxy():
    #     print(e)

    # for e in GetProxy.youdaili_proxy():
    #     print(e)

    # for e in GetProxy.xici_proxy():
    #     print(e)

    # for e in GetProxy.data5u_proxy():
    #     print(e)

    # for e in GetProxy.xdaili_proxy():
    #     print(e)

    # for e in GetProxy.ipaddress_proxy():
    #     print(e)

    # for e in GetProxy.us_proxy():
    #     print(e)

    # for e in GetProxy.kdldiff_proxy():
    #     print(e)

    # for e in GetProxy.kubobo_proxy():
    #     print(e)

    # for e in GetProxy.ip181_proxy():
    #     print(e)

    # for e in GetProxy.swei360_proxy():
    #     print(e)

    # for e in GetProxy.ip3366_proxy():
    #     print(e)

    # for e in GetProxy.kxdaili_proxy():
    #     print(e)

    # proxy_list = getattr(GetProxy, "ip181_proxy")()
    # for e in proxy_list:
    #     print(e)

    # for e in GetProxy.listplus_proxy():
    #     print(e)

    # for e in GetProxy.listplushttp_proxy():
    #     print(e)

    # for e in GetProxy.ssl_proxy():
    #     print(e)

    # for e in GetProxy.db_proxy():
    #     print(e)

    # for e in GetProxy.cool_proxy():
    #     print(e)

    for e in GetProxy.free_proxy():
        print(e)