# _*_ coding: utf=8 _*_

from time import sleep
import json

from control.rabbit_consumer import RabbitMQConsumer
from control.rabbit_producer import RabbitMQProducer
from control.mysql import MySQLClient, DownloadClient
from util.config import DOWNLOADPDF, DOWNLOADHTML, DOWNLOADNCBI, DOWNLOADDOI, \
    DOWNLOADPMID, PDF2TXT, DOWNLOADBRW
from core.download import download_pdf_url, download_html_with_doi, browser_download
from core.download import download_html_with_pbmd, get_html_pbmd, download_ncbi_pbmd
from core.download import download_sci_url
from util.logger import Logger
from util.info import HeaderInfo
from util.utils import dispatch_sleep_time

log = Logger(__name__, 'logs/download_consume.log').getLogger()


class DownloadConsume(RabbitMQConsumer):
    def __init__(self, data_base, table_name, queue_name, q, number=0):
        RabbitMQConsumer.__init__(self, queue_name, q)
        self.mysql = MySQLClient(data_base, table_name)
        self.download = DownloadClient(data_base, "download", 0)
        self.header = HeaderInfo(q)  # 采用普通的头部信息
        self.number = number

    def start_consuming(self):
        self.add_on_cancel_callback()
        self._consumer_tag = self.channel.basic_consume(self.on_message, self.queue_name, no_ack=False)

    def on_message(self, ch, method, properties, body):
        param = json.loads(body.decode("utf-8"))
        param["proxy"] = self.db.get()
        param["header"] = self.header.get_header()
        uid = param.get("id", None)
        url = param.get("url", None)
        pmid = param.get("pmid", None)
        ret = False
        try:
            if self.queue_name == DOWNLOADPDF:  # 直连下载模式
                ret, status = download_pdf_url(uid, url, param["header"])
                if not ret and status == 429 or status == 408 or status == 401:  # 转发至直接采用浏览器访问模式
                    is_find = self.download.find("title", "url", param, 0)
                    if not is_find:  # 若是未查询到相同数据
                        self.download.insert(param, 0)
            elif self.queue_name == DOWNLOADBRW:  # 浏览器下载
                ret = browser_download(uid, url, str(self.number))
            elif self.queue_name == DOWNLOADDOI:
                # ret = download_html_with_doi(uid, url, param["proxy"], param["header"])
                pass
            elif self.queue_name == DOWNLOADPMID:
                # ret = download_html_with_pbmd(uid, url, param["proxy"], param["header"])
                # if not ret:
                #     pmid = get_html_pbmd(url)
                # if pmid:  # 获取有效PMID
                #     param["pmid"] = pmid
                #     producer = RabbitMQProducer(DOWNLOADNCBI)
                #     producer.produce(param)
                pass
            elif self.queue_name == DOWNLOADHTML:  # SCI_HUB访问URL方式
                ret, status = download_sci_url(uid, url, param["proxy"], param["header"])
                if not ret and status == 429 or status == 408 or status == 401 or status == 0:
                    is_find = self.download.find("title", "url", param, 1)
                    if not is_find:
                        self.download.insert(self.param, 1)
            elif self.queue_name == DOWNLOADNCBI:
                if pmid:  # 获取有效PMID
                    ret = download_ncbi_pbmd(uid, pmid, param["proxy"], param["header"])

            path = uid + '.pdf'
            if ret:  # 校验是否能下载文章，此处能下载PDF文档
                pid = self.mysql.get_id("title", "author", "journal",
                                        (param.get("title"), param.get("author"), param.get("journal")))
                if pid:  # 读取原有id， 避免现有ID覆盖
                    uid = pid
                self.mysql.update("path", (uid, path))

                # 用于后续全文检索处理
                index_param = {"uid": uid}
                pdf2txt_producer = RabbitMQProducer(PDF2TXT)
                pdf2txt_producer.produce(index_param)
            else:  # 若是未能下载文章则直接丢弃, 让后续调度处理
                pass
        except Exception as e:
            log.debug("download %s failed" % url)

        sleep(dispatch_sleep_time()*2)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def consume(self):
        self.conn = self.connect()
        self.conn.ioloop.start()


if __name__ == "__main__":
    from queue import Queue
    q = Queue()
    consumer = DownloadConsume("info", "paper", "downhtml", q)
    consumer.consume()


