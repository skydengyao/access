# _*_ coding: utf-8 _*_

import os
import requests
import re
from lxml import etree

from util.config import SCI_HUB, NCBI, NCBI_BASE, BASE_DIR
from util.logger import Logger

TIMEOUT = 30

log = Logger(__name__, "logs/download.log").getLogger()


def download_pdf_url(uid, url):
    """
    根据URL下载文档
    """
    try:
        r = requests.get(url, timeout=TIMEOUT)
        print('status: ', r.status_code)
        print(r.headers)
        r.raise_for_status()
        pdf = uid + '.pdf'
        path = BASE_DIR + pdf
        with open(path, "wb") as f:
            f.write(r.content)
        return True
    except Exception as e:
        log.debug("access %s failed" % url)
        return False


def download_sci_doi(uid, doi, proxy, header):
    """
    根据DOI在SCI HUB上下载文档
    """
    try:
        url = SCI_HUB + doi
        r = requests.get(url, proxies=proxy, headers=header, timeout=TIMEOUT)
        r.raise_for_status()
        pdf = uid + '.pdf'
        path = BASE_DIR + pdf
        with open(path, "wb") as f:
            f.write(r.content)
        return True
    except Exception as e:
        log.debug("access %s failed" % url)
        return False


def get_sci_pbmd_url(pbmd, proxy, header):
    """
    根据PMID在SCI HUB上获取对应的下载地址
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
    try:
        url = SCI_HUB + url
        r = requests.get(url, proxies=proxy, headers=header, timeout=TIMEOUT)
        r.raise_for_status
        html = r.content
        tree = etree.HTML(html)
        pdf_url = tree.xpath('.//div[@id="content"]/iframe/@src')[0]
        return pdf_url
    except Exception as e:
        log.debug("access %s failed" % url)
        return None


def download_sci_url(uid, url, proxy, header):
    pdf_url = get_sci_url_pdf(url, proxy, header)
    if pdf_url:
        return download_pdf_url(uid, pdf_url)
    return False


def get_html_doi(url):
    """
    在网页中提取DOI
    """
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
    """
    在网页中提取PMID
    """
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
    """
    根据网页提取的DOI，在SCI HUB中下载文档
    """
    doi_list = get_html_doi(url)
    if doi_list:
        if len(doi_list) > 0:
            doi = doi_list[0]
            ret = download_sci_doi(uid, doi, proxy, header)
            if ret:
                return True
    return False


def download_sci_pbmd(uid, pbmd, proxy, header):
    """
    在SCI HUB上根据PMID下载文档
    """
    url = get_sci_pbmd_url(pbmd, proxy, header)
    if url:
        return download_pdf_url(uid, url)
    return False


def download_html_with_pbmd(uid, url, proxy, header):
    """
    根据PMID在SCI HUB上下载文档
    """
    pbmd_list = get_html_pbmd(url)
    if pbmd_list:
        for pbmd in pbmd_list:
            ret = download_sci_pbmd(uid, pbmd, proxy, header)
            if ret:
                return True
    return False


def get_ncbi_pbmd_url(pbmd, proxy, header):
    try:
        url = NCBI + pbmd
        r = requests.get(url, proxies=proxy, headers=header, timeout=TIMEOUT)
        r.raise_for_status()
        html = r.content
        tree = etree.HTML(html)
        elements = tree.xpath('.//div[@class="aux"]/div[@class="resc status"]')
        if len(elements) > 1:
            free_url = elements[1].xpath('./a/@href')
            return NCBI_BASE + free_url
    except Exception as e:
        log.debug("access %s failed" % pbmd)
    return None


def get_ncbi_free_url(url, proxy, header):
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
    """
    valid_url = get_ncbi_pbmd_url(pbmd, proxy, header)
    if valid_url:
        pdf_url = get_ncbi_free_url(pbmd, proxy, header)
        if pdf_url:
            download_pdf_url(uid, pdf_url)

