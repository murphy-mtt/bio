#!/usr/bin/env python3
# coding:utf-8
"""
Name: bdtongji.py
Author: murphy
Email: zd_wangfenglin@163.com
Time: 2020/4/2 3:07 下午
Desc:
"""


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

    def source_all(self):
        """
        全部来源
        :return:
        """
        response = self.send_request()
        result = response['body']['data'][0]['result']['pageSum'][0]
        ret_pv = result[0]
        ret_uv = result[1]

        print(f"网站的PV是：{ret_pv}\n网站的UV是：{ret_uv}")

        return

    def trend(self, **kwargs):
        """
        趋势分析
        :return:
        """
        response = self.send_request(kwargs)
        result = response['body']['data'][0]['result']['items']

        ret_data = result[0]
        ret_pv = result[1]

        return ret_data, ret_pv

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


class SurvivalAnalysis:
    def __init__(self, data_frame):
        self.data_frame = data_frame

    def _callback(self, process, *args):
        method = getattr(self, process, None)
        if callable(method):
            method(*args)

    def all_source_plot(self, **kwargs):
        all_source = self.data_frame
        title = kwargs['title']
        path = kwargs['path']
        visitor = (all_source['visitor'] == "new")
        T = all_source["avg_visit_time"]
        kmf = lifelines.KaplanMeierFitter()
        fig, ax = plt.subplots()
        kmf.fit(T[visitor], label="New Visitor")
        kmf.plot(ax=ax)
        kmf.fit(T[~visitor], label="Old Visitor")
        kmf.plot(ax=ax)
        plt.ylim(0, 1)
        plt.title(title)
        plt.savefig(path)

    def coxph(self, **kwargs):
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
    my_id = "12391745"
    today = str(datetime.date.today()).replace("-", "")
    bdtj = BaiduTongJi()
    all_s = bdtj.all_source(
        site_id=my_id,
        start_date="20190101",
        end_date="20190501",
        metrics='pv_count, pv_ratio, visit_count, visitor_count, new_visitor_count, ip_count, bounce_ratio, avg_visit_time, avg_visit_pages',
        method="source/all/a",
        gran='day',
    )
    plot = SurvivalAnalysis(data_frame=all_s)
    plot.coxph(
        title="OncoView Cox proportional hazard",
        path="/Users/wangfenglin/stat/plot.png"
    )
