# _*_ coding: utf-8 _*_

from random import randint
from queue import Queue

from util.config import USER_AGENT
from util.utils import set_expire


class AgentScheduler(object):
    def __init__(self, q):
        self.size = len(USER_AGENT)
        self.q = q
        index = q.get() if not q.empty() else 0
        self.index = int(self.size/2) if index == 0 else index
        self.direction = True if self.index % 2 == 0 else False

    def get_user_agent(self):
        index = randint(0, self.index-1) if self.direction else randint(self.index, self.size-1)
        self.q.put(index)
        return USER_AGENT[index]


# class ProxyScheduler(object):
#     def __init__(self, http_queue, https_queue):
#         self.http = check_http_proxy(http_queue, 3)
#         if not https_queue.empty:
#             self.https = https_queue.get()
#             https_queue.put(self.https)  # 即取即入
#         else:
#             self.https = None
#
#     def get_proxy(self):
#         proxies = {}
#         value = randint(0, PROXY_MAX_VALUE)
#         mode = True if 0 < value <= PROXY_MAX_VALUE * 0.80 else False
#
#         if self.http is not None:
#             proxies["http"] = self.http
#
#         if not mode and self.https is not None:
#             proxies["https"] = self.https
#
#         return proxies if len(proxies) > 0 else None


class HeaderInfo(object):
    def __init__(self, agent_queue):
        self.schedule = AgentScheduler(agent_queue)
        self.header = {}

    def set_header(self):
        self.header['accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        self.header['user-agent'] = self.schedule.get_user_agent()
        self.header['Connection'] = 'keep-alive'
        self.header['Accept-Encoding'] = 'gzip, deflate, br'
        self.header['accept-language'] = 'zh-CN,zh;q=0.8'

    def get_header(self):
        self.set_header()
        return self.header


class GoogleScholarHeader(HeaderInfo):
    def __init__(self, agent_queue):
        HeaderInfo.__init__(self, agent_queue)

    def get_header(self):
        self.set_header()
        self.header['host'] = 'scholar.google.com'
        return self.header


class UserData(object):
    def __init__(self, keys):
        self.keywords = keys
        self.param = {}

    def set_request(self):
        self.param["start"] = 0  # 默认获取第一页
        self.param["hl"] = "zh-CN"
        self.param["as_sdt"] = "0"

        q = '+'.join(self.keywords)
        self.param["q"] = q
        size = len(self.keywords)
        self.param["oq"] = self.keywords[0] if size > 0 else ""
        return self.param

    def save_request(self, r):
        p = r.pipeline()
        p.hset(self.param["q"], "q", self.param["q"])
        p.hset(self.param["q"], "hl", self.param["hl"])
        p.hset(self.param["q"], "as_sdt", self.param["as_sdt"])
        p.hset(self.param["q"], "oq", self.param["oq"])
        p.hset(self.param["q"], "start", self.param["start"])
        p.expireat(self.param["q"], set_expire())
        p.execute()


if __name__ == "__main__":
    agent_queue = Queue()
    agent_queue.put(3)
    google = GoogleScholarHeader(agent_queue)
    header = google.get_header()
    print(header)
