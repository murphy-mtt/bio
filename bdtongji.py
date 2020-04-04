#!/usr/bin/env python3
# coding:utf-8
"""
Name: bdtongji.py
Author: murphy
Email: zd_wangfenglin@163.com
Time: 2020/4/2 3:07 下午
Desc:
"""


import os
import requests
import json
import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import lifelines


class BaiduTongJi:
    def __init__(self, username, password, token, account_type=1):
        self.api_url = 'https://api.baidu.com/json/tongji/v1/ReportService/getData'
        self.header = {
                "username": username,
                'password': password,
                "token": token,
                "account_type": account_type
            }
        with open(os.path.join(os.path.expanduser("~"), "online_config/baidutuiguang_matrix.json"), 'r') as f:
            m = json.load(f)
        self.matrix = m
        return

    def send_request(self, body):
        request_body = {
            "header": self.header,
            "body": body,
        }
        data = json.dumps(request_body)
        request = requests.post(self.api_url, data)
        response = json.loads(request.text)
        return response

    def trend(self, **kwargs):
        """
        趋势分析
        :return:
        """
        col = kwargs['metrics'].split(',')
        response = self.send_request(kwargs)
        result = response['body']['data'][0]['result']['items']

        ret_date = np.array([i[0] for i in result[0]])
        ret_pv = np.array(result[1])
        df = pd.DataFrame(ret_pv, columns=col)
        df['date'] = ret_date

        return df

    def all_source(self, **kwargs):
        """
        获取百度统计中高"全部来源"数据
        :param kwargs:
        :return: Dataframe
        """
        kwargs['visitor'] = 'old'
        response = self.send_request(kwargs)
        col = kwargs['metrics'].split(', ')
        dates = np.array([i[0] for i in response['body']['data'][0]['result']['items'][0]])
        old_df = pd.DataFrame(response['body']['data'][0]['result']['items'][1], index=dates, columns=col)
        old_df['visitor'] = 'old'

        kwargs['visitor'] = 'new'
        response = self.send_request(kwargs)
        col = kwargs['metrics'].split(', ')
        dates = np.array([i[0] for i in response['body']['data'][0]['result']['items'][0]])
        new_df = pd.DataFrame(response['body']['data'][0]['result']['items'][1], index=dates, columns=col)
        new_df['visitor'] = 'new'
        return pd.concat([new_df, old_df])

    def district_visit(self, **kwargs):
        """
        结果简单没有细节，不进一步挖掘
        :param kwargs:
        :return:
        """
        response = self.send_request(kwargs)
        return response


class SurvivalAnalysis:
    def __init__(self, data_frame):
        self.data_frame = data_frame

    def _callback(self, process, *args):
        method = getattr(self, process, None)
        if callable(method):
            method(*args)

    def all_source_plot(self, **kwargs):
        """
        KaplanMeier fit and plot, using baidutongji all_source dataframe as input
        :param kwargs:
        :return:
        """
        all_source = self.data_frame
        title = kwargs['title']
        path = kwargs['path']
        visitor = (all_source['visitor'] == "new")
        T = all_source["avg_visit_time"]
        kmf = lifelines.KaplanMeierFitter()
        fig, ax = plt.subplots()
        kmf.fit(T[visitor], label="New Visitors")
        kmf.plot(ax=ax)
        kmf.fit(T[~visitor], label="Old Visitors")
        kmf.plot(ax=ax)
        plt.ylim(0, 1)
        plt.title(title)
        plt.savefig(path)

    def coxph(self, **kwargs):
        """
        CoxPH plot using baidutongji all_source dataframe as input.
        :param kwargs:
        :return:
        """
        title = kwargs['title']
        path = kwargs['path']
        fit, ax = plt.subplots()
        cph = lifelines.CoxPHFitter()
        cph.fit(self.data_frame.drop(['visitor'], axis=1), 'avg_visit_time')
        cph.plot(hazard_ratios=True, ax=ax)
        plt.title(title)
        plt.tight_layout()
        plt.savefig(path)


if __name__ == "__main__":
    account_file = os.path.join(os.path.expanduser("~"), "online_config/baidutongji.json")
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
    trend.to_csv('../bdtj_trend.csv')
