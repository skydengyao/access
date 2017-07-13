# _*_ coding: utf-8 _*_

import requests
import re
from lxml import etree
from selenium import webdriver

from util.utils import check_directory, update_download_file, wait_for_download
from util.config import SCI_HUB, NCBI, NCBI_BASE, BASE_DIR
from util.logger import Logger

TIMEOUT = 30

log = Logger(__name__, "logs/download.log").getLogger()


def download_pdf_url(uid, url, headers):
    """
    直接通过请求访问目标URL
    :param uid:
    :param url:
    :param headers:
    :return:
    """
    status = 0
    try:
        r = requests.get(url, headers=headers, timeout=TIMEOUT)
        status = r.status_code
        print('status: ', r.status_code)
        r.raise_for_status()
        pdf = uid + '.pdf'
        path = BASE_DIR + pdf
        with open(path, "wb") as f:
            f.write(r.content)
        return True
    except Exception as e:
        log.debug("access %s failed with status %s" %(url, status))
        return False


def browser_download(uid, url, number='0'):
    """
    通过浏览器直接访问目标URL
    :param url:
    :param id: 序列ID
    :param number: 子目录名
    :return:
    """
    options = webdriver.ChromeOptions()
    options.add_experimental_option("prefs", {
        "download.default_directory": "%s%s" %(BASE_DIR, number),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    })

    path = check_directory(BASE_DIR, number)
    br = webdriver.Chrome(chrome_options=options)
    try:
        br.get(url)
        wait_for_download(path)
        update_download_file(BASE_DIR, path, uid)
        br.close()
        return True
    except Exception as e:
        log.debug("access %s failed" % url)
        br.close()
        return False


def download_sci_doi(uid, doi, proxy, header):
    """
    根据DOI在SCI HUB上下载文档
    :param uid: 文档ID
    :param doi: 文档DOI
    :param proxy: 代理信息
    :param header: 头部信息
    :return:
    """
    status = 0
    try:
        url = SCI_HUB + doi
        r = requests.get(url, proxies=proxy, headers=header, timeout=TIMEOUT)
        status = r.status_code
        r.raise_for_status()
        pdf = uid + '.pdf'
        path = BASE_DIR + pdf
        with open(path, "wb") as f:
            f.write(r.content)
        return True
    except Exception as e:
        log.debug("access %s failed with status %s" %(url, status))
        return False


def get_sci_pbmd_url(pbmd, proxy, header):
    """
    根据PMID在SCI HUB上获取对应的下载地址
    :param pbmd: 文档pubmed信息
    :param proxy: 代理信息
    :param header: 头部信息
    :return:
    """
    param = {"request": pbmd,
             "sci-hub-plugin-check": ""}
    try:
        r = requests.post(SCI_HUB, param, headers=header, proxies=proxy, timeout=TIMEOUT)
        r.raise_for_status()
        html = r.content
        tree = etree.HTML(html)
        pdf_url = tree.xpath('.//div[@id="content"]/iframe/@src')[0]
        return pdf_url
    except Exception as e:
        log.debug("access pbmd %s failed" % pbmd)
        return None


def get_sci_url_pdf(url, proxy, header):
    """
    将目标URL直接采用SCI_HUB进行请求访问
    :param url:目标URL
    :param proxy: 代理
    :param header: 头部信息
    :return:
    """
    status = 0
    try:
        url = SCI_HUB + url
        r = requests.get(url, proxies=proxy, headers=header, timeout=TIMEOUT)
        status = r.status_code
        r.raise_for_status
        html = r.content
        tree = etree.HTML(html)
        pdf_url = tree.xpath('.//div[@id="content"]/iframe/@src')[0]
        return pdf_url
    except Exception as e:
        log.debug("access %s failed with status %s" %(url, status))
        return None


def download_sci_url(uid, url, proxy, header):
    """
    先通过SCI_HUB获取到目标的PDF现在地址，然后通过直连请求下载
    :param uid: 文档ID号
    :param url: 目标URL
    :param proxy: 代理
    :param header: 头部信息
    :return:
    """
    pdf_url = get_sci_url_pdf(url, proxy, header)
    if pdf_url:
        return download_pdf_url(uid, pdf_url)
    return False


def get_html_doi(url):
    """ 在网页中提取DOI """
    try:
        r = requests.get(url, timeout=TIMEOUT/2)
        r.raise_for_status()
        text = r.content.decode('utf-8')
        regex = r'.*?[DOI|doi][:=](\s+)?([0-9a-zA-Z./]{5,})'
        ret = re.findall(regex, text)
        return ret if len(ret) > 0 else None
    except Exception as e:
        log.debug("access %s failed" % url)
        return None


def get_html_pbmd(url):
    """ 在网页中提取PMID """
    try:
        r = requests.get(url, timeout=TIMEOUT)
        r.raise_for_status()
        text = r.content
        regex = r'.*?[pmid|PMID]:\s+?([0-9]{5,})'
        ret = re.findall(regex, text)
        return ret[0] if len(ret) > 0 else None
    except Exception as e:
        log.debug("access %s failed" % url)
        return None


def download_html_with_doi(uid, url, proxy, header):
    """ 根据网页提取的DOI，在SCI HUB中下载文档 """
    doi_list = get_html_doi(url)
    if doi_list:
        if len(doi_list) > 0:
            doi = doi_list[0]
            ret = download_sci_doi(uid, doi, proxy, header)
            if ret:
                return True
    return False


def download_sci_pbmd(uid, pbmd, proxy, header):
    """ 在SCI HUB上根据PMID下载文档 """
    url = get_sci_pbmd_url(pbmd, proxy, header)
    if url:
        return download_pdf_url(uid, url)
    return False


def download_html_with_pbmd(uid, url, proxy, header):
    """ 根据PMID在SCI HUB上下载文档 """
    pbmd_list = get_html_pbmd(url)
    if pbmd_list:
        for pbmd in pbmd_list:
            ret = download_sci_pbmd(uid, pbmd, proxy, header)
            if ret:
                return True
    return False


def get_ncbi_pbmd_url(pbmd, proxy, header):
    """
    在NCBI上根据pubmed获取文档下载地址
    :param pbmd: 文档pubmed信息
    :param proxy: 代理信息
    :param header: 头部信息
    :return:
    """
    status = 0
    try:
        url = NCBI + pbmd
        r = requests.get(url, proxies=proxy, headers=header, timeout=TIMEOUT)
        status = r.status_code
        r.raise_for_status()
        html = r.content
        tree = etree.HTML(html)
        elements = tree.xpath('.//div[@class="aux"]/div[@class="resc status"]')
        if len(elements) > 1:
            free_url = elements[1].xpath('./a/@href')
            return NCBI_BASE + free_url
    except Exception as e:
        log.debug("access %s failed with status %s" %(pbmd, status))
    return None


def get_ncbi_free_url(url, proxy, header):
    """
    根据NCBI上的免费下载获取文档目标URL
    :param url:
    :param proxy:
    :param header:
    :return:
    """
    try:
        r = requests.get(url, proxies=proxy, headers=header, timeout=TIMEOUT)
        r.raise_for_status()
        html = r.content
        tree = etree.HTML(html)
        pdf_url = tree.xpath('//div[@class="summary sec"]/h6/a/@href')
        return pdf_url
    except Exception as e:
        log.debug("access %s faild" % url)
        return None


def download_ncbi_pbmd(uid, pbmd, proxy, header):
    """
    采用NCBI对PMID下载文档
    :param uid: 文档ID
    :param pbmd: 文档pubmed
    :param proxy: 代理信息
    :param header: 头部信息
    :return:
    """
    valid_url = get_ncbi_pbmd_url(pbmd, proxy, header)
    if valid_url: # 获取到有效URL
        pdf_url = get_ncbi_free_url(pbmd, proxy, header)
        if pdf_url: # 能获取到目标URL
            download_pdf_url(uid, pdf_url)


if __name__ == '__main__':

    url = 'https://www.researchgate.net/profile/Vivekananda_Sunkari/publication/' \
          '259456487_Selective_blockade_of_estrogen_receptor_beta_improves_wound_' \
          'healing_in_diabetes/links/00b7d532250039187c000000/Selective-blockade-of-estrogen-' \
          'receptor-beta-improves-wound-healing-in-diabetes.pdf'
    browser_download(url, '0', '0')

