#!/usr/bin/env python3
# coding:utf-8
"""
Name: save_bdtj_to_file.py
Author: murphy
Email: zd_wangfenglin@163.com
Time: 2020/4/5 3:52 下午
Desc:
"""

import os
import json
import datetime
from .bdtongji import BaiduTongJi


account_file = os.path.join(os.path.expanduser("~"), "online_config/baidutongji.json")
current_dir = os.path.dirname(os.path.abspath(__file__))
with open(account_file, 'r') as f:
    account = json.load(f)

bdtj = BaiduTongJi(
    username=account['username'],
    password=account['password'],
    token=account['token'],
)
trend = bdtj.trend(
    site_id=account['site_id'],
    end_date=str(datetime.date.today()).replace("-", ""),
    start_date='20190301',
    method="trend/time/a",
    metrics=bdtj.matrix['trend'],
    gran='day',
    visitor='new',
)
trend.to_csv(os.path.join(current_dir, 'bdtj/trend.csv'))

all_source = bdtj.all_source(
    site_id=account['site_id'],
    end_date=str(datetime.date.today()).replace("-", ""),
    start_date='20190301',
    method="source/all/a",
    metrics=bdtj.matrix['all_source'],
    gran='day',
)
all_source.to_csv(os.path.join(current_dir, 'bdtj/all_source.csv'))
