import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import lifelines


class DataProcessor:
    def __init__(self, data_frame):
        self.df = data_frame

    def specific_dtype(self, **kwargs):
        """
        修改dataframe特定列的数据类型
        :param kwargs: columns=dtypes
        :return: self.df
        """
        for key in kwargs.keys():
            if kwargs[key] in ['float64', 'int64']:
                self.df[key] = pd.to_numeric(self.df[key], errors='coerce')
            elif kwargs[key] in ['category']:
                self.df[key] = self.df[key].astype("category")
            else:
                pass
        return self.df

    def generate_category_value(self, category, number_column):
        """
        根据category型变量生成number_column数据，example：根据gender，生成days_to_last_follow_up数据
        :param category:
        :param number_column:
        :return:
        """
        category_content = list(set(self.df[category].to_list()))
        result = {}
        for c in category_content:
            result[c] = self.df.loc[self.df[category] == c, number_column]
        return result

    def kaplan_meier_fit(self, data):
        kmf = lifelines.KaplanMeierFitter()
        kmf.fit(data)
        return kmf

    def callback(self, fun, *args):
        method = getattr(self, fun, None)
        if callable(method):
            method(args)


if __name__ == "__main__":
    fp = "/Users/wangfenglin/test/clinical.project-TCGA-LUSC.2020-04-10/clinical.tsv"
    chandler = DataProcessor(data_frame=pd.read_csv(fp, delimiter='\t'))
    chandler.specific_dtype(
        days_to_last_follow_up="float64",
        race='category',
    )
    data = chandler.generate_category_value('classification_of_tumor', 'days_to_last_follow_up')
    fig, ax = plt.subplots()
    kmf = lifelines.KaplanMeierFitter()
    for k, v in data.items():
        kmf.fit(durations=v.fillna(0), event_observed=[1 if j is False else 0 for j in v.isnull()])
        kmf.plot(ax=ax, label=k)
    plt.tight_layout()
    plt.savefig("/Users/wangfenglin/stat/kmp1.png")
