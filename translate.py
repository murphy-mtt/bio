#!/usr/bin/env python3
# coding:utf-8
"""
Name: translate.py
Author: murphy
Email: zd_wangfenglin@163.com
Time: 2020/4/3 4:15 下午
Desc:
"""


import sys
import uuid
import requests
import base64
import hashlib
import time
import importlib

importlib.reload(sys)
# sys.setdefaultencoding('utf-8')

YOUDAO_URL_UPLOAD = 'https://openapi.youdao.com/file_trans/upload'
YOUDAO_URL_QUERY = 'https://openapi.youdao.com/file_trans/query'
YOUDAO_URL_DOWNLOAD = 'https://openapi.youdao.com/file_trans/download'
APP_KEY = '5b99b290338302f4'
APP_SECRET = 'fyabUEvXJvd4gE1pq7Bw8zqIhlC38byz'


def truncate(q):
    if q is None:
        return None
    q_utf8 = q.decode("utf-8")
    size = len(q_utf8)
    return q_utf8 if size <= 20 else q_utf8[0:10] + str(size) + q_utf8[size - 10:size]


def encrypt(signStr):
    hash_algorithm = hashlib.sha256()
    hash_algorithm.update(signStr.encode('utf-8'))
    return hash_algorithm.hexdigest()


def do_request(url, data):
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    return requests.post(url, data=data, headers=headers)


def upload():
    f = open(r'文件的路径', 'rb')  # 二进制方式打开文件
    q = base64.b64encode(f.read())  # 读取文件内容，转换为base64编码
    f.close()
    salt = str(uuid.uuid1())
    curtime = str(int(time.time()))
    signStr = APP_KEY + truncate(q) + salt + curtime + APP_SECRET
    sign = encrypt(signStr)

    data = {}
    data['q'] = q
    data['fileName'] = '文件名称'
    data['fileType'] = '文件类型'
    data['langFrom'] = '源语言'
    data['langTo'] = '目标语言'
    data['appKey'] = APP_KEY
    data['salt'] = salt
    data['curtime'] = curtime
    data['sign'] = sign
    data['docType'] = 'json'
    data['signType'] = 'v3'

    response = do_request(YOUDAO_URL_UPLOAD, data)
    print(response.content)


def query():
    flownumber = '文件流水号'
    salt = str(uuid.uuid1())
    curtime = str(int(time.time()))
    signStr = APP_KEY + truncate(flownumber) + salt + curtime + APP_SECRET
    sign = encrypt(signStr)

    data = {}
    data['flownumber'] = flownumber
    data['appKey'] = APP_KEY
    data['salt'] = salt
    data['curtime'] = curtime
    data['sign'] = sign
    data['docType'] = 'json'
    data['signType'] = 'v3'

    response = do_request(YOUDAO_URL_QUERY, data)
    print(response.content)


def download():
    flownumber = '文件流水号'
    salt = str(uuid.uuid1())
    curtime = str(int(time.time()))
    signStr = APP_KEY + truncate(flownumber) + salt + curtime + APP_SECRET
    sign = encrypt(signStr)

    data = {}
    data['flownumber'] = flownumber
    data['downloadFileType'] = '文件下载类型'
    data['appKey'] = APP_KEY
    data['salt'] = salt
    data['curtime'] = curtime
    data['sign'] = sign
    data['docType'] = 'json'
    data['signType'] = 'v3'

    response = do_request(YOUDAO_URL_DOWNLOAD, data)
    print(response.content)


if __name__ == '__main__':
    upload()
    query()
    download()
