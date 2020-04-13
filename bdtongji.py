#!/usr/bin/env python3
# coding:utf-8
"""
Name: bdtongji.py
Author: murphy
Email: zd_wangfenglin@163.com
Time: 2020/4/2 3:07 下午
Desc: Download baidutongji record and make statistics
"""


import os
import requests
import json
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import lifelines
import seaborn as sns


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
        col = response['body']['data'][0]['result']['fields']
        col.remove('source_type_title')
        dates = np.array([i[0] for i in response['body']['data'][0]['result']['items'][0]])
        old_df = pd.DataFrame(response['body']['data'][0]['result']['items'][1], columns=col)
        old_df['visitor'] = 'old'
        old_df['date'] = dates

        kwargs['visitor'] = 'new'
        response = self.send_request(kwargs)
        col = response['body']['data'][0]['result']['fields']
        col.remove('source_type_title')
        dates = np.array([i[0] for i in response['body']['data'][0]['result']['items'][0]])
        new_df = pd.DataFrame(response['body']['data'][0]['result']['items'][1], columns=col)
        new_df['visitor'] = 'new'
        new_df['date'] = dates
        return pd.concat([new_df, old_df])

    def district_visit(self, **kwargs):
        """
        结果简单没有细节，不进一步挖掘
        :param kwargs:
        :return:
        """
        response = self.send_request(kwargs)
        return response

    def realtime_visitor(self, **kwargs):
        """
        没啥用，没写完
        :param kwargs:
        :return:
        """
        response = self.send_request(kwargs)
        col = response['body']['data'][0]['result']['fields']
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
        old = all_source[all_source['visitor'] == 'old']
        old_c = old.loc[:, 'avg_visit_time'].str.isdigit()
        old_cleaned = old[old_c].copy()
        new = all_source[all_source['visitor'] == 'new']
        new_c = new.loc[:, 'avg_visit_time'].str.isdigit()
        new_cleaned = new[new_c].copy()
        kmf = lifelines.KaplanMeierFitter()
        fig, ax = plt.subplots()
        kmf.fit(new_cleaned['avg_visit_time'], label="New Visitors")
        kmf.plot(ax=ax, show_censors=True)
        kmf.fit(old_cleaned['avg_visit_time'], label="Old Visitors")
        kmf.plot(ax=ax, show_censors=True)
        plt.ylim(0, 1)
        plt.title(title)
        plt.tight_layout()
        plt.savefig(path)
        plt.close('all')

    def coxph(self, **kwargs):
        """
        CoxPH plot using baidutongji all_source dataframe as input.
        :param kwargs:
        :return:
        """
        title = kwargs['title']
        path = kwargs['path']
        df_raw = self.data_frame
        df_raw = df_raw.applymap(lambda x: x if re.search("[-+]?[0-9]*\.?[0-9]+", str(x)) else np.nan)
        if kwargs['exclude']:
            df = df_raw.drop(kwargs['exclude'], axis=1)
        df = df.dropna(how='any')
        fit, ax = plt.subplots()
        cph = lifelines.CoxPHFitter()
        cph.fit(df, 'avg_visit_time')
        cph.plot(hazard_ratios=True, ax=ax)
        plt.title(title)
        plt.tight_layout()
        plt.savefig(path)
        plt.close('all')

    def cluster_map(self, **kwargs):
        row_df = self.data_frame
        row_df['avg_visit_time'] = row_df['avg_visit_time'].apply(
            lambda x: x if re.search("[-+]?[0-9]*\.?[0-9]+", str(x)) else np.nan)
        row_df = row_df.dropna(how='any')
        row_df = row_df.drop(kwargs['exclude'], axis=1)
        df = row_df.applymap(float)
        sns.clustermap(df.corr())
        plt.savefig(kwargs['path'])
        plt.tight_layout()
        plt.close('all')

    def heat_map(self, **kwargs):
        sns.set(style="white")
        row_df = self.data_frame
        row_df['avg_visit_time'] = row_df['avg_visit_time'].apply(
            lambda x: x if re.search("[-+]?[0-9]*\.?[0-9]+", str(x)) else np.nan)
        row_df = row_df.dropna(how='any')
        row_df = row_df.drop(kwargs['exclude'], axis=1)
        df = row_df.applymap(float)
        corr = df.corr()
        mask = np.triu(np.ones_like(corr, dtype=np.bool))
        cmap = sns.diverging_palette(220, 10, as_cmap=True)
        # Draw the heatmap with the mask and correct aspect ratio
        sns.heatmap(corr, mask=mask, cmap=cmap, vmax=.3, center=0,
                    square=True, linewidths=.5, cbar_kws={"shrink": .5})
        plt.savefig(kwargs['path'])
        plt.tight_layout()
        plt.close('all')


if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    all_source_df = pd.read_csv(os.path.join(current_dir, 'bdtj/all_source.csv'))
    sa = SurvivalAnalysis(data_frame=all_source_df)
    sa.all_source_plot(
        title="The difference of visiting time between New & Old visitors",
        path="/Users/wangfenglin/stat/kmp.png",
    )
    sa.coxph(
        title="cox",
        path="/Users/wangfenglin/stat/coxph.png",
        exclude=['visitor', 'date', 'trans_ratio', 'trans_ratio', 'bounce_ratio', 'date', 'trans_count', 'Unnamed: 0']
    )
    sa.cluster_map(
        title='Correlation of Oncoview factors',
        path="/Users/wangfenglin/stat/cluster.png",
        exclude=['date', 'trans_count', 'trans_ratio', 'visitor', 'Unnamed: 0'],
    )

    sa.heat_map(
        title='Correlation of Oncoview factors',
        path="/Users/wangfenglin/stat/corr.png",
        exclude=['date', 'trans_count', 'trans_ratio', 'visitor', 'Unnamed: 0'],
    )
