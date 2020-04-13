import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


class DataProcessor:
    def __init__(self, data_frame):
        self.df = data_frame

    def specific_dtype(self, **kwargs):
        for key in kwargs.keys():
            if kwargs[key] in ['float64', 'int64']:
                self.df[key] = pd.to_numeric(self.df[key], errors='coerce')
            elif kwargs[key] in ['category']:
                self.df[key] = self.df[key].astype("category")
        return self.df


if __name__ == "__main__":
    fp = "/Users/wangfenglin/test/clinical.project-TCGA-LUSC.2020-04-10/clinical.tsv"
    chandler = DataProcessor(data_frame=pd.read_csv(fp, delimiter='\t'))
    chandler.specific_dtype(
        days_to_last_follow_up="float64",
        race='category',
    )
    print(chandler.df.dtypes.race)
