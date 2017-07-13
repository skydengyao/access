# _*_ coding:utf-8 _*_

from queue import Queue

# 全局队列
QUEUE = Queue()

# 存储目录
BASE_DIR = '/home/liuyong/Documents/pdfs/'

# 优先级调度睡眠时间
PRIORI_CPUTIME = 3
MIDDLE_CPUTIME = 3*4
LAGBEHIND_CPUTIME = 3*8

#消息队列控件
EXCHANGE = 'message'
EXCHANGE_TYPE = 'direct'

# 消息队列名称
PRIORI = 'priori'
MIDDLE = 'middle'
LAGBEHIND = 'lagbehind'
DOWNLOADPDF = 'downpdf'
DOWNLOADHTML = 'downhtml'
DOWNLOADNCBI = 'downncbi'
DOWNLOADDOI = 'downdoi'
DOWNLOADPMID = 'downpmid'
DOWNLOADBRW = 'downbrw'
PDF2TXT = 'pdf2txt'

# MongoDB 表名
VALID_PROXY = 'valid_proxy'
RAW_PROXY = 'raw_proxy'

# RabbitMQ 授权
AUTHENTICATE = {"user": "liuyong", "password": "123456"}

MONGODB = {"host": "localhost", "port": 27017, "table": "valid_proxy"}
RABBITMQ = {"host": "localhost", "port": 5672}
REDIS = {"host": "localhost", "port": 6379}
MYSQL = {"host": "localhost", "user": "guest", "password": "123456@Guest"}

# 代理最少个数
MINIMUM_SIZE = 30

# IP代理调度函数
PROXY_SERVICE = ["kdldiff_proxy", "doublesix_proxy", "goubanjia_proxy",
                 "data5u_proxy", "ipaddress_proxy", "us_proxy", "ip181_proxy", "db_proxy",
                 "swei360_proxy", "ip3366_proxy", "ssl_proxy", "listplus_proxy", "listplushttp_proxy"]

# 间隔时间
IN_MEM_MINUTES = 3

# 访问URL
BASE_URL = "https://scholar.google.com/scholar"
# 访问网页数
PAGES = 3*10

# 访问SCI_HUB
SCI_HUB = "http://sci-hub.cc/"
# 访问NCBI
NCBI = "https://www.ncbi.nlm.nih.gov/pubmed/"
NCBI_BASE = "https://www.ncbi.nlm.nih.gov"

# 代理默认数值，仅由于随机数选择
PROXY_MAX_VALUE = 100

GOOGLE_SCHOLAR_HEADER = {
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'host': 'scholar.google.com',
}

# 用户代理
USER_AGENT = [
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
        "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:54.0) Gecko/20100101 Firefox/54.0"]

